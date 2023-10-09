BASE_TITLE_TIME: float = 8
POOLING_TITLE_TIME = 0.01
BASE_USER_TIME: float = 4
WAIT_TIME_PAGE_DOWN: float = 30

ATTEMPTS_PER_CHUNK = 4

BODY_USER_XPATH = '/html/body/div[1]/div/div/div[2]/main/div'
WAIT_PRESENCE_TITLE_XPATH = '/html/head/title'
WAIT_FOR_USER_XPATH = '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[5]/div[1]/a/span[1]/span'
WAIT_FOR_USER_ID_XPATH = '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/aside/a'
EMPTY_USER_XPATH = '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[2]/div/div[1]/span'

EXPECTED_FORMAT_TITLE = '(@{username}) / X'
USER_DOES_NOT_EXIST = 'This account doesn’t exist'
USER_SUSPENDED = 'Account suspended'

USER_BASE_URL = 'https://twitter.com/{username}'
