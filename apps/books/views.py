from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from .models import User, Book, Review
# Create your views here.
def index(request):
	return render(request, 'books/index.html')

def process_user(request, process):
	if request.method == "POST":
		if process == "register":
			val_result = User.userManager.register(request.POST)
			if val_result[0] == False: # aka registration info is INVALID
				for error in val_result[1]:
					messages.error(request, error)
				return redirect(reverse('index'))
			else: # registration info is VALID (therefore, Successfully registered!)
				messages.success(request, val_result[1])
				request.session['user_id'] = val_result[2]
				request.session['status'] = True
				return redirect(reverse('show_books'))
		else: # case when 'process' == "login"
			val_result = User.userManager.login(request.POST)
			if val_result[0] == False: # aka login info is INVALID
				for error in val_result[1]:
					messages.error(request, error)
				return redirect(reverse('index'))
			else: # login info is VALID (therefore, Successfully logged in!)
				messages.success(request, val_result[1])
				request.session['user_id'] = val_result[2] # user id!
				request.session['status'] = True
				return redirect(reverse('show_books'))
	else:
		return redirect(reverse('index'))

def show_books(request):
	if 'status' in request.session:
		data = Book.bookManager.all_books()
		context = {
			'user': User.objects.get(id=request.session['user_id']),
			'reviews': data[0],
			'books': data[1]
		}
		return render(request,'books/show_books.html', context)
	else:
		messages.error(request, "You must be logged in to go to that route!")
		return redirect(reverse('index'))

def logout(request):
	if 'status' in request.session:
		if request.method == "POST":
			request.session.flush()
			messages.success(request, "You have successfully logged out!")
			return redirect(reverse('index'))
		else:
			return redirect(reverse('index'))
	else:
		messages.error(request, "You must be logged in to go to that route!")
		return redirect(reverse('index'))

def add_books(request):
	if 'status' in request.session:
		if request.method == "GET":
			authors = Book.bookManager.get_authors()
			context = {
				'authors': authors
			}
			return render(request, 'books/add_books.html', context)
		elif request.method == "POST":
			val_result = Book.bookManager.add_book(request.POST, request.session['user_id'])
			if val_result[0] == False: # aka registration info is INVALID
				for error in val_result[1]:
					messages.error(request, error)
				return redirect('/books/add')
			else: # registration info is VALID (therefore, Successfully registered!)
				messages.success(request, val_result[1])
				return redirect('/books/{}'.format(val_result[2]))
	else:
		messages.error(request, "You must be logged in to go to that route!")
		return redirect(reverse('index'))

def show_reviews_per_book(request, book_id):
	if 'status' in request.session:
		data = Review.reviewManager.reviews_per_book(book_id)
		context = {
			'book': data[0],
			'reviews': data[1]
		}
		return render(request, 'books/show_reviews_per_book.html', context)
	else:
		messages.error(request, "You must be logged in to go to that route!")
		return redirect(reverse('index'))

def add_review(request, book_id):
	if 'status' in request.session:
		if request.method == "POST":
			val_result = Review.reviewManager.add_review(request.POST, book_id, request.session['user_id'])
			if val_result[0] == False:
				for error in val_result[1]:
					messages.error(request, error)
				return redirect('/books/{}'.format(book_id))
			else:
				messages.success(request, val_result[1])
				return redirect('/books/{}'.format(book_id))
		else:
			# do nothing
			return redirect('/books/{}'.format(book_id))
	else:
		messages.error(request, "You must be logged in to go to that route!")
		return redirect(reverse('index'))

def show_user(request, user_id):
	if 'status' in request.session:
		data = User.userManager.user_info(user_id)
		context = {
			'user': data[0],
			'books': data[1]
		}
		for idx in data[0]:
			print idx.alias
			print idx.total_reviews
			print idx.name
		return render(request, 'books/show_user.html', context)
	else:
		messages.error(request, "You must be logged in to go to that route!")
		return redirect(reverse('index'))

def delete_review(request, book_id, review_id):
	if 'status' in request.session:
		if request.method == "POST":
			# delete the post
			Review.objects.get(id=review_id).delete()
			return redirect('/books/{}'.format(book_id))
		else:
			# do nothing
			return redirect('/books/{}'.format(book_id))
	else:
		messages.error(request, "You must be logged in to go to that route!")
		return redirect(reverse('index'))
