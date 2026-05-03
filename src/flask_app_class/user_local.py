import logging
from .user_controller import FlaskUserController, FlaskUser
import passlib.hash
from config_file_manager import load_file


class LocalUserController(FlaskUserController):
    ''' Extend the base FlaskUserController to utilize a local file for authentication and authorization. The file should be in the format of a JSON file with a list of users and their hashed passwords. 
        Example: {
                    users: [
                        {"id": 1, "username": "user1", "password_hash": "hashed_password1"},
                        {"id": 2, "username": "user2", "password_hash": "hashed_password2"}
                    ],
                    hash_func: 'pbkdf2_sha256'
                  } '''
    
    def __init__(self, user_file:str, logger=logging):
        super().__init__(logger=logger)
        self._inherit_info_str = f'LocalUserController:{user_file}'
        self._logger.info(f"{self.info_str}: Loading users from file")
            self.config_manager = load_file(user_file, save_on_change=True)

    def authenticate_user(self, username:str, password=None, password_hash=None, strip_username=True, lcase_username=True):
        ''' Authenticate a user and return a FlaskUser object '''
        if strip_username:
            username = username.strip() # Remove spaces that might be before or after the username
        if lcase_username:
            username = username.lower() # Easier for mobile devices that might capitalize the first letter
        user_list = self.config_manager.get('users', [])
        for user in user_list:
            if user['username'] == username:
                if password_hash is not None:
                    if 'hash_func' not in self.config_manager:
                        self._logger.info(f"{self.info_str}: No hash function specified in config, defaulting to pbkdf2_sha256")
                        self.config_manager['hash_func'] = 'pbkdf2_sha256'
                    if getattr(passlib.hash, self.config_manager['hash_func']).verify(password_hash, user['password_hash']):
                        self._logger.info(f"{self.info_str}: {username}: Auth Successful")
                        return FlaskUser(user_id=username, username=username, auth_ok=True, acct_active=True)
        return None
    
    def get_user(self, user_id=None):
        ''' Find a user from a username or user_id '''
        if user_id is not None:
            user_list = self.config_manager.get('users', [])
            for user in user_list:
                if user['id'] == user_id:
                    return FlaskUser(user_id=user['id'], username=user['username'], auth_ok=False, acct_active=False)
        return None
    
    def add_user(self, username:str, password:str):
        ''' Add a user to the user file with a hashed password '''
        # get the next user id by finding the max id in the current user list and adding 1, if the list is empty start with 1
        user_id = max([user['id'] for user in self.config_manager.get('users', [])], default=0) + 1
        if 'hash_func' not in self.config_manager:
            self._logger.info(f"{self.info_str}: No hash function specified in config, defaulting to pbkdf2_sha256")
            self.config_manager['hash_func'] = 'pbkdf2_sha256'

        password_hash = getattr(passlib.hash, self.config_manager['hash_func']).hash(password)
        if 'users' not in self.config_manager:
            self.config_manager['users'] = []
        self.config_manager['users'].append({'id': user_id, 'username': username, 'password_hash': password_hash})

    def delete_user(self, username:str):
        ''' Delete a user from the user file '''
        user_list = self.config_manager.get('users', [])
        if username in [user['username'] for user in user_list]:
            user_list = [user for user in user_list if user['username'] != username]
            self.config_manager['users'] = user_list
            self._logger.info(f"{self.info_str}: User {username} deleted")
        else:
            self._logger.warning(f"{self.info_str}: User {username} not found in user list")
