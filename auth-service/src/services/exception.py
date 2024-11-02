class AuthException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AccessException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class RoleException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class SocialException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
