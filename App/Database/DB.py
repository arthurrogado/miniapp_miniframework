"""Camada base de acesso a dados com SQLite.

Fornece CRUD genérico, soft-delete automático e conversão para dict.
Tabelas com coluna `deleted_at` são filtradas automaticamente no select.

Padrão de uso:
    db = DB()
    db.insert('users', {'name': 'John', 'age': 25})
    users = db.select('users', ['*'])
    db.close()

    # Ou via context manager:
    with DB() as db:
        db.insert('users', {'name': 'John', 'age': 25})
"""

import sqlite3
from datetime import datetime as dt

from App.Config import DB_NAME, CLOUD_ID


class DB:
    def __init__(self, bot=None):
        self.bot = bot
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        except Exception:
            pass

    def dictify_query(self, cursor: sqlite3.Cursor, columns: list = None):
        """Converte resultado do cursor em lista de dicts."""
        try:
            if columns:
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(e)
            return []

    def dictify_result(self, cursor: sqlite3.Cursor, result: list):
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in result]

    def get_all_columns(self, table: str):
        self.cursor.execute(f"PRAGMA table_info({table})")
        return [column[1] for column in self.cursor.fetchall()]

    def has_deleted_at(self, table: str):
        """Verifica se a tabela possui coluna deleted_at (soft delete)."""
        self.cursor.execute(f"PRAGMA table_info({table})")
        columns = self.cursor.fetchall()
        return any(column[1] == 'deleted_at' for column in columns)

    # ─── Generic CRUD ────────────────────────────────────────────────

    def insert(self, table: str, data: dict):
        """Insere um registro. data deve ser um dict {coluna: valor}.

        Retorna lastrowid em caso de sucesso, False em caso de erro.
        Exemplo: insert('users', {'userid': 123, 'name': 'João'})
        """
        try:
            placeholders = ','.join(['?' for _ in data.values()])
            sql = f'INSERT INTO {table} ({",".join(data.keys())}) VALUES ({placeholders})'
            self.cursor.execute(sql, list(data.values()))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(e)
            return False

    def select(self, table: str, columns: list, where: str = None, params: list = None, final: str = None):
        """Seleciona registros com soft-delete automático.

        Args:
            table: Nome da tabela
            columns: Lista de colunas ou ['*']
            where: Cláusula WHERE com placeholders ? (ex: 'userid = ?')
            params: Valores para os placeholders (lista/tupla)
            final: SQL adicional (ORDER BY, LIMIT, etc.)

        Exemplos:
            select('users', ['*'])
            select('users', ['name'], 'userid = ?', [123])
            select('users', ['*'], 'age > ?', [18], 'ORDER BY name')
        """
        column_exists = self.has_deleted_at(table)

        if column_exists:
            sql = f"SELECT {','.join(columns)}"
            sql += f" FROM {table}"
            sql += f" WHERE {where} AND deleted_at IS NULL" if where else " WHERE deleted_at IS NULL"
            sql += f" {final}" if final else ""
        else:
            sql = f"SELECT {','.join(columns)}"
            sql += f" FROM {table}"
            sql += f" WHERE {where}" if where else ""
            sql += f" {final}" if final else ""

        self.cursor.execute(sql, params or [])
        rows = self.cursor.fetchall()
        return [dict(zip([key[0] for key in self.cursor.description], row)) for row in rows]

    def select_one(self, table: str, columns: list, where: str = None, params: list = None, final: str = None):
        """Retorna o primeiro resultado como dict ou None."""
        result = self.select(table, columns, where, params=params, final=final)
        return result[0] if result else None

    def update(self, table: str, data: dict, where: str = None, params: list = None) -> bool:
        """Atualiza registros. data deve ser um dict {coluna: novo_valor}.

        Args:
            table: Nome da tabela
            data: Dict com {coluna: valor}
            where: Cláusula WHERE com placeholders ? (ex: 'userid = ?')
            params: Valores extras para os placeholders do WHERE

        Exemplos:
            update('users', {'name': 'Novo'}, 'userid = ?', [123])
        """
        try:
            set_clause = ','.join([f"{col} = ?" for col in data.keys()])
            sql = f'UPDATE {table} SET {set_clause}'
            if where:
                sql += f' WHERE {where}'

            values = list(data.values())
            if params:
                values.extend(params)

            self.cursor.execute(sql, values)
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(e)
            return False

    def delete(self, table: str, where: str = None, params: list = None):
        """Deleta registros (hard delete).

        Exemplos:
            delete('users', 'userid = ?', [123])
        """
        self.cursor.execute(
            f'DELETE FROM {table}' + (f' WHERE {where}' if where else ''),
            params or []
        )
        self.conn.commit()
        return self.cursor.rowcount > 0