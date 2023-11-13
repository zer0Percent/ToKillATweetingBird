from lxml import html
from bs4 import BeautifulSoup
from datetime import datetime
import user.user_versions as user_versions
from user.user_parser_exceptions import ConvertNumberToIntegerException, ExtractBiographyException, ExtractCategoryException, ExtractJoinDateException, ExtractLinkException, ExtractLocationException, NoXPathFoundException, ParseUserException, ExtractUserException, ProcessEmojiException, ProcessHashtagException, ProcessLinkException, ProcessMentionException, ProcessTextException

import logging
import sys
file_handler = logging.FileHandler(filename='alternative_url.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)

handlers = [file_handler, stdout_handler]
logging.basicConfig(
    level=logging.INFO, 
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)
logger=logging.getLogger('LOGGER_NAME')

class UserParser:
    
    def __init__(self, username: str, content: str, xpaths: dict):
        self.username: str = username
        self.content: str = content
        self.xpaths: dict = xpaths

        self.user_tree = html.fromstring(self.content)
    
    def _find_user_node(self, xpaths: list):
        for xpath in xpaths:
            user_node = self._get_user_node(xpath)
            if user_node is not None:
                return user_node

    def _get_user_node(self, xpath: str):
        try:
            return self.user_tree.xpath(xpath)[0]
        except Exception as e:
            return None
    
    def _sanity_check_of(self, section: str, content: str):

        if section not in user_versions.DATA_LOCATORS.keys():
            return False

        soup = BeautifulSoup(content, 'html.parser')
        element = soup.find(attrs={'data-testid' : user_versions.DATA_LOCATORS[section]})
        return element is not None
    
    def parse_user(self):

        try:

            user_name: dict = self.extract_user_name()
            displayed_name: dict = self.extract_displayed_name()
            account_status: dict = self.extract_account_status()

            biography: dict = self.extract_biography()

            profile_header: dict = self.extract_profile_header()

            followings: dict = self.extract_followings()
            followers: dict = self.extract_followers()
            posts_count: dict = self.extract_posts_count()

            user = user_name | displayed_name | account_status | biography | profile_header | followings | followers | posts_count

            del self.username
            del self.user_tree

            return user
        
        except ParseUserException as e:
            raise e

        except Exception as e:
            raise e
        
    def extract_user_name(self):

        property: str = user_versions.USERNAME_PROPERTY
        xpaths_user_section: list = self.xpaths[property]
        for xpath in xpaths_user_section:
            try:
                user_node = self._get_user_node(xpath)
                if user_node is not None:
                    username: str = user_node.text_content()
                    return {property : username}
            except Exception as e:
                logger.warning(f'Could not extract the {property} for the XPATH {xpath} of the user {self.username}. Reason {e}')
            
        really_has_content: bool = self._sanity_check_of(property, self.content)
        if really_has_content:
            raise NoXPathFoundException(f'The property {property} is on data test. The given XPATHS do not capture the information for the user {self.username}')
        
        raise ExtractUserException(f'No XPATH found for the property {property} of the user {self.username}.')
        
    def extract_displayed_name(self):

        property: str = user_versions.DISPLAYED_NAME_PROPERTY
        xpaths_displayed_name: list = self.xpaths[property]
        for xpath in xpaths_displayed_name:
            try:
                displayed_name_node = self._get_user_node(xpath)
                if displayed_name_node is not None:

                    name_elements: list = displayed_name_node.getchildren()
                    displayed_name_chunks: list = list()
                    for item in name_elements:
                        self._process_text(item, displayed_name_chunks)
                        self._process_link(item, displayed_name_chunks)
                        self._process_emoji(item, displayed_name_chunks)
                    displayed_name: str = ''.join(displayed_name_chunks)
                    return {property : displayed_name}
                
            except Exception as e:
                logger.warning(f'Could not extract the {property} for the XPATH {xpath} of the user {self.username}. Reason {e}')
            
        really_has_content: bool = self._sanity_check_of(property, self.content)
        if really_has_content:
            raise NoXPathFoundException(f'The property {property} is on data test. The given XPATHS do not capture the information for the user {self.username}')
        
        logging.warning(f'No XPATH found for the property {property} of the user {self.username}.')

    def extract_account_status(self):

        property: str = user_versions.ACCOUNT_STATUS_ITEMS
        xpath_account_status: list = self.xpaths[property]

        for xpath in xpath_account_status:
            try:
                account_status_node = self._get_user_node(xpath)
                if account_status_node is not None:

                    account_status: dict = {
                        user_versions.IS_VERIFIED_PROPERTY : False,
                        user_versions.VERIFIED_TYPE_PROPERTY : None,
                        user_versions.IS_PRIVATE_PROPERTY : False
                    }
                    span_status: list = account_status_node.getchildren()
                    for span in span_status:
                        self._set_account_status(span, account_status)
                    return account_status

            except Exception as e:
                logger.warning(f'Could not extract the {property} for the XPATH {xpath} of the user {self.username}. Reason {e}') 

        really_has_content: bool = self._sanity_check_of(property, self.content)
        if really_has_content:
            raise NoXPathFoundException(f'The property {property} is on data test. The given XPATHS do not capture the information for the user {self.username}')
        
        logging.warning(f'No XPATH found for the property {property} of the user {self.username}.')
    
    def _set_account_status(self, section, account_status: dict):
        try:

            verified_items: list = section.getchildren()
            if len(verified_items) > 0:
                
                svg_element = verified_items[0]

                type_account_status: str = svg_element.attrib['aria-label']
                if type_account_status == user_versions.VERIFIED_ACCOUNT_WORDING:
                    account_status[user_versions.IS_VERIFIED_PROPERTY] = True
                    account_status[user_versions.VERIFIED_TYPE_PROPERTY] = self._get_verified_type(svg_element)

                if type_account_status == user_versions.PRIVATE_ACCOUNT_WORDING:
                    account_status[user_versions.IS_PRIVATE_PROPERTY] = True

        except Exception as e:
            raise e
    def _get_verified_type(self, svg_section_verified):

        try:
            children_svg: list = svg_section_verified.getchildren()

            if len(children_svg) > 0:
                g_element = children_svg[0]
                
                children_g_element: list = g_element.getchildren()
                if len(children_g_element) == 3:
                    return user_versions.VERIFIED_GOLD
                path_element = children_g_element[0]

                is_present_fill_element: bool = self._has_fill_attribute(path_element)
                if is_present_fill_element:
                    return user_versions.VERIFIED_GOVERNMENT
                
                return user_versions.VERIFIED_BLUE
        except Exception as e:
            raise Exception(f'Could not determine the verified type for the user {self.username}. Reason {e}')
    def _has_fill_attribute(self, path_element):
        try:
            fill_attribute: str = path_element.attrib['fill']
            return fill_attribute is not None
        except Exception as e:
            return False
    def extract_biography(self):
            
        property: str = user_versions.BIOGRAPHY_PROPERTY
        xpaths_biography: list = self.xpaths[property]

        for xpath in xpaths_biography:
            try:
                biography_node = self._get_user_node(xpath)

                if biography_node is not None:
                    biography_content: str = None
                    biography_elements = biography_node.getchildren()
                    
                    biography_chunks: list = list()
                    for element in biography_elements:
                        self._process_text(element, biography_chunks)
                        self._process_link(element, biography_chunks)
                        self._process_emoji(element, biography_chunks)
                        self._process_mention(element, biography_chunks)
                        self._process_hashtag(element, biography_chunks)

                    biography_content: str = ''.join(biography_chunks)
                    del biography_chunks

                    return {property: biography_content}
            
            except ExtractBiographyException as e:
                logger.warning(f'Could not extract the {property} for the XPATH {xpath} of the user {self.username}. Reason {e}')
        
        really_has_content: bool = self._sanity_check_of(property, self.content)
        if really_has_content:
            raise NoXPathFoundException(f'The property {property} is on data test. The given XPATHS do not capture the information for the user {self.username}')
        
        logging.warning(f'No XPATH found for the property {property} of the user {self.username}.')

        return {property: None}

    def extract_profile_header(self):
        property: str = user_versions.PROFILE_HEADER_ITEMS
        xpath_header: list = self.xpaths[property]

        for xpath in xpath_header:
            try:
                header_node = self._get_user_node(xpath)

                if header_node is not None:
                    header_items: list = header_node.getchildren()
                    
                    header: dict = {
                        user_versions.CATEGORY_PROPERTY: user_versions.DEFAULT_CATEGORY,
                        user_versions.LOCATION_PROPERTY: None,
                        user_versions.LINK_PROPERTY: None,
                        user_versions.JOIN_DATE_PROPERTY: None
                    }
                    for item in header_items:
                        if user_versions.TODAY_BIRTHDAY_WORDING not in item.text_content():
                            self._extract_category(item, header)
                            self._extract_location(item, header)
                            self._extract_link(item, header)
                            self._extract_join_date(item, header)

                    return header
            except ExtractCategoryException as e:
                logger.warning(f'Could not extract the category for the XPATH {xpath} of the user {self.username}. Reason {e}')
            except ExtractLocationException as e:
                logger.warning(f'Could not extract the location for the XPATH {xpath} of the user {self.username}. Reason {e}')
            except ExtractLinkException as e:
                logger.warning(f'Could not extract the link for the XPATH {xpath} of the user {self.username}. Reason {e}')
            except ExtractJoinDateException as e:
                logger.warning(f'Could not extract the join date for the XPATH {xpath} of the user {self.username}. Reason {e}')
    
        really_has_content: bool = self._sanity_check_of(property, self.content)
        if really_has_content:
            raise NoXPathFoundException(f'The property {property} is on data test. The given XPATHS do not capture the information for the user {self.username}')
        
        logging.warning(f'No XPATH found for the property {property} of the user {self.username}.')

    def _extract_category(self, section, header: dict):
        try:

            if section.attrib['data-testid'] == 'UserProfessionalCategory':
                children_category: list = section.getchildren()
                span_textual_category = children_category[1]
                header[user_versions.CATEGORY_PROPERTY] = span_textual_category.text_content()

        except Exception as e:
            raise ExtractCategoryException(f'Could not extract the category of {self.username}. Reason {e}')
        
    def _extract_location(self, section, header: dict):
        try:
            if section.attrib['data-testid'] == 'UserLocation':
                children_location: list = section.getchildren()

                span_location_content = children_location[1] # The second element since the first one is a SVG
                children_span_location: list = span_location_content.getchildren()

                location_chunks: list = list()
                for location_item in children_span_location:
                    if location_item.tag == 'span':
                        location_chunks.append(location_item.text_content())
                    if location_item.tag == 'img':
                        location_chunks.append(location_item.attrib['alt'])

                header[user_versions.LOCATION_PROPERTY] = ''.join(location_chunks)

        except Exception as e:
            raise ExtractLocationException(f'Could not extract the location of {self.username}. Reason {e}')
    

    def _extract_link(self, section, header: dict):
        try:
            if section.attrib['data-testid'] == 'UserUrl':
                children_user_url: list = section.getchildren()
                span_user_url = children_user_url[1]
                header[user_versions.LINK_PROPERTY] = span_user_url.text_content()

        except Exception as e:
            raise ExtractLinkException(f'Could not extract the website of {self.username}. Reason {e}')

    def _extract_join_date(self, section, header: dict):
        try:
            if section.attrib['data-testid'] == 'UserJoinDate':
                raw_join_date: str = section.text_content()
                raw_join_date = raw_join_date.split('Joined ')[1]

                header[user_versions.JOIN_DATE_PROPERTY] = f'{self._convert_date_with_month(raw_join_date)}-01'

        except Exception as e:
            raise ExtractJoinDateException(f'Could not extract the join date of {self.username}. Reason {e}')
        
    def _convert_date_with_month(self, date: str):
        date_object = datetime.strptime(date, '%B %Y')
        return date_object.strftime('%Y-%m')
    
    def extract_followings(self):
        
        property: str = user_versions.FOLLOWINGS_PROPERTY
        xpaths_following: list = self.xpaths[property]

        for xpath in xpaths_following:
                
                try:
                    following_node = self._get_user_node(xpath)

                    if following_node is not None:

                        followings_raw: str = following_node.text_content()
                        return {property: self._convert_number_to_integer(followings_raw)}
                    
                except ConvertNumberToIntegerException as e:
                    raise e
                except Exception as e:
                    logger.warning(f'Could not extract the {property} for the XPATH {xpath} of the user {self.username}. Reason {e}')

        really_has_content: bool = self._sanity_check_of(property, self.content)
        if really_has_content:
            raise NoXPathFoundException(f'The property {property} is on data test. The given XPATHS do not capture the information for the user {self.username}')
        
        logging.warning(f'No XPATH found for the property {property} of the user {self.username}.')
    
    def extract_followers(self):
        
        property: str =  user_versions.FOLLOWERS_PROPERTY
        xpaths_followers: list = self.xpaths[property]
        for xpath in xpaths_followers:
            try:
                node_followers = self._get_user_node(xpath)
                if node_followers is not None:
                    
                    followers_raw: str = node_followers.text_content()
                    return {property: self._convert_number_to_integer(followers_raw)}
                
            except ConvertNumberToIntegerException as e:
                raise e
            except Exception as e:
                logger.warning(f'Could not extract the {property} for the XPATH {xpath} of the user {self.username}. Reason {e}')

        really_has_content: bool = self._sanity_check_of(property, self.content)
        if really_has_content:
            raise NoXPathFoundException(f'The property {property} is on data test. The given XPATHS do not capture the information for the user {self.username}')
        
        logging.warning(f'No XPATH found for the property {property} of the user {self.username}.')

    def extract_posts_count(self):
        
        property: str = user_versions.POSTS_COUNT_PROPERTY
        xpaths_post_counts: list = self.xpaths[property]

        for xpath in xpaths_post_counts:
            try:
                node_post_counts = self._get_user_node(xpath)

                if node_post_counts is not None:

                    post_counts_raw: str = node_post_counts.text_content()
                    post_counts_raw_split = post_counts_raw.split(' posts')
                    if len(post_counts_raw) == 2:
                        post_counts_raw = post_counts_raw_split[0]
                        return {property: self._convert_number_to_integer(post_counts_raw)}
                    
                    post_counts_raw = post_counts_raw.split(' post')[0]
                    return {property: self._convert_number_to_integer(post_counts_raw)}
                
            except ConvertNumberToIntegerException as e:
                raise e
            except Exception as e:
                logger.warning(f'Could not extract the number of posts of the user {self.username}. Reason {e}')

        really_has_content: bool = self._sanity_check_of(property, self.content)
        if really_has_content:
            raise NoXPathFoundException(f'The property {property} is on data test. The given XPATHS do not capture the information for the user {self.username}')
        
        logging.warning(f'No XPATH found for the property {property} of the user {self.username}.')

    def _convert_number_to_integer(self, raw_number: str):
        try:
            multipliers = {'K': 10**3, 'M': 10**6, 'B': 10**9, 'T': 10**12}

            if raw_number[-1] in multipliers:
                return int(float(raw_number[:-1]) * multipliers[raw_number[-1]])
            else:
                raw_number: str = raw_number.replace(',', '')
                raw_number: str = raw_number.replace('.', '')
                return int(raw_number)
        except Exception as e:
            raise ConvertNumberToIntegerException(f'Could not convert the raw number {raw_number} to integer. Reason {e}')



    def _process_text(self, dom_element, biography_chunks: list):
        try:
            if dom_element.tag == 'span':
                children_span_count: int = len(dom_element.getchildren())
                if children_span_count == 0:
                    biography_chunks.append(dom_element.text_content())
        except Exception as e:
            raise ProcessTextException(f'Could not process the text for the user biography {self.username}. Reason {e}')
        
    def _process_link(self, dom_element, biography_chunks: list):
        try:
            if dom_element.tag == 'a':
                biography_chunks.append(f'{dom_element.text_content()}')
        except Exception as e:
            raise ProcessLinkException(f'Could not process the link for the user biography {self.username}. Reason {e}')
        
    def _process_emoji(self, dom_element, biography_chunks: list):
        try:
            if dom_element.tag == 'img':
                biography_chunks.append(dom_element.attrib['alt'])
        except Exception as e:
            raise ProcessEmojiException(f'Could not process the emoji for the user biography {self.username}. Reason {e}')
        
    def _process_mention(self, dom_element, biography_chunks: list):
        try:
            if dom_element.tag == 'div':
                children_div_mention: list = dom_element.getchildren()

                span_mention_element = children_div_mention[0]
                if span_mention_element.tag == 'span':
                    span_children: list = span_mention_element.getchildren()
                    a_element = span_children[0]
                    if a_element.tag == 'a':
                        biography_chunks.append(a_element.text_content())
        except Exception as e:
            raise ProcessMentionException(f'Could not process the mention for the user biography {self.username}. Reason {e}')
    
    def _process_hashtag(self, dom_element, biography_chunks: list):
        try:
            if dom_element.tag == 'span':
                children_span_hashtag: list = dom_element.getchildren()

                if len(children_span_hashtag) != 0:
                    a_element = children_span_hashtag[0]
                    if a_element.tag == 'a':
                        biography_chunks.append(a_element.text_content())
        except Exception as e:
            raise ProcessHashtagException(f'Could not process the hashtag for the user biography {self.username}. Reason {e}')