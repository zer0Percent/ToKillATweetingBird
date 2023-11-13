USERNAME_PROPERTY = 'username'
DISPLAYED_NAME_PROPERTY = 'displayed_name'
IS_VERIFIED_PROPERTY = 'is_verified'
IS_PRIVATE_PROPERTY = 'is_private'
VERIFIED_TYPE_PROPERTY = 'verified_type'


BIOGRAPHY_PROPERTY = 'biography'

PROFILE_HEADER_ITEMS = 'profile_headers'
ACCOUNT_STATUS_ITEMS = 'account_status'
CATEGORY_PROPERTY = 'category'
LOCATION_PROPERTY = 'location'
LINK_PROPERTY = 'link'
JOIN_DATE_PROPERTY = 'join_date'

FOLLOWINGS_PROPERTY = 'followings'
FOLLOWERS_PROPERTY = 'followers'
POSTS_COUNT_PROPERTY = 'posts_count'

DEFAULT_CATEGORY = 'Standard User'
NON_VERIFIED = 'not_verified'
VERIFIED_BLUE = 'blue'
VERIFIED_GOLD = 'gold'
VERIFIED_GOVERNMENT = 'government'


VERIFIED_ACCOUNT_WORDING = 'Verified account'
PRIVATE_ACCOUNT_WORDING = 'Protected account'
TODAY_BIRTHDAY_WORDING = 'Today is their birthday!'

PRIVATE_ACCOUNT_XPATH_EXCEPTIONS = 'private_exceptions'
USERNAME_EXCEPTIONS = 'username_exceptions'
FOLLOWING_EXCEPTIONS = 'following_exceptions'
FOLLOWER_EXCEPTIONS = 'follower_exceptions'
HEADER_ITEM_XPATHS_ALTERNATIVES = 'header_alternative'
XPATHS = 'xpaths'
USER_XPATH_VERSIONS: dict = {

    'v1' : {
        USERNAME_PROPERTY : ['/html/body/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div/div/div/span',
                            '/html/body/div/div/div[1]/div/div[1]/div[1]/div/div/div/div/div/div[2]/div/h2/div/div/div/div/span[1]/span/span'],

        DISPLAYED_NAME_PROPERTY : ['/html/body/div/div/div[1]/div/div[1]/div[1]/div/div/div/div/div/div[2]/div/h2/div/div/div/div/span[1]/span'],

        ACCOUNT_STATUS_ITEMS : ['/html/body/div/div/div[1]/div/div[1]/div[1]/div/div/div/div/div/div[2]/div/h2/div/div/div/div/span[2]'],

        BIOGRAPHY_PROPERTY : ['/html/body/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[3]/div/div'],
        PROFILE_HEADER_ITEMS : ['/html/body/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div', '/html/body/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[3]/div'],

        FOLLOWINGS_PROPERTY : ['/html/body/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[5]/div[1]/a/span[1]/span',
                               '/html/body/div/div/div[1]/div/div[3]/div/div/div[1]/div[2]/div[4]/div[1]/a/span[1]/span',
                               '/html/body/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[1]/a/span[1]/span', 
                               '/html/body/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[5]/div[1]/div/span[1]/span', 
                               '/html/body/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[1]/div/span[1]/span'],

        FOLLOWERS_PROPERTY : ['/html/body/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[5]/div[2]/a/span[1]/span', 
                              '/html/body/div/div/div[1]/div/div[3]/div/div/div[1]/div[2]/div[4]/div[2]/a/span[1]/span',
                              '/html/body/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/a/span[1]/span',
                              '/html/body/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[5]/div[2]/div/span[1]/span',
                              '/html/body/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/div/span[1]/span'],

        POSTS_COUNT_PROPERTY : ['/html/body/div/div/div[1]/div/div[1]/div[1]/div/div/div/div/div/div[2]/div/div']
    }
}

USERNAME_DATATEST = 'UserName'
USER_DESCRIPTION_DATATEST = 'UserDescription'

CATEGORY_DATATEST = 'UserProfessionalCategory'
LOCATION_DATATEST = 'UserLocation'
LINK_DATATEST = 'UserUrl'
JOIN_DATE_DATATEST = 'UserJoinDate'

DATA_LOCATORS = {
        USERNAME_PROPERTY : USERNAME_DATATEST,
        BIOGRAPHY_PROPERTY : USER_DESCRIPTION_DATATEST,
        CATEGORY_PROPERTY : CATEGORY_DATATEST,
        LOCATION_PROPERTY : LOCATION_DATATEST,
        LINK_PROPERTY : LINK_DATATEST,
        JOIN_DATE_PROPERTY : JOIN_DATE_DATATEST
}