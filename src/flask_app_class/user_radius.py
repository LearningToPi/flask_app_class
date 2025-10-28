import logging
from .user_controller import FlaskUserController, FlaskUser
from ._radius import Radius, DEFAULT_RETRIES, DEFAULT_TIMEOUT


class RadiusUserController(FlaskUserController):
    ''' Extends the base FlaskUserController to utilize a RADIUS backend for authentication and authorization
        NOTES: 
            - Radius user controller only supports read methods, 
            - user_id is the username
            - user_table is a list of user id's that should be permitted (can be used to filter users): [1, 55, 132]
        '''
    def __init__(self, host:str, shared_secret:str, port=1812, user_table=None, logger=logging, retries=DEFAULT_RETRIES, timeout=DEFAULT_TIMEOUT):
        super().__init__(logger=logger)
        self._inherit_info_str = f'{host}:{port}'
        self._logger.info(f"{self.info_str}: Connecting to RADIUS Server")
        self.radius = Radius(secret=shared_secret, host=host, port=port, retries=retries, timeout=timeout)
        self.user_table = user_table if user_table is not None else []

    def authenticate_user(self, username:str, password=None, password_hash=None, strip_username=True, lcase_username=True):
        ''' Authenticate a user and return a FlaskUser object '''
        if strip_username:
            username = username.strip() # Remove spaces that might be before or after the username
        if lcase_username:
            username = username.lcase() # Easier for mobile devices that might capitalize the first letter
        if len(self.user_table) == 0 or username in self.user_table:
            if self.radius.authenticate(username=username, password=password):
                self._logger.info(f"{self.info_str}: {username}: Auth Successful")
                return FlaskUser(user_id=username, username=username, auth_ok=True, acct_active=True)
        return None

    def authorize_user(self, username: str, **kwargs):
        ''' Need to setup the radius package to return extended attributes to use authorization '''
        return NotImplemented

    def get_user(self, user_id=None):
        ''' Find a user from a user_id - Currently requires the user list '''
        if user_id in self.user_table:
            return FlaskUser(user_id, user_id, False, False)
        return None
