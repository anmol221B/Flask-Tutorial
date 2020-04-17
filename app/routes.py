from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm,RegistrationForm,EditProfileForm
from werkzeug.urls import url_parse

from flask_login import current_user, login_user, login_required, logout_user
from app.models import User

from datetime import datetime

@app.route('/')
@app.route('/index')
@login_required
def index():
	return render_template('index.html', title='Home Page')


@app.route('/login' , methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form  = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('invalid username or password')
			return redirect(url_for('login'))
		login_user(user,remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html' , title = 'Sign In',form=form)

# The first new thing in this version is the methods argument in the route decorator. This tells Flask that this view function accepts GET and POST requests, overriding the default, 
# which is to accept only GET requests. The HTTP protocol states that GET requests are those that return information to the client (the web browser in this case). 
# All the requests in the application so far are of this type. POST requests are typically used when the browser submits form data to the server (in reality GET requests can also be used for this purpose,
# but it is not a recommended practice). The "Method Not Allowed" error that the browser showed you before, appears because the browser tried to send a POST request and the application was not configured
# to accept it. By providing the methods argument, you are telling Flask which request methods should be accepted.

# The form.validate_on_submit() method does all the form processing work. When the browser sends the GET request to receive the web page with the form, this method is going to return False, 
# so in that case the function skips the if statement and goes directly to render the template in the last line of the function.

# When form.validate_on_submit() returns True, the login view function calls two new functions, imported from Flask. The flash() function is a useful way to show a message to the user. 
# A lot of applications use this technique to let the user know if some action has been successful or not. In this case, I m going to use this mechanism as a temporary solution, because I don t 
# have all the infrastructure necessary to log users in for real yet. The best I can do for now is show a message that confirms that the application received the credentials.

# The second new function used in the login view function is redirect(). This function instructs the client web browser to automatically navigate to a different page, given as an argument. 
# This view function uses it to redirect the user to the index page of the application.

# When you call the flash() function, Flask stores the message, but flashed messages will not magically appear in web pages. The templates of the application need to render these flashed messages
#  in a way that works for the site layout. I'm going to add these messages to the base template, so that all the templates inherit this functionality. 


# The top two lines in the login() function deal with a weird situation. Imagine you have a user that is logged in, and the user navigates to the /login URL of your application. Clearly that is a mistake, 
# I want to not allow that. The current_user variable comes from Flask-Login and can be used at any time during the handling to obtain the user object that represents the client of the request. 
# The value of this variable can be a user object from the database (which Flask-Login reads through the user loader callback I provided above), or a special anonymous user object if the user did not 
# log in yet. Remember those properties that Flask-Login required in the user object? One of those was is_authenticated, which comes in handy to check if the user is logged in or not. When the user is
# already logged in, I just redirect to the index page.

# In place of the flash() call that I used earlier, now I can log the user in for real. The first step is to load the user from the database. The username came with the form submission, so I can query 
# the database with that to find the user. For this purpose I'm using the filter_by() method of the SQLAlchemy query object. The result of filter_by() is a query that only includes the objects that have 
# a matching username. Since I know there is only going to be one or zero results, I complete the query by calling first(), which will return the user object if it exists, or None if it does not. 
# In Chapter 4 you have seen that when you call the all() method in a query, the query executes and you get a list of all the results that match that query. The first() method is another commonly 
# used way to execute a query, when you only need to have one result.

# If I got a match for the username that was provided, I can next check if the password that also came with the form is valid. This is done by invoking the check_password() method I defined above. 
# This will take the password hash stored with the user and determine if the password entered in the form matches the hash or not. So now I have two possible error conditions: the username can be 
# invalid, or the password can be incorrect for the user. In either of those cases, I flash a message, and redirect back to the login prompt so that the user can try again.

# If the username and password are both correct, then I call the login_user() function, which comes from Flask-Login. This function will register the user as logged in, so that means that any future pages
# the user navigates to will have the current_user variable set to that user.

# To complete the login process, I just redirect the newly logged-in user to the index page.

# What remains is to implement the redirect back from the successful login to the page the user wanted to access. When a user that is not logged in accesses a view function protected with the 
# @login_required decorator, the decorator is going to redirect to the login page, but it is going to include some extra information in this redirect so that the application can then return to the 
# first page. If the user navigates to /index, for example, the @login_required decorator will intercept the request and respond with a redirect to /login, but it will add a query string argument to 
# this URL, making the complete redirect URL /login?next=/index. The next query string argument is set to the original URL, so the application can use that to redirect back after login.

# Right after the user is logged in by calling Flask-Login's login_user() function, the value of the next query string argument is obtained. Flask provides a request variable that contains all the 
# information that the client sent with the request. In particular, the request.args attribute exposes the contents of the query string in a friendly dictionary format. There are actually three possible 
# cases that need to be considered to determine where to redirect after a successful login:

# If the login URL does not have a next argument, then the user is redirected to the index page.
# If the login URL includes a next argument that is set to a relative path (or in other words, a URL without the domain portion), then the user is redirected to that URL.
# If the login URL includes a next argument that is set to a full URL that includes a domain name, then the user is redirected to the index page.
# The first and second cases are self-explanatory. The third case is in place to make the application more secure. An attacker could insert a URL to a malicious site in the next argument, so the 
# application only redirects when the URL is relative, which ensures that the redirect stays within the same site as the application. To determine if the URL is relative or absolute, I parse it with 
# Werkzeug's url_parse() function and then check if the netloc component is set or not.



@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))



@app.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data,email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)



@app.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	post = [
		{'author':user,'body':'test1'},
		{'author':user,'body':'test2'}
	]
	return render_template('user.html',user=user,posts=post)



# The @before_request decorator from Flask register the decorated function to be executed right before the view function. This is extremely useful because now I can insert code that I want to execute
#  before any view function in the application, and I can have it in a single place. The implementation simply checks if the current_user is logged in, and in that case sets the last_seen field to the
#   current time. I mentioned this before, a server application needs to work in consistent time units, and the standard practice is to use the UTC time zone. Using the local time of the system is not
#    a good idea, because then what goes in the database is dependent on your location. The last step is to commit the database session, so that the change made above is written to the database. 
#    If you are wondering why there is no db.session.add() before the commit, consider that when you reference current_user, Flask-Login will invoke the user loader callback function, which will 
#    run a database query that will put the target user in the database session. So you can add the user again in this function, but it is not necessary because it is already there.


@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()



@app.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
	    form = EditProfileForm(current_user.username)
	    if form.validate_on_submit():
	        current_user.username = form.username.data
	        current_user.about_me = form.about_me.data
	        db.session.commit()
	        flash('Your changes have been saved.')
	        return redirect(url_for('edit_profile'))
	    elif request.method == 'GET':
	        form.username.data = current_user.username
	        form.about_me.data = current_user.about_me
	    return render_template('edit_profile.html', title='Edit Profile',form=form)



@app.route('/follow/<username>')
@login_required
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('User {} is not found.'.format(username))
		return redirect(url_for('index'))
	if user==current_user:
		flash('You cant follow yourself')
		return redirect(url_for('user',username=username))
	current_user.follow(user)
	db.session.commit()
	flash('You are now following {}'.format(username))
	return redirect(url_for('user',username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('User {} is not found.'.format(username))
		return redirect(url_for('index'))
	if user==current_user:
		flash('You cant unfollow yourself')
		return redirect(url_for('user',username=username))
	current_user.unfollow(user)
	db.session.commit()
	flash('You unfollowed {}'.format(username))
	return redirect(url_for('user',username=username))