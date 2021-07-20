import re

def produce_emails_list(strr):
    def validate_email(email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.match(regex, email)):
            return email
        else:
            raise ValueError(f'Faulty email was provided in TARGET_EMAILS_LIST.\n>> {email}')
    try:
        strr = [validate_email(email.strip()) for email in strr.split(',')]
    except Exception as e:
        print(e)

def establish_connection(host, port, credentials):
    print(host)
    print(port)
    print(credentials)