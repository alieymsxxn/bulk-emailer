import os
import configparser
from helper import *

parser = configparser.ConfigParser()
parser.read("params.config")


target_emails_list = produce_emails_list(parser.get("config", "TARGET_EMAILS_LIST"))


host = parser.get("config", "SMTP_HOST")
port = parser.get("config", "SMTP_PORT")
credentials = {
    'sender_name':parser.get("config", "SENDER_NAME"),
    'sender_email':parser.get("config", "SENDER_EMAIL"),
    'sender_password':parser.get("config", "SENDER_PASSWORD")
}

connection = establish_connection(host=host, port=port, credentials=credentials)