"""DAO para tabela de usuários.

Estender com métodos específicos do domínio.
O padrão é: uma instância por operação (short-lived).

Exemplo:
    user = User().get_user(12345)
    User().add_user(12345, 'João', '2000-01-01')
"""

from App.Database.DB import DB


class User(DB):
    def __init__(self, bot=None):
        super().__init__(bot)

    def add_user(self, userid, name, birthday=None):
        data = {'userid': userid, 'name': name}
        if birthday:
            data['birthday'] = birthday
        return self.insert('users', data)

    def get_user(self, userid):
        return self.select_one('users', ['*'], 'userid = ?', params=[userid])

    def get_all_users(self):
        return self.select('users', ['*'])

    def update_user(self, userid, **fields):
        """Atualiza campos do usuário. Ex: update_user(123, name='Novo', birthday='2000-01-01')"""
        if not fields:
            return False
        return self.update('users', fields, 'userid = ?', params=[userid])

    def delete_user(self, userid):
        return self.delete('users', 'userid = ?', params=[userid])

    def is_admin(self, userid):
        from App.Config import ADMINS_IDS
        return userid in ADMINS_IDS

    def is_not_admin(self, userid):
        return not self.is_admin(userid)