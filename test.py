import unittest
from datetime import datetime, timedelta
from app import app,db
from app.models import User,Post 


# While I don't consider the followers implementation I have built a "complex" feature, I think it is also not trivial. My concern when I write non-trivial code, is to ensure that this code will continue
# to work in the future, as I make modifications on different parts of the application. The best way to ensure that code you have already written continues to work in the future is to create a suite of 
# automated tests that you can re-run each time changes are made.



class UserModelCase(unittest.TestCase):
	def setUp(self):
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_password_hashing(self):
		u = User(username='anm')
		u.set_password('qwe')
		self.assertFalse(u.check_password('asd'))
		self.assertTrue(u.check_password('qwe'))

	def test_avatar(self):
		u = User(username='john',email='john@gmail.com')
		self.assertEqual(u.avatar(128),('https://www.gravatar.com/avatar/1f9d9a9efc2f523b2f09629444632b5c?d=identicon&s=128'))


	def test_follow(self):
		u1 = User(username='sher3',email='sher2@gmail.com')
		
		u2 = User(username='john3',email='john2@gmail.com')
		db.session.add(u1)
		
		db.session.add(u2)
		# db.session.commit()
		self.assertEqual(u1.followed.all(),[])
		self.assertEqual(u2.followers.all(),[])

		u1.follow(u2)
		db.session.commit()
		self.assertTrue(u1.is_following(u2))
		self.assertEqual(u1.followed.count(),1)
		self.assertEqual(u1.followed.first().username,'john3')
		self.assertEqual(u2.followers.count(),1)
		self.assertEqual(u2.followers.first().username,'sher3')

		u1.unfollow(u2)
		db.session.commit()
		self.assertFalse(u1.is_following(u2))
		self.assertEqual(u1.followed.count(),0)
		self.assertEqual(u2.followers.count(),0)

	def test_follow_post(self):
		u1 = User(username='john4', email='john1@example.com')
		u2 = User(username='susan4', email='susan1@example.com')
		u3 = User(username='mary4', email='mary1@example.com')
		u4 = User(username='david4', email='david1@example.com')
		db.session.add_all([u1, u2, u3, u4])

		now = datetime.utcnow()

		p1 = Post(body='Post from john',author=u1,timestamp=now + timedelta(seconds = 1))
		p2 = Post(body='Post from susan',author=u2,timestamp=now + timedelta(seconds = 3))
		p3 = Post(body='Post from mary',author=u3,timestamp=now + timedelta(seconds = 6))
		p4 = Post(body='Post from david',author=u4,timestamp=now + timedelta(seconds = 9))

		db.session.add_all([p1,p2,p3,p4])
		db.session.commit()

		u1.follow(u2)
		u1.follow(u4)
		u2.follow(u3)
		u3.follow(u4)
		db.session.commit()

		f1 = u1.followed_post().all()
		f2 = u2.followed_post().all()
		f3 = u3.followed_post().all()
		f4 = u4.followed_post().all()

		self.assertEqual(f1,[p4,p2,p1])
		self.assertEqual(f2,[p3,p2])
		self.assertEqual(f3,[p4,p3])
		self.assertEqual(f4,[p4])


if __name__ == '__main__':
	unittest.main(verbosity=2)



# I have added four tests that exercise the password hashing, user avatar and followers functionality in the user model. The setUp() and tearDown() methods are special methods that the unit testing 
# framework executes before and after each test respectively. I have implemented a little hack in setUp(), to prevent the unit tests from using the regular database that I use for development. By changing 
# e application configuration to sqlite:// I get SQLAlchemy to use an in-memory SQLite database during the tests. The db.create_all() call creates all the database tables. This is a quick way to create 
# a database from scratch that is useful for testing. For development and production use I have already shown you how to create database tables through database migrations.