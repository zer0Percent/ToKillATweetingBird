class ParseTweetException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractUserException(ParseTweetException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractVerifiedUserException(ParseTweetException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractActivityException(ParseTweetException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractRetweetException(ParseTweetException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractRetweeterException(ParseTweetException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractLanguageException(ParseTweetException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractTweetContentException(ParseTweetException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractCitingToTweetException(ParseTweetException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractPublishTimeException(ParseTweetException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)


class ProcessMentionException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ProcessTextException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ProcessEmojiException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ProcessAElementException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ProcessImgElementException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class TweetVersioningException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class PersistingTweetException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class UpdateParsedStatusException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class GetRawTweetsException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)