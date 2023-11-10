import user.user_versions as user_versions
from datetime import datetime
from user.user_parser_exceptions import ConvertNumberToIntegerException, ExtractAccountStatusException, ExtractBiographyException, ExtractCategoryException, ExtractFollowingsFollowersException, ExtractHeaderProfileException, ExtractJoinDateException, ExtractLinkException, ExtractLocationException, ExtractPostsCountException, ParseUserException, ExtractUserException, ProcessEmojiException, ProcessHashtagException, ProcessLinkException, ProcessMentionException, ProcessTextException


class UserParser:
    
    def __init__(self, username: str, user_tree, xpaths: dict):
        self.username: str = username
        self.user_tree = user_tree
        self.user_nodes: dict = self._parse_html_nodes(xpaths)

    def _parse_html_nodes(self, xpaths: dict):
        content_dict = dict()

        for user_section, xpath in xpaths[user_versions.XPATHS].items():
            content_dict[user_section] = self._get_user_node(xpath)

        if content_dict[user_versions.BIOGRAPHY_PROPERTY] is None:
            content_dict[user_versions.PROFILE_HEADER_ITEMS] = self._get_user_node(xpaths[user_versions.HEADER_ITEM_XPATHS_ALTERNATIVES][user_versions.PROFILE_HEADER_ITEMS])

        if content_dict[user_versions.FOLLOWINGS_PROPERTY] is None:

            for following_exception_xpath in xpaths[user_versions.FOLLOWING_EXCEPTIONS][user_versions.FOLLOWINGS_PROPERTY]:
                node_following = self._get_user_node(following_exception_xpath)
                if node_following is not None:
                    content_dict[user_versions.FOLLOWINGS_PROPERTY] = node_following
                    break

        if content_dict[user_versions.FOLLOWERS_PROPERTY] is None:

            for follower_exception_xpath in xpaths[user_versions.FOLLOWER_EXCEPTIONS][user_versions.FOLLOWERS_PROPERTY]:
                node_follower = self._get_user_node(follower_exception_xpath)
                if node_follower is not None:
                    content_dict[user_versions.FOLLOWERS_PROPERTY] = node_follower
                    break

        return content_dict
    
    def _get_user_node(self, xpath: str):
        try:
            return self.user_tree.xpath(xpath)[0]
        except Exception as e:
            return None
    
    def parse_user(self):

        try:

            user_name: dict = self.extract_user_name(self.user_nodes[user_versions.USERNAME_PROPERTY])
            displayed_name: dict = self.extract_displayed_name(self.user_nodes[user_versions.DISPLAYED_NAME_PROPERTY])
            account_status: dict = self.extract_account_status(self.user_nodes[user_versions.ACCOUNT_STATUS_ITEMS])

            biography: dict = self.extract_biography(self.user_nodes[user_versions.BIOGRAPHY_PROPERTY])

            profile_header: dict = self.extract_profile_header(self.user_nodes[user_versions.PROFILE_HEADER_ITEMS])

            followings: dict = self.extract_followings(self.user_nodes[user_versions.FOLLOWINGS_PROPERTY])
            followers: dict = self.extract_followers(self.user_nodes[user_versions.FOLLOWERS_PROPERTY])
            posts_count: dict = self.extract_posts_count(self.user_nodes[user_versions.POSTS_COUNT_PROPERTY])

            user = user_name | displayed_name | account_status | biography | profile_header | followings | followers | posts_count

            del self.username
            del self.user_tree
            del self.user_nodes

            return user
        
        except ParseUserException as e:
            raise e
        
        except Exception as e:
            print(self.user_nodes)
            raise e
        
    def extract_user_name(self, section):
        try:
            return {user_versions.USERNAME_PROPERTY : section.text_content()}
        except Exception as e:
            raise ExtractUserException(f'Could not extract the user name of {self.username}. Reason {e} ')
        
    def extract_displayed_name(self, section):
        try:
            name_elements: list = section.getchildren()

            displayed_name_chunks: list = list()
            for item in name_elements:
                self._process_text(item, displayed_name_chunks)
                self._process_link(item, displayed_name_chunks)
                self._process_emoji(item, displayed_name_chunks)

            displayed_name: str = ''.join(displayed_name_chunks)

            return {user_versions.DISPLAYED_NAME_PROPERTY : displayed_name}
        except Exception as e:
            raise ExtractUserException(f'Could not extract the displayed name of {self.username}. Reason {e} ')
    
    def extract_account_status(self, section):

        try:

            account_status: dict = {
                user_versions.IS_VERIFIED_PROPERTY : False,
                user_versions.VERIFIED_TYPE_PROPERTY : None,
                user_versions.IS_PRIVATE_PROPERTY : False
            }

            span_status: list = section.getchildren()
            for span in span_status:
                self._set_account_status(span, account_status)

            return account_status
        except Exception as e:
            raise ExtractAccountStatusException(f'Could not extract the account status of the user {self.username}. Reason {e}')

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
    def extract_biography(self, section):
        try:

            biography_content: str = None
            if section is not None:
                biography_elements = section.getchildren()
                
                biography_chunks: list = list()
                for element in biography_elements:
                    self._process_text(element, biography_chunks)
                    self._process_link(element, biography_chunks)
                    self._process_emoji(element, biography_chunks)
                    self._process_mention(element, biography_chunks)
                    self._process_hashtag(element, biography_chunks)

                biography_content: str = ''.join(biography_chunks)
                del biography_chunks

            return {user_versions.BIOGRAPHY_PROPERTY: biography_content}
        
        except ExtractBiographyException as e:
            raise e

    def extract_profile_header(self, section):

        try:
            header_items: list = section.getchildren()
            
            header: dict = {
                user_versions.CATEGORY_PROPERTY: user_versions.DEFAULT_CATEGORY,
                user_versions.LOCATION_PROPERTY: None,
                user_versions.LINK_PROPERTY: None,
                user_versions.JOIN_DATE_PROPERTY: None
            }
            for item in header_items:
                self._extract_category(item, header)
                self._extract_location(item, header)
                self._extract_link(item, header)
                self._extract_join_date(item, header)

            return header
        except Exception as e:
            raise ExtractHeaderProfileException(f'Could not extract the header profile for the user {self.username}. Reason {e}')


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

                header[user_versions.JOIN_DATE_PROPERTY] = self._convert_date_with_month(raw_join_date)

        except Exception as e:
            raise ExtractJoinDateException(f'Could not extract the join date of {self.username}. Reason {e}')
        
    def _convert_date_with_month(self, date: str):
        date_object = datetime.strptime(date, '%B %Y')
        return date_object.strftime('%Y-%m')
    
    def _convert_date_with_year_day_month(self, date: str):
        ...
    
    def extract_followings(self, section):
        try:
            followings_raw: str = section.text_content()
            return {user_versions.FOLLOWINGS_PROPERTY: self._convert_number_to_integer(followings_raw)}
        except ConvertNumberToIntegerException as e:
            raise e
        except Exception as e:
            raise ExtractFollowingsFollowersException(f'Could not extract the number of followings of the user {self.username}. Reason {e}')
    
    def extract_followers(self, section):
        try:
            followers_raw: str = section.text_content()
            return {user_versions.FOLLOWERS_PROPERTY: self._convert_number_to_integer(followers_raw)}
        except ConvertNumberToIntegerException as e:
            raise e
        except Exception as e:
            raise ExtractFollowingsFollowersException(f'Could not extract the number of followers of the user {self.username}. Reason {e}')
        
    def extract_posts_count(self, section):
        try:
            post_counts_raw: str = section.text_content()
            post_counts_raw_split = post_counts_raw.split(' posts')
            if len(post_counts_raw) == 2:
                post_counts_raw = post_counts_raw_split[0]
                return {user_versions.POSTS_COUNT_PROPERTY: self._convert_number_to_integer(post_counts_raw)}
            
            post_counts_raw = post_counts_raw.split(' post')[0]
            return {user_versions.POSTS_COUNT_PROPERTY: self._convert_number_to_integer(post_counts_raw)}
        except ConvertNumberToIntegerException as e:
            raise e
        except Exception as e:
            raise ExtractPostsCountException(f'Could not extract the number of posts of the user {self.username}. Reason {e}')
    
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