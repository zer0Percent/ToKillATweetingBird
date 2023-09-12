import re
import sys
import logging
import constants
import tweet_versions
from tweet_parser_exceptions import ExtractActivityException, ExtractLanguageException, ExtractPublishTimeException, ExtractRetweetException, ExtractRetweeterException, ExtractTweetContentException, ExtractUserException, ExtractVerifiedUserException, ProcessAElementException, ProcessEmojiException, ProcessMentionException, ProcessTextException, ExtractCitingToTweetException, ParseTweetException

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class TweetParser:
    
    def __init__(self, tweet_id: str, tweet_tree, xpaths: dict):
        self.tweet_id: str = tweet_id
        self.tweet_tree = tweet_tree
        self.tweet_nodes: dict = self._parse_html_nodes(xpaths)

    def _parse_html_nodes(self, xpaths: dict):
        content_dict = dict()

        for tweet_section, xpath in xpaths.items():
            content_dict[tweet_section] = self._get_tweet_node(xpath)

        return content_dict

    def _get_tweet_node(self, xpath: str):
        try:
            return self.tweet_tree.xpath(xpath)[0]
        except Exception as e:
            return None
        
    def parse_tweet(self):

        try:
            tweet: dict = {'tweet_id' : self.tweet_id}
            user_name: dict = self.extract_user_name(self.tweet_nodes[tweet_versions.USER_PROPERTY])
            is_verified: dict = self.extract_is_verified(self.tweet_nodes[tweet_versions.VERIFIED_PROPERTY])

            activity_section: dict = self.extract_activity_section(self.tweet_nodes[tweet_versions.ACTIVITY_SECTION_PROPERTY])

            is_retweet: dict = self.extract_is_retweet(self.tweet_nodes[tweet_versions.IS_RETWEET_PROPERTY])
            retweeter: dict = self.extract_retweeter(self.tweet_nodes[tweet_versions.RETWEETER_PROPERTY])

            tweet_content: dict = self.extract_tweet_content(self.tweet_nodes[tweet_versions.TWEET_TEXTUAL_CONTENT_PROPERTY])
            citing_to: dict = self.extract_citing_tweet(tweet_content[constants.CONTENT_PROPERTY])

            language: dict = self.extract_language(self.tweet_nodes[tweet_versions.LANGUAGE_PROPERTY])

            publish_time: dict = self.extract_publish_time(self.tweet_nodes[tweet_versions.PUBLISH_TIME_PROPERTY])
            
            tweet = tweet | user_name | is_verified | tweet_content | citing_to |  language | activity_section | is_retweet | retweeter | publish_time

            del self.tweet_id
            del self.tweet_tree
            del self.tweet_nodes

            return tweet
        
        except ParseTweetException as e:
            logging.error(e.message)
    
    def extract_user_name(self, section):
        try:
            return {constants.USERNAME_PROPERTY : section.text_content()}
        except Exception as e:
            raise ExtractUserException(f'Could not extract the user of the tweet with ID {self.tweet_id}. Reason {e} ')

    def extract_is_verified(self, section):

        try:
            is_verified: bool = False

            if section.tag == 'div':
                childs = section.getchildren()

                if len(childs) > 0:
                    child_span = childs[0]

                    if child_span.tag == 'span':
                        childs_svg = child_span.getchildren()

                        if len(childs_svg) > 0:
                            child_svg = childs_svg[0]
                            if child_svg.tag == 'svg' and child_svg.attrib['aria-label'] == 'Verified account':
                                is_verified = True
            
            return {constants.IS_VERIFIED_PROPERTY : is_verified}
        except Exception as e:
            raise ExtractVerifiedUserException(f'Could not extract the verified status of the user tweet with ID {self.tweet_id}. Reason {e}')

    def extract_activity_section(self, section) -> dict:

        retweets: int = 0
        likes: int = 0
        citations: int = 0
        bookmarks: int = 0

        try:
            section: str = section.text_content()
            section = section.replace(',', '')
            section = section.replace('.', '')
            lower_section = section.lower()

            has_retweets = self._has_retweets(lower_section)
            has_likes = self._has_likes(lower_section)
            has_citations = self._has_citations(lower_section)
            has_bookmarks = self._has_bookmarks(lower_section)

            if has_retweets:
                retweets = self._get_retweets(lower_section)

            if has_likes:
                likes = self._get_likes(lower_section)

            if has_citations:
                citations = self._get_citations(lower_section)
            
            if has_bookmarks:
                bookmarks = self._get_bookmarks(lower_section)

            return {constants.RETWEETS_PROPERTY : retweets,
                    constants.LIKES_PROPERTY : likes, 
                    constants.CITATIONS_PROPERTY : citations, 
                    constants.BOOKMARKS_PROPERTY : bookmarks}
        
        except Exception as e:
            raise ExtractActivityException(f'Could not extract the activity of the tweet with ID {self.tweet_id}. Reason {e}')

    def extract_is_retweet(self, section: str):
        try:
            return {constants.IS_RETWEET_PROPERTY : True if section != None else False}
        except Exception as e:
            raise ExtractRetweetException(f'Could not extract whether is retweet of the tweet with ID {self.tweet_id}. Reason {e}')
    
    def extract_retweeter(self, section):
        try:
            if section == None:
                return {constants.RETWEETER_PROPERTY : None}
            
            retweeter: str = section.attrib['href']
            return {constants.RETWEETER_PROPERTY : retweeter.replace('/', '@')}
        except Exception as e:
            raise ExtractRetweeterException(f'Could not extract the retweeter of the tweet with ID {self.tweet_id}. Reason {e}')
    
    def extract_language(self, section):
        try:
            return {constants.LANGUAGE_PROPERTY : section.attrib['lang']}
        except Exception as e:
            raise ExtractLanguageException(f'Could not extract the language of the tweet with ID {self.tweet_id}. Reason {e}')
        
    def extract_tweet_content(self, section):
        try:
            tweet_content_tree = section.getchildren()[0].getchildren()
            tweet_parsed = self.parse_tweet_content(tweet_content_tree)

            return {constants.CONTENT_PROPERTY : tweet_parsed}
        except Exception as e:
            raise ExtractTweetContentException(f'Could not extract the content of the tweet with ID {self.tweet_id}. Reason {e}')

    def extract_citing_tweet(self, tweet_content: str):

        try:
            if constants.CITE_WORDING not in tweet_content:
                return { constants.TWEET_ID_CITATION : None , constants.USERNAME_CITING_TO : None }
            
            cite_string: str = tweet_content.split(' ')[-1:][0] # The last element of the array
            citation_url: list = cite_string.split(constants.CITE_WORDING)

            username_citing_to: str = citation_url[0].replace('/', '@')
            tweet_id_citation = citation_url[-1:][0] # The last element of the array

            return {constants.TWEET_ID_CITATION : tweet_id_citation, constants.USERNAME_CITING_TO : username_citing_to}
        except Exception as e:
            raise ExtractCitingToTweetException(f'Could not extract the citing tweet of the tweet with ID {self.tweet_id}. Reason {e}')

    def extract_publish_time(self, section):
        try:
            return {constants.PUBLISH_TIME_PROPERTY : section.attrib['datetime']}
        except Exception as e:
            raise ExtractPublishTimeException(f'Could not extract the publish of the tweet with ID {self.tweet_id}. Reason {e}')

    def _has_retweets(self, section: str):
        return constants.RETWEET_WORDING in section or constants.REPOST_WORDING in section
    def _get_retweets(self, section: str):

        splitting_sharing = section.split(constants.RETWEET_WORDING)
        if len(splitting_sharing) == 1:
            splitting_sharing = section.split(constants.REPOST_WORDING)
                
        retweets_string: str = splitting_sharing[0].strip()
        numbers = re.findall(r'\d+', retweets_string)

        return int(numbers[-1:][0])
    
    def _has_likes(self, section: str):
        return constants.LIKE_WORDING in section
    def _get_likes(self, section: str):
        splitting_likes = section.split(constants.LIKE_WORDING)
        likes_string: str = splitting_likes[0].strip()
        numbers = re.findall(r'\d+', likes_string)

        return int(numbers[-1:][0])
    
    def _has_citations(self, section: str):
        return constants.CITATION_WORDING in section
    def _get_citations(self, section: str):
        splitting_citation = section.split(constants.CITATION_WORDING)
        citation_string: str = splitting_citation[0].strip()
        numbers = re.findall(r'\d+', citation_string)

        return int(numbers[-1:][0])
    
    def _has_bookmarks(self, section: str):
        return constants.BOOKMARK_WORDING in section
    def _get_bookmarks(self, section: str):
        splitting_bookmarks = section.split(constants.BOOKMARK_WORDING)
        bookmark_string: str = splitting_bookmarks[0].strip()
        numbers = re.findall(r'\d+', bookmark_string)

        return int(numbers[-1:][0])
    
    def parse_tweet_content(self, tweet_tree):

        try:

            tweet = list()
            for dom_element in tweet_tree:

                self._process_mention(dom_element, tweet)

                self._process_text(dom_element, tweet)

                self._process_emoji(dom_element, tweet)
                    
                self._process_a_element(dom_element, tweet)

            tweet_content = ''.join(tweet)
            del tweet

            return tweet_content
        except ProcessMentionException as e:
            raise e
        except ProcessTextException as e:
            raise e
        except ProcessEmojiException as e:
            raise
        except ProcessAElementException as e:
            raise e
    
    def _process_mention(self, dom_element, tweet: list):

        try:
            if dom_element.tag == 'div':
                child = dom_element.getchildren()[0]
                if child.tag == 'span':
                    child_span = child.getchildren()[0]

                    if child_span.tag == 'a':
                        tweet.append(
                            child_span.text_content()
                        )

        except Exception as e:
            raise ProcessMentionException(f'Error when processing the mentions for the tweet with ID {self.tweet_id}. Reason {e}')

    def _process_text(self, dom_element, tweet: list):

        try:
            if dom_element.tag == 'span':
                tweet.append(dom_element.text_content())
        except Exception as e:
            raise ProcessTextException(f'Error when processing the text for the tweet with ID {self.tweet_id}. Reason {e}')

    def _process_emoji(self, dom_element, tweet: list):

        try:
            if dom_element.tag == 'img':

                tweet.append(
                    dom_element.attrib['alt']
                )
        except Exception as e:
            raise ProcessEmojiException(f'Error when processing the emojis for the tweet with ID {self.tweet_id}. Reason {e}')

    def _process_a_element(self, dom_element, tweet: list):

        try:
            href = None
            if dom_element.tag == 'a':
                href = dom_element.attrib['href']
                if href == '/':
                    href = dom_element.text_content()

            if href is not None:
                tweet.append(href)
        except Exception as e:
            raise ProcessAElementException(f'Error when processing the links for the tweet with ID {self.tweet_id}. Reason {e}')

    def get_node(self, node_name: str):
        return self.tweet_nodes[node_name]
    

    