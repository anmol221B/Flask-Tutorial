# CONFIGURATION :  
# The SECRET_KEY configuration variable that I added as the only configuration item is an important part in most Flask applications. 
# Flask and some of its extensions use the value of the secret key as a cryptographic key, useful to generate signatures or tokens. 
# The Flask-WTF extension uses it to protect web forms against a nasty attack called Cross-Site Request Forgery or CSRF (pronounced "seasurf"). 
# As its name implies, the secret key is supposed to be secret, as the strength of the tokens and signatures generated with it depends on no person outside of the trusted maintainers of the 
# application knowing it.

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['anmol.cogni16@gmail.com']



# I think it is very important that I take a proactive approach regarding errors. If an error occurs on the production version of the application, I want to know right away. So my first solution 
# is going to be to configure Flask to send me an email immediately after an error, with the stack trace of the error in the email body.

# The configuration variables for email include the server and port, a boolean flag to enable encrypted connections, and optional username and password. The five configuration variables are sourced 
# from their environment variable counterparts. If the email server is not set in the environment, then I will use that as a sign that emailing errors needs to be disabled. The email server port can also 
# e given in an environment variable, but if not set, the standard port 25 is used. Email server credentials are by default not used, but can be provided if needed. The ADMINS configuration variable is a 
# ist of the email addresses that will receive error reports, so your own email address should be in that list.

