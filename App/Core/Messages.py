class Messages:
    """Catálogo centralizado de mensagens padronizadas do bot.
    
    Evita strings hardcoded espalhadas pelo código.
    Estender esta classe para adicionar mensagens específicas do projeto.
    """

    GENERIC_ERROR = "Oops! An unexpected error occurred. Please contact support."
    OP_CANCELLED = "⚠️ Operation cancelled"
    ADMIN_ONLY = "⛔ Only administrators can perform this action."

    @staticmethod
    def success(text: str) -> str:
        return f"✅ {text}"

    @staticmethod
    def warning(text: str) -> str:
        return f"⚠️ {text}"

    @staticmethod
    def error(text: str) -> str:
        return f"❌ {text}"
