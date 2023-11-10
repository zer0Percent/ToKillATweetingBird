import sys
import logging
from lxml import  html
from user import user_versions
from user.user_parser import UserParser
from connection.content_parsed_saver import ContentParsedSaver
from user.user_parser_exceptions import GetRawUsersException, ParseUserException, PersistingUserException

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class UserParserRunner:
    def __init__(self) -> None:
        self.user_saver: ContentParsedSaver = ContentParsedSaver()

    def start(self):

        try:
            parsed_users_count: int = 0
            logging.info(f'Parsing and inserting users...')
            while True:
                raw_users: list = self.user_saver.get_raw_users()

                if len(raw_users) == 0:
                    logging.info(f'Parsed and inserted {parsed_users_count} Closing parser.')
                    self.user_saver.close_connection_destiny()
                    return parsed_users
                parsed_users: int = self.persist_users(raw_users)
                parsed_users_count += parsed_users
                logging.info(f'Parsed {parsed_users_count}.')
                del raw_users

        except GetRawUsersException as e:
            logging.error(f'{e.message} Closing tool.')
            self.user_saver.close_connection_source()
            self.user_saver.close_connection_destiny()
            
        except Exception as e:
            logging.error(f'Could not insert the users. Closing tool. Reason: {e}')
            self.user_saver.close_connection_source()
            self.user_saver.close_connection_destiny()

    def persist_users(self, raw_users: list):
        parsed_users: int = 0

        for id, username, byte_array_content in raw_users:

            try:   
                content = bytearray(byte_array_content).decode()
                user_tree = html.fromstring(content)

                user_version_xpaths: dict = self.get_user_version_xpaths()
                user_parser: UserParser = UserParser(username=username, user_tree=user_tree, xpaths=user_version_xpaths)

                user_parsed: dict = user_parser.parse_user()
                
                tuple_user_parsed = (
                    user_parsed[user_versions.USERNAME_PROPERTY],
                    user_parsed[user_versions.DISPLAYED_NAME_PROPERTY],
                    user_parsed[user_versions.IS_VERIFIED_PROPERTY],
                    user_parsed[user_versions.VERIFIED_TYPE_PROPERTY],
                    user_parsed[user_versions.IS_PRIVATE_PROPERTY],
                    user_parsed[user_versions.BIOGRAPHY_PROPERTY],
                    user_parsed[user_versions.CATEGORY_PROPERTY],
                    user_parsed[user_versions.LOCATION_PROPERTY],
                    user_parsed[user_versions.LINK_PROPERTY],
                    user_parsed[user_versions.JOIN_DATE_PROPERTY],
                    user_parsed[user_versions.FOLLOWINGS_PROPERTY],
                    user_parsed[user_versions.FOLLOWERS_PROPERTY],
                    user_parsed[user_versions.POSTS_COUNT_PROPERTY]
                )
                
                self.user_saver.save_user(tuple_user_parsed, id)

                parsed_users += 1

                del user_version_xpaths
                del user_parsed
                del user_parser

            except ParseUserException as e:
                logging.error(f'{e.message}')

            except PersistingUserException as e:
                logging.error(f'{e.message}')

            except Exception as e:
                print(e)
                logging.error(f'{e}')
        
        return parsed_users
    
    def get_user_version_xpaths(self):
        return user_versions.USER_XPATH_VERSIONS['v1']