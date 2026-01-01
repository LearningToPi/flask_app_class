import sys
import argparse
from logging_handler import DEBUG, INFO, WARNING, ERROR, CRITICAL
from flask_app_class import FlaskApp

parser = argparse.ArgumentParser(description="Flask Class Based application framework.")
parser.add_argument("--config", type=str, default=None, help='Enter a JSON configuration file to load.')
parser.add_argument("--log_level", type=str, default='DEBUG', help='Enter a logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")')
args = parser.parse_args()

app = FlaskApp(config_file=args.config, web_log_level=args.log_level, app_log_level=args.log_level)
app.start()