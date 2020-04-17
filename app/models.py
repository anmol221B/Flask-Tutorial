# Flask-Migrate exposes its commands through the flask command. You have already seen flask run, which is a sub-command that is native to Flask. The flask db sub-command is added by Flask-Migrate 
# to manage everything related to database migrations. So let's create the migration repository for microblog by running flask db init :
# (venv) $ flask db init


# The First Database Migration
# With the migration repository in place, it is time to create the first database migration, which will include the users table that maps to the User database model. 
# There are two ways to create a database migration: manually or automatically. To generate a migration automatically, Alembic compares the database schema as defined by the database models, 
# against the actual database schema currently used in the database. It then populates the migration script with the changes necessary to make the database schema match the application models. 
# In this case, since there is no previous database, the automatic migration will add the entire User model to the migration script. The flask db migrate sub-command generates these automatic migrations:
# (venv) $ flask db migrate -m "users table"

# The flask db migrate command does not make any changes to the database, it just generates the migration script. To apply the changes to the database, the flask db upgrade command must be used.
# (venv) $ flask db upgrade


# Preparing The User Model for Flask-Login
# The Flask-Login extension works with the application''s user model, and expects certain properties and methods to be implemented in it. This approach is nice, because as long as these required items 
# are added to the model, Flask-Login does not have any other requirements, so for example, it can work with user models that are based on any database system.

# The four required items are listed below:

# is_authenticated: a property that is True if the user has valid credentials or False otherwise.
# is_active: a property that is True if the user''s account is active or False otherwise.
# is_anonymous: a property that is False for regular users, and True for a special, anonymous user.
# get_id(): a method that returns a unique identifier for the user as a string (unicode, if using Python 2).
# I can implement these four easily, but since the implementations are fairly generic, Flask-Login provides a mixin class called UserMixin that includes generic implementations that are appropriate 
# for most user model classes. Here is how the mixin class is added to the model:

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5







# This is a direct translation of the association table from my diagram above. Note that I am not declaring this table as a model, like I did for the users and posts tables. Since this is an auxiliary 
# table that has no data other than the foreign keys, I created it without an associated model class.

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)




class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship('User',secondary=followers, primaryjoin=(followers.c.follower_id==id), 
    														secondaryjoin=(followers.c.followed_id==id),backref=db.backref('followers',lazy='dynamic'),lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self,password):
    	self.password_hash = generate_password_hash(password)

    def check_password(self,password):
    	return check_password_hash(self.password_hash,password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size) 

    def follow(self,user):
    	if not self.is_following(user):
    		self.followed.append(user)

    def unfollow(self,user):
    	if self.is_following(user):
    		self.followed.remove(user)

    def is_following(self,user):
    	return self.followed.filter(followers.c.followed_id==user.id).count()>0

    def followed_post(self):
    	 	followed = Post.query.join(followers,followers.c.followed_id==Post.user_id).filter(followers.c.follower_id==self.id)
    	 	own = Post.query.filter_by(user_id=self.id)
    	 	return followed.union(own).order_by(Post.timestamp.desc())    	

# I'm going to implement the "follow" and "unfollow" functionality as methods in the User model. It is always best to move the application logic away from view functions and into models or other 
# auxiliary classes or modules, because as you will see later in this chapter, that makes unit testing much easier.

# The User class created above inherits from db.Model, a base class for all models from Flask-SQLAlchemy. This class defines several fields as class variables. 
# Fields are created as instances of the db.Column class, which takes the field type as an argument, plus other optional arguments that, 
# for example, allow me to indicate which fields are unique and indexed, which is important so that database searches are efficient.

# The __repr__ method tells Python how to print objects of this class, which is going to be useful for debugging. You can see the __repr__() method in action in the Python interpreter session 





# User Loader Function
# Flask-Login keeps track of the logged in user by storing its unique identifier in Flask''s user session, a storage space assigned to each user who connects to the application. Each time the logged-in 
# ser navigates to a new page, Flask-Login retrieves the ID of the user from the session, and then loads that user into memory.

# Because Flask-Login knows nothing about databases, it needs the application''s help in loading a user. For that reason, the extension expects that the application will configure a user loader function,
# that can be called to load a user given the ID. This function can be added in the app/models.py module:
# The user loader is registered with Flask-Login with the @login.user_loader decorator. The id that Flask-Login passes to the function as an argument is going to be a string, 
# so databases that use numeric IDs need to convert the string to integer as you see above.

@login.user_loader
def load_user(id):
	return User.query.get(int(id))







# The User class has a new posts field, that is initialized with db.relationship. This is not an actual database field, but a high-level view of the relationship between users and posts, and for 
# that reason it isnt in the database diagram. For a one-to-many relationship, a db.relationship field is normally defined on the "one" side, and is used as a convenient way to get access to the "many". 
# So for example , if I have a user stored in u, the expression u.posts will run a database query that returns all the posts written by that user. The first argument to db.relationship is the model 
# class that represents the "many" side of the relationship. This argument can be provided as a string with the class name if the model is defined later in the module. The backref argument defines 
# the name of a field that will be added to the objects of the "many" class that points back at the "one" object. This will add a post.author expression that will return the user given a post. 
# The lazy argument defines how the database query for the relationship will be issued, which is something that I will discuss later. Don't worry if these details don't make much sense just yet, 
# I will show you examples of this at the end of this article.

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)



# The timestamp field is going to be indexed, which is useful if you want to retrieve posts in chronological order. I have also added a default argument, and passed the datetime.utcnow function. 
# When you pass a function as a default, SQLAlchemy will set the field to the value of calling that function (note that I did not include the () after utcnow, so Im passing the function itself, and not 
# the result of calling it). In general, you will want to work with UTC dates and times in a server application. This ensures that you are using uniform timestamps regardless of where the users are located.
# These timestamps will be converted to the users local time when they are displayed.

# The user_id field was initialized as a foreign key to user.id, which means that it references an id value from the users table. In this reference the user part is the name of the database table 
# for the model. It is an unfortunate inconsistency that in some instances such as in a db.relationship() call, the model is referenced by the model class, which typically starts with an uppercase 
# character, while in other cases such as this db.ForeignKey() declaration, a model is given by its database table name, for which SQLAlchemy automatically uses lowercase characters and, for 
# multi-word model names, snake case.


# But with database migration support, after you modify the models in your application you generate a new migration script (flask db migrate), you probably review it to make sure the 
# automatic generation did the right thing, and then apply the changes to your development database (flask db upgrade). You will add the migration script to source control and commit it.
# When you are ready to release the new version of the application to your production server, all you need to do is grab the updated version of your application, which will include the new migration
# script, and run flask db upgrade. Alembic will detect that the production database is not updated to the latest revision of the schema, and run all the new migration scripts that were created after 
# the previous release.

# (venv) $ flask db migrate -m "posts table"
# (venv) $ flask db upgrade

# Play Time
# >>> from app import db
# >>> from app.models import User, Post
# Start by creating a new user:

# >>> u = User(username='john', email='john@example.com')
# >>> db.session.add(u)
# >>> db.session.commit()

# Changes to a database are done in the context of a session, which can be accessed as db.session. Multiple changes can be accumulated in a session and once all the changes have been 
# registered you can issue a single db.session.commit(), which writes all the changes atomically. If at any time while working on a session there is an error, a call to db.session.rollback() will 
# abort the session and remove any changes stored in it. The important thing to remember is that changes are only written to the database when db.session.commit() is called. Sessions guarantee that 
# the database will never be left in an inconsistent state.


# I hope you realize how useful it is to work with a migration framework. Any users that were in the database are still there, the migration framework surgically applies the changes in 
# the migration script without destroying any data.


