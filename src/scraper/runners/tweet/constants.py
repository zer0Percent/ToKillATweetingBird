BASE_TITLE_TIME: float = 6
BASE_TWEET_TIME: float = 2
WAIT_TIME_PAGE_DOWN: float = 30

ATTEMPTS_PER_CHUNK: int = 4
TWEET_ATTEMPT_THRESHOLD: int = 3

EXPECTED_TITLE_OF_TWEET_WITH_CONTENT = 'on X:'
DELETED_TWEET_OR_WITH_CONTENT_BUT_ERROR = 'Something went wrong. Try reloading.'
PAGE_DOES_NOT_EXISTS = 'Hmm...this page doesn’t exist. Try searching for something else.'
PAGE_DOES_NOT_EXISTS_SPACE = 'Hmm... this page doesn’t exist. Try searching for something else.'
PAGE_IS_DOWN = 'This page is down'

BODY_TWEET_XPATH = '/html/body/div[1]'
WAIT_PRESENCE_TITLE_XPATH = '/html/head/title'
EMPTY_TWEET_XPATH = '/html/body/div/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div/span/span'
PAGE_IS_DOWN_XPATH = '/html/body/div[2]/div[1]/h1'
WAIT_FOR_TWEET_XPATH = '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[1]/div'
WAIT_FOR_TWEET_NO_CONTENT_XPATH = '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[2]'

TWEET_BASE_URL = 'https://twitter.com/anyuser/status/'