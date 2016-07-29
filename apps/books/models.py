from __future__ import unicode_literals
from django.db import models
import re
import bcrypt
# Create your models here.

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
class UserManager(models.Manager):
	def register(self, info):
		name = str(info['name'])
		alias = str(info['alias'])
		email = info['email']
		password = info['password']
		confirm_pw = info['confirm_pw']
		errors = []
		if len(name) < 2:
			errors.append('You name is too short! Please put more than 2 characters!')
		elif len(name) > 100:
			errors.append('You name is too long! Please keep it under 100 characters!')
		elif str.isalpha(str(info['name'].replace(' ', ''))) != True:
			errors.append('Your name should only contain alphabets!')
		if len(alias) < 2:
			errors.append('Your alias is too short! Please put more than 2 characters!')
		elif len(alias) > 100:
			errors.append('You alias is too long! Please keep it under 100 characters!')
		elif str.isalpha(alias) != True:
			errors.append('Your alias name should only contain alphabets! No spaces or symbols')
		if len(email) < 1:
			errors.append('Email cannot be blank!')
			# if email doesn't match regular expression,
			# display an invlaid email address message.
		elif not EMAIL_REGEX.match(email):
			errors.append('Invalid Email Address!')
		try:
			if User.objects.get(email=email):
				errors.append('Same email already exist!')
		except:
			pass
		if len(password) < 8:
			errors.append('Password should be longer than 8 characters!')
		elif password != confirm_pw:
			errors.append('Your password does not match the confirmed password!')

		if errors:
			return (False, errors)
		else:
			hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
			User.objects.create(name = name, alias = alias, email = email, password = hashed_pw)
			user = User.objects.get(email=email)
			return (True, 'Successfully registered! <3', user.id)

	def login(self, info):
		errors = []
		email = info['email']
		password = info['password']
		try:
			user = User.objects.get(email=email)
			if bcrypt.hashpw(password.encode(), user.password.encode()) != user.password:
				errors.append('Your password is probably wrong.')
		except:
			errors.append('Not existing email. Please register!')

		if errors:
			return (False, errors)
		else:
			return (True, 'Successfully logged in! <3' , user.id)

	def user_info(self, user_id):
		data_1 = User.objects.raw("SELECT books_user.id, books_user.alias, books_user.name, books_user.email, COUNT(books_review.user_id) AS 'total_reviews' FROM books_user JOIN books_review ON books_user.id = books_review.user_id WHERE books_review.user_id = {} GROUP BY books_user.id".format(user_id))

		data_2 = Review.objects.raw("SELECT books_review.id, books_review.book_id, books_book.title FROM books_review JOIN books_book ON books_review.book_id = books_book.id WHERE books_review.user_id = {} GROUP BY books_book.title".format(user_id))

		return (data_1, data_2)

class reviewManager(models.Manager):
	def reviews_per_book(self, book_id):
		data_1 = Book.objects.get(id=book_id)
		data_2 = Review.objects.raw("SELECT books_review.id, books_review.rating, books_user.alias, books_review.user_id, books_review.created_at, books_review.description FROM books_review JOIN books_user ON books_review.user_id = books_user.id WHERE books_review.book_id = {} ORDER BY books_review.created_at DESC".format(book_id))
		return (data_1, data_2)

	def add_review(self, data, book_id, user_id):
		description = str(data['description'])
		rating = int(data['rating'])
		errors = []
		if len(description) < 30:
			errors.append('Your review for the book seems too short. Please write a decent review! (at least 30 characters long! but fewer than 700 characters!)')
		elif len(description) > 700:
			errors.append('Your review is too long! Please kee it under 700 characters!')

		if errors:
			return (False, errors)
		else:
			Review.objects.create(description = description, rating = rating, user_id= user_id, book_id = book_id)
			return (True, "Successfully added a new review to this book!")

class bookManager(models.Manager):
	def add_book(self, data, user_id):
		title = str(data['title'])
		if data['author_new']:
			author = str(data['author_new'])
		else:
			author = str(data['author_list'])
		author_temp = author # for isalpha test later on
		description = str(data['description'])
		rating = int(data['rating'])

		errors = []

		if len(title) < 1:
			errors.append('Please add a title of the book!')
		elif len(title) > 100:
			errors.append('Title of the book seems too long. Please keep it under 100 characters!')
		if len(author) < 2:
			errors.append('Author of the book seems too short. Please write full name of the author!')
		elif len(author) > 100:
			errors.append('Author of the book seems too long. Please keep it under 100 characters!')
		elif str.isalpha(str(author_temp.replace(' ', ''))) != True:
			errors.append('Author of the book cannot contain symbols or numbers!')
		try:
			if Book.objects.get(title=title):
				errors.append('Same title already exist! Go to the page with the same title and leave your review there!')
		except:
			pass
		if len(description) < 30:
			errors.append('Your review for the book seems too short. Please write a decent review! (at least 30 characters long! but fewer than 700 characters!)')
		elif len(description) > 700:
			errors.append('Your review is too long! Please kee it under 700 characters!')

		if errors:
			return (False, errors)
		else:
			Book.objects.create(title = title, author = author)
			book = Book.objects.get(title = title)
			Review.objects.create(description = description, rating = rating, user_id= user_id, book_id = book.id)
			return (True, 'Successfully added a new book and its review!', book.id)

	def all_books(self):
		data_1 = Book.objects.raw("SELECT books_book.id, books_book.title, books_review.rating, books_review.user_id, books_user.alias, books_review.description, books_review.created_at FROM books_book JOIN books_review ON books_book.id = books_review.book_id JOIN books_user ON books_review.user_id = books_user.id ORDER BY books_review.created_at DESC LIMIT 3")

		data_2 = Book.objects.raw("SELECT books_book.id, books_book.title FROM books_book ORDER BY books_book.title")

		return (data_1, data_2)

	def get_authors(self):
		data = Book.objects.raw("SELECT books_book.id, books_book.author FROM books_book GROUP BY books_book.author")
		return data

class User(models.Model):
	name = models.CharField(max_length=100)
	alias = models.CharField(max_length=100)
	email = models.EmailField()
	password = models.CharField(max_length=255) # hashed password
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	# *************************
	# Connect an instance of UserManager to our User model!
	userManager = UserManager()
	# Re-adds objects as a manager (so all the normal ORM literature matches)
	objects = models.Manager()
	# *************************

class Book(models.Model):
	title = models.CharField(max_length=100)
	author = models.CharField(max_length=100)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	bookManager = bookManager()
	# Re-adds objects as a manager (so all the normal ORM literature matches)
	objects = models.Manager()

class Review(models.Model):
	rating = models.IntegerField()
	description = models.TextField(max_length=700)
	user = models.ForeignKey(User)
	book = models.ForeignKey(Book)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	reviewManager = reviewManager()
	# Re-adds objects as a manager (so all the normal ORM literature matches)
	objects = models.Manager()
