from gevent import monkey
monkey.patch_all()
from .monkey_patch import patch_wsgihandler
patch_wsgihandler()
from flask import Flask, render_template, send_from_directory, g, session, send_file
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from urllib.parse import urlparse, urljoin
import os
import json
import inspect
from datetime import datetime, timedelta
from threading import Lock, Thread
from time import sleep
import re, glob
from flask_socketio import SocketIO, emit, disconnect
from werkzeug.middleware.proxy_fix import ProxyFix
from logging_handler import create_logger, DEBUG, INFO

'''
==================================
Global Variables available in to all modules
==================================
'''
FLASK_SECRET_LENGTH = 128
FLASK_DEFAULT_STATIC_DIR = 'static'
BASE_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'base_templates')


def load_config_json(config_file:str):
    ''' Load a json config file '''
    global config_data
    with open(config_file, 'r', encoding='utf-8') as input_file:
        config_data = json.loads(input_file.read())
    return config_data

class FlaskApp:
    ''' Class to hold and manage all the general flask related data and functions '''
    def __init__(self, config_file:str, flask_logger=None, app_logger=None, app_path=None,
                 templates_path=os.path.join(os.path.dirname(__file__), 'templates')):
        # app config
        self.config_file = config_file
        self.config = {}
        self._templates = None
        self.site_data = {
            'templates_path': os.path.abspath(templates_path),
            'app_path': app_path,
            }

        # init objects
        self.app = None
        self.login_manager = None
        self.async_mode = None
        self.socketio = None
        self.user_controller = None

        # configure loggers
        if type(flask_logger).__name__ != 'RootLogger' or type(flask_logger).__name__ != 'Logger' or flask_logger is None:
            self.flask_logger = create_logger(INFO)
        else:
            self.flask_logger = flask_logger
        if type(app_logger).__name__ != 'RootLogger' or type(app_logger).__name__ != 'Logger' or app_logger is None:
            self.app_logger = create_logger(DEBUG, name=__name__)
        else:
            self.app_logger = app_logger

        # create list of web pages and API url's
        self.web_pages = {
            'web_home': {
                'routes': ['/', '/index.html', '/default.html'],
                'params': {}
            }
        }
        self.api_pages = {}

        # mapping of static path overrides and all static content pages
        self.static_pages = {}
        self.static_page_args = {}

        self.init()

    @property
    def base_templates(self):
        ''' Return a list of the available base templates '''
        if self._templates is not None:
            return self._templates
        self._templates = []
        for entry in os.scandir(BASE_TEMPLATE_PATH):
            if entry.is_dir():
                # check for a templates folder
                for template_entry in os.scandir(entry.path):
                    if template_entry.name == 'templates':
                        self._templates.append(entry.name)
        return self._templates

    def init_login_manager(self):
        ''' Configure the login manager '''
        self.login_manager = LoginManager()
        self.login_manager.login_view = self.site_data.get('login_page', '/login.html')
        self.login_manager.init_app(self.app)
        if self.config.get('auth', '').lower() == 'radius' or self.config.get('authentication', '').lower() == 'radius':
            from .user_radius import RadiusUserController
            self.user_controller = RadiusUserController(**self.config.get('radius'))
            self.login_manager.user_loader(self.user_controller.get_user)

    def init(self):
        ''' Stop the running process and recreate all Flask objects.  Allows a complete reset of the Flask environment with all routes '''
        self.stop()
        self.config = load_config_json(self.config_file)

        # flask objects
        self.app = Flask(__name__, static_folder=self.config.get('static_dir', os.path.join(os.getcwd(), FLASK_DEFAULT_STATIC_DIR)), template_folder=self.site_data['templates_path'])
        self.web_static_dir = self.config.get('static_dir', FLASK_DEFAULT_STATIC_DIR)
        self.web_static_inc_subs = self.config.get('web_static_inc_subs', True)
        self.async_mode = None
        self.app.wsgi_app = ProxyFix(self.app.wsgi_app, x_proto=1, x_host=1)
        self.socketio = SocketIO(self.app, async_mode=self.async_mode, cors_allowed_origins='*')

        self.site_data['base_template'] = self.config.get('base_template', None) if self.config.get('base_template', None) in self.base_templates else None
        self.site_data['debug'] = self.config.get('debug', False)
        self.site_data['auth'] = self.config.get('auth', None)
        if self.site_data['auth'] is not None:
            self.site_data['login_page'] = self.config.get('login_page', '/login.html')
            self.site_data['logout_page'] = self.config.get('login_page', '/logout.html')

        # configure the site template by creating a sym-link to the base template under the Flask site templates (Flask requires all templates to be in 1 dir)
        if self.site_data.get('base_template', None) is not None:
            if os.path.exists(os.path.join(self.site_data['templates_path'], '_base_template')):
                os.unlink(os.path.join(self.site_data['templates_path'], '_base_template'))
            os.symlink(os.path.join(BASE_TEMPLATE_PATH, self.site_data.get('base_template')), os.path.join(self.site_data['templates_path'], '_base_template'))
            self.site_data['site_template'] = os.path.join('_base_template', 'templates', self.site_data.get('site_template_file', 'base.html.j2'))
        self.site_data.update(self.config.get('site_data', {}))
        self.web_pages.update(self.config.get('web_pages', {}))
        self.api_pages.update(self.config.get('api_pages', {}))
        
        # create sym link for the app in addition to the base template
        if self.site_data.get('app_path', None) is not None and os.path.join(self.site_data.get('app_path', None), 'templates') != self.site_data['templates_path']:
            if os.path.exists(os.path.join(self.site_data['templates_path'], '_app')):
                os.unlink(os.path.join(self.site_data['templates_path'], '_app'))
            os.symlink(self.site_data.get('app_path'), os.path.join(self.site_data['templates_path'], '_app'))

        # configure login manager
        if self.config.get('auth', None) != None or self.config.get('authentication', None) != None:
            self.init_login_manager()

        # load or generate flask secret key
        if os.path.isfile(self.config.get('flask_secret_file', '.flask_secret')):
            with open(self.config.get('flask_secret_file', '.flask_secret'), 'rb') as input_file:
                self.app_logger.info(f"{self.info_str}: Reading flask secret file {self.config.get('flask_secret_file', '.flask_secret')}")
                self.app.secret_key = input_file.read()
        else:
            self.app.secret_key = os.urandom(FLASK_SECRET_LENGTH)
            with open(self.config.get('flask_secret_file', '.flask_secret'), 'wb') as output_file:
                self.app_logger.info(f"{self.info_str}: Writing flask secret file {self.config.get('flask_secret_file', '.flask_secret')}")
                output_file.write(self.app.secret_key)
        self.update_flask_routes(reinit=False)

        # configure dropdowns
        for dropdown_menu in self.config.get('dropdowns', []):
            self.add_dropdown(name=dropdown_menu.get('name', 'Menu'), items=dropdown_menu.get('items', []), replace=True)

    @property
    def dropdown_menus(self) -> list:
        ''' Returns a list of the dropdown menus that are currently configured '''
        if 'dropdowns' not in self.site_data:
            self.site_data['dropdowns'] = []
        return self.site_data['dropdowns']

    def remove_dropdown(self, name:str):
        ''' Deletes a dropdown based on the display name '''
        for i in range(len(self.dropdown_menus)):
            if self.dropdown_menus[i]['name'] == name:
                self.dropdown_menus.remove(i)
                return

    def add_dropdown(self, name:str, items:list, replace=True):
        ''' Add a dropdown to the list of dropdown menus.  Replace will replace the existing menu definition with the provided definition
            Items format: [
                    {'name': '[Display name]',
                     'url': '[URL for the link, relative should start with /]'],
                     'newtab': true|false (default is False)}
                ] '''
        if replace:
            self.remove_dropdown(name)
        for i in range(len(self.dropdown_menus)):
            if self.dropdown_menus[i]['name'] == name:
                for k in range(len(items)):
                    for j in range(len(self.dropdown_menus[i].get('items',[]))):
                        if self.dropdown_menus[i]['items'][j].get('name') == items[k].get('name'):
                            dict(self.dropdown_menus[i]['items'][j]).update(items[k])
                            return
                    # we didn't find a matching item, so add it
                    self.dropdown_menus[i]['items'].append(items[k])
                    return
        # if we didn't run an update, add the menu
        self.dropdown_menus.append({'name': name, 'items': items})

    @property
    def info_str(self):
        ''' Returns the info string for the class (used in logging commands) '''
        return f"{self.__class__.__name__} ({self.config.get('address', '0.0.0.0')}:{self.config.get('port', 8080)}){':DEBUG' if self.config.get('debug', False) else ''}"

    def __del__(self):
        self.stop()

    def update_flask_routes(self, reinit=False):
        ''' Update the flask routes '''
        if reinit or self.app is None:
            self.init()
        # add base template static files
        if self.site_data.get('base_template', None) is not None and os.path.isdir(os.path.join(self.site_data['templates_path'], '_base_template', 'static')):
            self._add_flask_static_files(os.path.join(self.site_data['templates_path'], '_base_template', 'static'))
        # add app static files
        if self.site_data.get('app_path', None) is not None and os.path.isdir(os.path.join(self.site_data['templates_path'], '_app', 'static')):
            self._add_flask_static_files(os.path.join(self.site_data['templates_path'], '_app', 'static'))
        # add static files from the project
        self._add_flask_static_files(os.path.join(os.getcwd(), self.config.get('static_dir', FLASK_DEFAULT_STATIC_DIR)))

        # add dynamic pages
        for page in self.web_pages:
            for route in self.web_pages[page]['routes']:
                self.app.add_url_rule(route, view_func=getattr(self, page), **self.web_pages[page].get('params', {}))

        # add api pages
        for page in self.api_pages:
            for route in self.api_pages[page]['routes']:
                self.app.add_url_rule(route, view_func=getattr(self, page), **self.api_pages[page].get('params', {}))

    def _add_flask_static_files(self, root_path):
        ''' Loop through all files in the path specified and add as static files.  If '_base_template', files will be added WITHOUT the '_base_template' in the route '''
        for static_file in get_all_files(root_path, True):
            self.static_pages[static_file.split(root_path)[1]] = static_file
            self.app.add_url_rule(static_file.split(root_path)[1], view_func=self.web_static_file, **self.static_page_args)

    def start(self, ):
        ''' Start the Flask process in a thread '''
        self.socketio.run(self.app,
                          host=self.config.get('address', '0.0.0.0'),
                          port=self.config.get('port', 8080),
                          debug=self.config.get('debug', False),
                          use_reloader=False)
        sleep(5)

    def render_template(self, template:str, page=None, **kwargs):
        ''' Render the requested template.  Automatically inserts base page data '''
        # get function name of the calling function
        stack = inspect.stack()
        for x in range(len(stack)):
            if stack[x].function == 'render_template':
                break
        if x + 1 < len(stack):
            calling_func = stack[x+1].function
        if os.path.exists(os.path.join(self.site_data['templates_path'], template)):
            return render_template(template, site=self.site_data, page=self.web_pages[calling_func].get('data', {}) if page is None else page, **kwargs)
        elif os.path.exists(os.path.join(self.site_data['templates_path'], '_app', 'templates', template)):
            return render_template(os.path.join('_app', template), site=self.site_data, page=self.web_pages[calling_func].get('data', {}) if page is None else page, **kwargs)
        return render_template(os.path.join('_base_template', 'templates', template), site=self.site_data, page=self.web_pages[calling_func].get('data', {}) if page is None else page, **kwargs)

    def stop(self):
        pass

    def web_home(self):
        return "<body>test123</body>" 

    def web_static_file(self):
        ''' Return a static file '''
        file_name = request.url_rule.rule.rsplit('/', 1)[-1]
        return send_file(self.static_pages[request.url_rule.rule], download_name=file_name, as_attachment=bool(safe_string(request.args.get('download', False))))

    def request_args_safe(self, *args) -> bool:
        ''' Checks that all request arguments are safe strings.  Non-alphanumeric characters that are accepted can be passed as arguments '''
        for argument in request.args:
            if not safe_string(request.args.get(argument), *args):
                self._logger.error(f"{self.info_str}: Argument '{argument}' failed safe check!")
                return False
        return True


def get_all_files(path:str, include_subdir:bool):
    ''' Recursive function to return a list of all files '''
    file_list = []
    if os.path.isdir(path):
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file():
                    file_list.append(entry.path)
                elif entry.is_dir():
                    file_list.extend(get_all_files(entry.path, include_subdir))
    return file_list


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def safe_string(value, *args):
    """ Verify that a passed string is alpha numeric plus any additional safe characters """
    if value is not None:
        for arg in args:
            value = value.replace(arg, 'X')
        if (isinstance(value, str) and str(value).isalnum()) or value == '':
            return True
    return False
