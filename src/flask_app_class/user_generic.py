'''
Generic user controller for when no other user controller is used.  Returns 'admin' as the user and always logged in
'''

import logging
from .user_controller import FlaskUserController, FlaskUser


class GenericUserController(FlaskUserController):
    ''' Extends the base FlaskUserController to always return a logged in user of 'admin' '''
    def __init__(self, logger=logging):
        super().__init__(logger=logger)

    def authenticate_user(self, *args, **kwargs):
        ''' Authenticate a user and return a FlaskUser object '''
        return FlaskUser(user_id='admin', username='admin', auth_ok=True, acct_active=True)

    def get_user(self, user_id=None):
        ''' Find a user from a user_id - Currently requires the user list '''
        return FlaskUser(user_id='admin', username='admin', auth_ok=True, acct_active=True)
