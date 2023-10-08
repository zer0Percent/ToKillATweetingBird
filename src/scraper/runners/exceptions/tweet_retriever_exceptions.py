class WaitForTitleException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class WaitForTweetDivException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class GetTweetInBrowserException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class EmptyTweetException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class PageIsDownException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)