from flask_login import UserMixin
import logging

class FlaskUserController:
    ''' Parent class to handle basic user management functions.  Tasks should be overriden by an inherritting class  '''
    def __init__(self, logger=logging):
        self._logger = logger
        self._inherit_info_str = ''

    def __del__(self):
        self.close()

    def close(self):
        pass

    @property
    def info_str(self):
        ''' Returns the info string for the class (used in logging commands) '''
        return f"{self.__class__.__name__}({self._inherit_info_str})"

    def authenticate_user(self, username:str, password=None, password_hash=None):
        ''' Authenticate a user and return a FlaskUser object '''
        return NotImplemented

    def authorize_user(self, username:str, **kwargs):
        ''' Authorize a user based on criteria that is passed '''
        return NotImplemented

    def get_user(self, username=None, user_id=None):
        ''' Find a user from a username or user_id '''
        return NotImplemented
    
    def enable_user(self, user_id):
        ''' Mark a user as enabled '''
        return NotImplemented

    def disable_user(self, user_id):
        ''' Mark a user as disabled '''
        return NotImplemented

    def add_user(self, username:str, password=None, enabled=True, **kwargs):
        ''' Create a new user in the underlying system '''
        return NotImplemented

    def delete_user(user_id):
        ''' Delete a user in the underlying system ''' 
        return NotImplemented

    def update_user(self, user_id, username=None, password=None, enabled=None, **kwargs):
        ''' Update properties for a user in the underlying system '''
        return NotImplemented
        

class FlaskUser(UserMixin):
    '''
    Represents a user that has attempted a login via the FlaskLoginController. 
    Extends the Flask UserMixin class to represent the user. Base class includes __eq__ and __ne__ functions
    '''
    def __init__(self, user_id:str|int, username:str, auth_ok:bool, acct_active:bool):
        ''' Create an instance to represent a user login ''' 
        self._user_data = (user_id, username, auth_ok, acct_active)

    @property
    def is_active(self):
        ''' is_active returns True if the account is active (not suspended or rejected for reasons other than auth) '''
        return self._user_data[4]

    @property
    def username(self):
        return self._user_data[1]

    @property
    def name(self):
        return self.user_data[1]

    @property
    def is_authenticated(self):
        ''' Returns True if the account is authenticated '''
        return self._user_data[2]

    def get_id(self):
        return self._user_data[0]

    def __str__(self):
        ''' Return the username and ID as a string '''
        return f"{self.username}({self.get_id()})"