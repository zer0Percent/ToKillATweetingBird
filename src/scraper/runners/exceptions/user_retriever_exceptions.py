class WaitForUserNameException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class GetUserInBrowserException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class NoExistsUserException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class PageIsDownException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)