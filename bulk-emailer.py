# chunks logic
# email sending limits

import os
import re
import smtplib
import configparser
from os.path import expanduser

def access_params_dir():
        def create_ini_file(file_path):
            config = configparser.ConfigParser()
            config['SYS_CONFIG'] = {
                'number_of_chunks': '',
                'schedule': '',
            }
            config['EMAIL_CONFIG'] = {
                'target_emails': 'aliey8998@gmail.com,mohsinalisep@gmail.com',
                'sender_name': 'Mohsin Ali',
                'sender_email': 'aliey8998@gmail.com',
                'sender_password': 'aliey8998',
                'smtp_port': '587',
                'smtp_host': 'smtp.gmail.com',
                'test_recipient_email': 'mohsinalisep@gmail.com',
                'test_recipient_name': 'Mohsin Ali Test',
            }

            with open(file_path, 'w') as configfile:
                config.write(configfile)       
        def mk_params_dir():
            # dirs
            home_dir_path = os.getenv('BULK_EMAILER_HOME')
            home_dir_path = home_dir_path if home_dir_path else expanduser('~')
            home_dir_path = home_dir_path+'/.bulk-emailer'
            template_dir_path = home_dir_path+'/templates'
            logs_dir_path = home_dir_path+'/logs'
            
            # params file
            params_file_path = home_dir_path+'/params.config'

            if not os.path.isdir(home_dir_path) : os.mkdir(home_dir_path) 
            if not os.path.isdir(template_dir_path) : os.mkdir(template_dir_path)
            if not os.path.isdir(logs_dir_path) : os.mkdir(logs_dir_path)
            if not os.path.exists(params_file_path): create_ini_file(params_file_path)

            return params_file_path
        params_file_path = mk_params_dir()
        return params_file_path
                

def validate_params(params):
    def validate_emails(strr, empty_check=True):
        def _validate_email(email):
            if not email:
                if empty_check:
                    raise ValueError(f'Empty email can not be accepted.')
                return email
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if(re.match(regex, email)):
                return email
            else:
                raise ValueError(f'Faulty email was provided in TARGET_EMAILS.\n>> {email}')
        try:
            strr = [_validate_email(email.strip()) for email in strr.split(',')]
            return strr
        except Exception as e:
            print(e)

    params['target_emails'] = validate_emails(params['target_emails'])
    params['sender_email'] = validate_emails(params['sender_email'])
    params['test_recipient_email'] = validate_emails(params['test_recipient_email'], empty_check=False)

    return params


def get_params(path_to_params=None):
    # add validations
    params_file_path = access_params_dir()
    print(f'Home dir found at {params_file_path}')
    parser = configparser.ConfigParser()
    parser.read(params_file_path)
    params = dict(parser.items('EMAIL_CONFIG')+parser.items('SYS_CONFIG'))
    return validate_params(params)


class BulkEmailer:

    def __init__(self):
        self.params = get_params()
        # self.conn = self.establish_connection()
    

    def establish_connection(self):
        # add try except
        print(self.params['smtp_port'])
        print(self.params['smtp_host'])
        conn = smtplib.SMTP(host=self.params['smtp_host'], port=self.params['smtp_port'])
        conn.starttls()
        conn.login(user=self.params['sender_email'], password=self.params['sender_password'])
        return conn

    def send_email(self):
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        # For each contact, send the email:
        for email in self.params['target_emails']:
            msg = MIMEMultipart()       # create a message

            # add in the actual person name to the message template
            # message = message_template.substitute(PERSON_NAME=name.title())
            message = 'ILY SHRUTZZ'

            # setup the parameters of the message
            msg['From']=self.params['sender_email']
            msg['To']=email
            msg['Subject']="Test Email"

            # add in the message body
            msg.attach(MIMEText(message, 'plain'))

            # send the message via the server set up earlier.
            self.conn.send_message(msg)

            print('message sent to', email)
            


if __name__ == '__main__':
    be = BulkEmailer()
    # be.send_email()
    