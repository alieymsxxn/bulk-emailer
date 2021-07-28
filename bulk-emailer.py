import os
import re
import time
import smtplib
import configparser
from email import message
from os.path import expanduser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def access_params_dir():
        def create_ini_file(file_path):
            config = configparser.ConfigParser()
            config['SYS_CONFIG'] = {
                'number_of_chunks': '',
                'schedule': '',
            }
            config['EMAIL_CONFIG'] = {
                'target_emails' : 'aliey8998@gmail.com,mohsinalisep@gmail.com',
                'sender_name' : 'Mohsin Ali',
                'sender_email' : 'aliey8998@gmail.com',
                'sender_password' : 'aliey8998',
                'smtp_port' : '587',
                'smtp_host' : 'smtp.gmail.com',
                'test_recipient_email' : 'mohsinalisep@gmail.com',
                'test_recipient_name' : 'Mohsin Ali Test',
                'content' : 'html',
                'content_path' : 'index.html'
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

            return home_dir_path
        home_dir_path = mk_params_dir()
        return home_dir_path
                

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
    home_dir_path = access_params_dir()
    print(f'Home dir found at {home_dir_path}')
    parser = configparser.ConfigParser()
    parser.read(home_dir_path+'/params.config')
    params = dict(parser.items('EMAIL_CONFIG')+parser.items('SYS_CONFIG'))
    return validate_params(params), home_dir_path


class BulkEmailer:
    _retry = 0
    def __init__(self):
        self.params, self.home_dir_path = get_params()
        self.conn = self.establish_connection()
    
    def reconnect(self):
        self._retry = self._retry + 1
        if self._retry > 5:
            print('INFO:reconnect:Waiting for 60s before reconnecting again.')
            time.sleep(60)
            self._retry = 0
        print(f'INFO:reconnect:Attempting to reconnect {self._retry}.')
        self.conn = self.establish_connection()

    def establish_connection(self):
        try:
            conn = smtplib.SMTP(host=self.params['smtp_host'], port=self.params['smtp_port'])
            conn.starttls()
            conn.login(user=self.params['sender_email'][0], password=self.params['sender_password'])
            print('SUCCESS:establish_connection:Connection has been extablished.')
            return conn
        except smtplib.SMTPSenderRefused as e:
            print('ERROR:establish_connection:Connection refused by the smtp host.')
            exit()
        except smtplib.SMTPServerDisconnected as e:
            print('ERROR:establish_connection:Connection disconnected by the smtp host.')
            exit()
        except Exception as e:
            print('ERROR:establish_connection:An unknown error has occured.')
            exit()

    def send_email(self):
        # For each contact, send the email:
        for count, email in enumerate(self.params['target_emails']):
            msg = MIMEMultipart()       # create a message
            if count%10 == 0 and count != 0:
                print('INFO:send_email:Sleeping for 60s.')
                time.sleep(60)
            if self.params['content'] == 'html':
                fully_qualified_path = self.home_dir_path+'/templates/'+self.params['content_path']
                with open(fully_qualified_path, 'r') as file:
                    body = file.read()                
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))

            msg['From']=self.params['sender_email'][0]
            msg['To']=email
            msg['Subject']='bulk_emailer'
            
            try:
                self.conn.send_message(msg)
                print('SUCCESS:send_email:Message sent to', email)
            except smtplib.SMTPSenderRefused as e:
                print('ERROR:send_email:Connection refused by the smtp host.')
                self.reconnect()
            except smtplib.SMTPServerDisconnected as e:
                print('ERROR:send_email:Connection refused by the smtp host.')
                self.reconnect()
            except Exception as e:
                print('An unknown error has occured.')
                print(e)
                exit(-1)
            


if __name__ == '__main__':
    be = BulkEmailer()
    be.send_email()
    