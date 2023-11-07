USER_PROPERTY = 'user'
VERIFIED_PROPERTY = 'verified'
TWEET_DIV_PROPERTY = 'tweet_div'
LANGUAGE_PROPERTY = 'language'
TWEET_TEXTUAL_CONTENT_PROPERTY = 'tweet_textual_content'
ACTIVITY_SECTION_PROPERTY = 'activity_section'
PUBLISH_TIME_PROPERTY = 'publish_time'
IS_RETWEET_PROPERTY = 'is_retweet'
RETWEETER_PROPERTY = 'retweeter'
TWEET_ID_RETWEETED_PROPERTY = 'tweet_id_retweeted'

TWEET_XPATH_VERSIONS: dict = {

    'v1' : {
        USER_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div/div/section/div/div/div/div/div/div/div/article/div/div/div[2]/div[2]/div/div/div[1]/div/div/div[2]/div/div/a/div/span',
        VERIFIED_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div/div/section/div/div/div/div/div[1]/div/div/article/div/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/a/div/div[2]',

        TWEET_DIV_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div/div/section/div/div/div/div/div[1]/div/div/article/div/div/div[3]',
        
        LANGUAGE_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div/div/div[1]/div/div/article/div/div/div[3]/div[1]/div/div[1]',
        TWEET_TEXTUAL_CONTENT_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div/div/section/div/div/div/div/div[1]/div/div/article/div/div/div[3]/div[1]/div',

        ACTIVITY_SECTION_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div/div/section/div/div/div/div/div[1]/div/div/article/div/div/div[3]/div[5]',

        PUBLISH_TIME_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div/div/section/div/div/div/div/div[1]/div/div/article/div/div/div[3]/div[4]/div/div[1]/div/div/a/time',

        IS_RETWEET_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div/div/section/div/div/div/div/div[1]/div/div/article/div/div/div[1]/div/div/div/div/div[2]/div/div/div',
        RETWEETER_PROPERTY : '//*[@class="css-4rbku5 css-18t94o4 css-901oao r-14j79pv r-1loqt21 r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-qvutc0"]',
        TWEET_ID_RETWEETED_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div/div/section/div/div/div/div/div[1]/div/div/article/div/div/div[3]/div[4]/div/div[1]/div/div/a'
    },

    'v2' : {
        USER_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[2]/div[2]/div/div/div[1]/div/div/div[2]/div/div/a/div/span',
        VERIFIED_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/a/div/div[2]',
        
        TWEET_DIV_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]',
        
        LANGUAGE_PROPERTY: '/html/body/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[1]/div/div',
        TWEET_TEXTUAL_CONTENT_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[1]/div',

        ACTIVITY_SECTION_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[5]',

        PUBLISH_TIME_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[4]/div/div[1]/div/div/a/time',

        IS_RETWEET_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[1]/div/div/div/div/div[2]/div/div/div',
        RETWEETER_PROPERTY : '//*[@class="css-4rbku5 css-18t94o4 css-901oao r-1bwzh9t r-1loqt21 r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-qvutc0"]',
        TWEET_ID_RETWEETED_PROPERTY : '/html/body/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[4]/div/div[1]/div/div/a'
    }
}