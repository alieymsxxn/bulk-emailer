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
        def mk_params_dir():
            def create_ini_file(file_path):
                # initialize a config object
                config = configparser.ConfigParser()
                # config['SYS_CONFIG'] = {
                #     'number_of_chunks': '',
                #     'schedule': '',
                # }
                # define dict for the config file
                config['EMAIL_CONFIG'] = {
                    'target_emails'         : 'person1@somemail.com,person2@somemailmail.com',
                    'sender_name'           : 'Some Person',
                    'sender_email'          : 'sender@mymail.com',
                    'sender_password'       : '12345678',
                    'smtp_port'             : '587',
                    'smtp_host'             : 'smtp.gmail.com',
                    'test_recipient_email'  : 'testperson@mymail.com',
                    'test_recipient_name'   : 'Test Person',
                    'content_type'          : 'html',
                    'content_filename'      : 'index.html'
                }
                # write to the conifg file
                with open(file_path, 'w') as file:
                    config.write(file)     
                  
            # dirs
            dirs = {}
            # get bulk_emailer_home environment var if set
            home_dir_path = os.getenv('BULK_EMAILER_HOME')
            # if environment var not set, get path to home dir
            home_dir_path = home_dir_path if home_dir_path else expanduser('~')
            print(f'Home dir found at {home_dir_path}')
            # form string of path to .bulk-emaile folder in the home dir
            home_dir_path = home_dir_path+'/.bulk-emailer'
            dirs['home_dir'] = home_dir_path
            # form string of  path to .bulk-emaile/templates folder in the home dir
            template_dir_path = home_dir_path+'/templates'
            dirs['template_dir'] = template_dir_path
            # form string of path to .bulk-emaile/logs folder in the home dir
            logs_dir_path = home_dir_path+'/logs'
            dirs['logs_dir'] = logs_dir_path
            
           # form string of path to .bulk-emaile/params.config file in the home dir
            params_file_path = home_dir_path+'/params.config'
            dirs['params_file'] = params_file_path

            # create all the directories inside home directory if they don't exist
            if not os.path.isdir(home_dir_path) : os.mkdir(home_dir_path) 
            if not os.path.isdir(template_dir_path) : os.mkdir(template_dir_path)
            if not os.path.isdir(logs_dir_path) : os.mkdir(logs_dir_path)
            # create the config file if it does not exist
            if not os.path.exists(params_file_path): create_ini_file(params_file_path)

            return dirs
        dirs = mk_params_dir()
        return dirs
                

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
    # create or access all the dirs and get the paths in a dict
    paths_dir = access_params_dir()


    parser = configparser.ConfigParser()
    parser.read(paths_dir['home_dir']+'/params.config')
    params = dict(parser.items('EMAIL_CONFIG'))
    validate_params(params)
    
    # return validate_params(params), home_dir_path


class BulkEmailer:
    _retry = 0
    def __init__(self):
        get_params()
        # self.conn = self.establish_connection()
    
    def reconnect(self):
        self._retry = self._retry + 1
        if self._retry > 5:
            print('INFO:reconnect:Waiting for 60s before reconnecting again.')
            time.sleep(60)
            self._retry = 0
        print(f'INFO:reconnect:Attempting to reconnect {self._retry}.')
        self.conn = self.establish_connection()
    
    def close(self):
        self.conn.quit()
        print('INFO:close:Connection has been closed.')
    
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
                # self.conn.send_message(msg)
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
                exit()
        print('Script ended.')
        self.close()



if __name__ == '__main__':
    be = BulkEmailer()
    # be.send_email()
    