import re
import sys
import logging
import tweet.constants as constants
import tweet.tweet_versions as tweet_versions
from tweet.tweet_parser_exceptions import ExtractActivityException, ExtractLanguageException, ExtractPublishTimeException, ExtractRetweetException, ExtractRetweeterException, ExtractTweetContentException, ExtractTweetIdRetweeted, ExtractUserException, ExtractVerifiedUserException, ProcessAElementException, ProcessEmojiException, ProcessImgElementException, ProcessMentionException, ProcessTextException, ExtractCitingToTweetException, ParseTweetException

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
            retweeter: dict = self.extract_retweeter(self.tweet_nodes[tweet_versions.IS_RETWEET_PROPERTY])
            tweet_id_retweeted : dict = self.extract_tweet_id_retweeted(
                    is_retweet[constants.IS_RETWEET_PROPERTY],
                    self.tweet_nodes[tweet_versions.TWEET_ID_RETWEETED_PROPERTY]
            )

            tweet_content: dict = self.extract_tweet_content(self.tweet_nodes[tweet_versions.TWEET_DIV_PROPERTY])
            citing_to: dict = self.extract_citing_tweet(tweet_content[constants.CONTENT_PROPERTY])

            language: dict = self.extract_language(self.tweet_nodes[tweet_versions.LANGUAGE_PROPERTY])

            publish_time: dict = self.extract_publish_time(self.tweet_nodes[tweet_versions.PUBLISH_TIME_PROPERTY])
            
            tweet = tweet | user_name | is_verified | tweet_content | citing_to |  language | activity_section | is_retweet | retweeter | tweet_id_retweeted | publish_time

            del self.tweet_id
            del self.tweet_tree
            del self.tweet_nodes

            return tweet
        
        except ParseTweetException as e:
            raise e
    
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
            
            a_element_retweeter = section.getchildren()[0]
            retweeter: str = a_element_retweeter.attrib['href']
            return {constants.RETWEETER_PROPERTY : retweeter.replace('/', '@')}
        except Exception as e:
            raise ExtractRetweeterException(f'Could not extract the retweeter of the tweet with ID {self.tweet_id}. Reason {e}')
    
    def extract_tweet_id_retweeted(self, is_retweet: bool, section):

        try:
            if not is_retweet:
                return {constants.TWEET_ID_RETWEETED_PROPERTY : None}
            
            a_element_tweet_id = section
            href_tweet_status: str = a_element_tweet_id.attrib['href']
            tweet_id_retweeted: str = href_tweet_status.split('/')[-1:][0]

            return {constants.TWEET_ID_RETWEETED_PROPERTY : tweet_id_retweeted}

        except Exception as e:
            raise ExtractTweetIdRetweeted(f'Could not extract the ID of the tweet that is being retweeted of the tweet {self.tweet_id}. Reason {e}')

    def extract_language(self, section):
        try:
            language_section = section.get('lang') if section is not None else constants.NO_LANGUAGE
            return {constants.LANGUAGE_PROPERTY : language_section}
        except Exception as e:
            raise ExtractLanguageException(f'Could not extract the language of the tweet with ID {self.tweet_id}. Reason {e}')
        
    def extract_tweet_content(self, section):
        try:

            tweet_content_tree = self._get_tweet_content_tree(section)
            tweet_parsed = self.parse_tweet_content(tweet_content_tree)

            return {constants.CONTENT_PROPERTY : tweet_parsed}
        except Exception as e:
            raise ExtractTweetContentException(f'Could not extract the content of the tweet with ID {self.tweet_id}. Reason {e}')
        
    def _get_tweet_content_tree(self, section):

        tweet_content_tree: list = list()

        tweet_content_nodes = section.getchildren()
        child_with_potential_textual_content = tweet_content_nodes[0].getchildren()[0].getchildren()
        if len(child_with_potential_textual_content) > 0:
            tweet_content_tree = tweet_content_tree + child_with_potential_textual_content[0].getchildren()
        
        multimedia_node = tweet_content_nodes[1]
        multimedia_nodes = self._get_multimedia_nodes(multimedia_node)

        return tweet_content_tree + multimedia_nodes
    def _get_multimedia_nodes(self, multimedia_node):

        multimedia_nodes: list = list()
        video_elements = multimedia_node.findall('.//video')
        if len(video_elements) > 0:
            multimedia_nodes = multimedia_nodes +  video_elements

        a_elements = multimedia_node.findall('.//a')
        if len(a_elements) > 0:
            for element in a_elements:
                if '/photo/' not in element.attrib['href']:
                    multimedia_nodes.append(element)

        img_elements = multimedia_node.findall('.//img')
        if len(img_elements) > 0:
            multimedia_nodes = multimedia_nodes + img_elements

        return multimedia_nodes

    def extract_citing_tweet(self, tweet_content: str):

        try:
            citations: list = self._get_citation_urls(tweet_content)

            has_citations: bool = len(citations) > 0
            if not has_citations:
                return { constants.TWEET_ID_CITATION : None , constants.USERNAME_CITING_TO : None }

            tweet_ids, usernames = self._parse_citations(citations)

            return {constants.TWEET_ID_CITATION : ", ".join(tweet_ids),
                   constants.USERNAME_CITING_TO : ", ".join(usernames)}
        
        except Exception as e:
            raise ExtractCitingToTweetException(f'Could not extract the citing tweet of the tweet with ID {self.tweet_id}. Reason {e}')
    def _get_citation_urls(self, tweet_content: str):
        split_tweet: list = tweet_content.split(' ')

        citations: list = list()
        for component in split_tweet:
            if constants.CITE_WORDING in component and len(component.split('/')) == 4:
                citations.append(component)
        return citations
    
    def _parse_citations(self, citations: list):
        usernames: list = list()
        tweet_id_citations = list()
        for cite in citations:
            split_citation: list = cite.split('/status/')

            username: str = split_citation[0].replace('/', '@')
            usernames.append(username)

            tweet_id: str = split_citation[1].split('/')[0]
            tweet_id_citations.append(tweet_id)

        return tweet_id_citations, usernames
    
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

                self._process_multimedia(dom_element, tweet)
                    
                self._process_a_element(dom_element, tweet)

            tweet_content = ''.join(tweet)
            del tweet

            return tweet_content
        except ProcessMentionException as e:
            raise e
        except ProcessTextException as e:
            raise e
        except ProcessEmojiException as e:
            raise e
        except ProcessAElementException as e:
            raise e
        except ProcessImgElementException as e:
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

    def _process_multimedia(self, dom_element, tweet: list):

        try:
            if dom_element.tag == 'img':
                
                element = f' {dom_element.attrib["src"]}'
                if dom_element.attrib['alt'] != 'Image':
                    element = dom_element.attrib['alt']
                    element = f' {element}'
                tweet.append(element)

            if dom_element.tag == 'video':
                shadow_content: list = dom_element.getchildren()
                if len(shadow_content) > 0:
                    video_url: str = shadow_content[0].attrib['src'].replace('blob:', '')
                    element = f' {video_url}'

                    tweet.append(element)
                
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
                href = f' {href}'
                tweet.append(href)
        except Exception as e:
            raise ProcessAElementException(f'Error when processing the links for the tweet with ID {self.tweet_id}. Reason {e}')

    def _process_img_element(self, dom_element, tweet: list):
        try:
            img = None
            if dom_element.tag == 'img':
                img = dom_element.attrib['src']

            if img is not None:
                tweet.append(img)
        except Exception as e:
            raise ProcessImgElementException(f'Error when processing the image for the tweet with ID {self.tweet_id}. Reason {e}')

    def get_node(self, node_name: str):
        return self.tweet_nodes[node_name]
    

    