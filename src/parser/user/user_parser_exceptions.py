class GetRawUsersException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)


class ParseUserException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractUserException(ParseUserException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractAccountStatusException(ParseUserException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractBiographyException(ParseUserException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractHeaderProfileException(ParseUserException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractCategoryException(ParseUserException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractLocationException(ParseUserException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractLinkException(ParseUserException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractJoinDateException(ParseUserException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractFollowingsFollowersException(ParseUserException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ExtractPostsCountException(ParseUserException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ConvertNumberToIntegerException(ParseUserException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ProcessTextException(ExtractBiographyException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ProcessLinkException(ExtractBiographyException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ProcessEmojiException(ExtractBiographyException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ProcessMentionException(ExtractBiographyException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class ProcessHashtagException(ExtractBiographyException):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)


class PersistingUserException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)