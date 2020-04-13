
# The application will exist in a package. In Python, a sub-directory that includes a __init__.py file is considered a package, and can be imported. 
# When you import a package, the __init__.py executes and defines what symbols the package exposes to the outside world.


from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os




app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'

# The 'login' value above is the function (or endpoint) name for the login view. In other words, the name you would use in a url_for() call to get the URL.
# The way Flask-Login protects a view function against anonymous users is with a decorator called @login_required. When you add this decorator to a view function below the @app.route decorators 
# from Flask, the function becomes protected and will not allow access to users that are not authenticated. Here is how the decorator can be applied to the index view function of the application:

from app import routes,models,errors

# The script above simply creates the application object as an instance of class Flask imported from the flask package. 
# The __name__ variable passed to the Flask class is a Python predefined variable, which is set to the name of the module in which it is used. 
# Flask uses the location of the module passed here as a starting point when it needs to load associated resources such as template files, which I will cover in Chapter 2.
#  For all practical purposes, passing __name__ is almost always going to configure Flask in the correct way. The application then imports the routes module, which doesn't exist yet.

# One aspect that may seem confusing at first is that there are two entities named app. The app package is defined by the app directory and the __init__.py script, 
# and is referenced in the from app import routes statement. The app variable is defined as an instance of class Flask in the __init__.py script, which makes it a member of the app package.

# Another peculiarity is that the routes module is imported at the bottom and not at the top of the script as it is always done. 
# The bottom import is a workaround to circular imports, a common problem with Flask applications. You are going to see that the routes module needs to import the app variable defined in this script, 
# so putting one of the reciprocal imports at the bottom avoids the error that results from the mutual references between these two files.


# Flask uses Python's logging package to write its logs, and this package already has the ability to send logs by email. All I need to do to get emails sent out on errors is to add a SMTPHandler 
# instance to the Flask logger object, which is app.logger:

if not app.debug:
	if app.config['MAIL_SERVER']:
		auth = None
		if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
			auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
		secure = None
		if app.config['MAIL_USE_TLS']:
			secure = ()
		mail_handler = SMTPHandler(
			mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
			fromaddr='no-reply@' + app.config['MAIL_SERVER'],
			toaddrs=app.config['ADMINS'], subject='FlASK_APP Failure',
			credentials=auth, secure=secure)
		mail_handler.setLevel(logging.ERROR)
		app.logger.addHandler(mail_handler)


# As you can see, I'm only going to enable the email logger when the application is running without debug mode, which is indicated by app.debug being True, and also when the email server exists in 
# the configuration.

# Setting up the email logger is somewhat tedious due to having to handle optional security options that are present in many email servers. But in essence, the code above creates a SMTPHandler instance, 
# sets its level so that it only reports errors and not warnings, informational or debugging messages, and finally attaches it to the app.logger object from Flask.

# export MAIL_SERVER=smtp.googlemail.com
# export MAIL_PORT=587
# export MAIL_USE_TLS=1
# export MAIL_USERNAME=<your-gmail-username>
# export MAIL_PASSWORD=<your-gmail-password>

	if not os.path.exists('logs'):
		os.mkdir('logs')
	file_handler = RotatingFileHandler('logs/flask_tut.log', maxBytes=10240,
                                   backupCount=10)
	file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
	file_handler.setLevel(logging.INFO)
	app.logger.addHandler(file_handler)

	app.logger.setLevel(logging.INFO)
	app.logger.info('FlASK APP startup')

# The RotatingFileHandler class is nice because it rotates the logs, ensuring that the log files do not grow too large when the application runs for a long time. In this case I'm limiting the size of
# the log file to 10KB, and I'm keeping the last ten log files as backup.
