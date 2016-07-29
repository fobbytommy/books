from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^logout$', views.logout, name="logout"),
    url(r'^books/add$', views.add_books, name="add_books"),
	url(r'^process/(?P<process>\w+)$', views.process_user, name="process_user"),
    url(r'^books$', views.show_books, name="show_books"),
    url(r'^books/(?P<book_id>\d+)$', views.show_reviews_per_book, name="show_reviews_per_book"),
	url(r'^add/review/(?P<book_id>\d+)$', views.add_review, name="add_review"),
	url(r'^users/(?P<user_id>\d+)$', views.show_user, name="show_user"),
    url(r'^delete/(?P<book_id>\d+)/(?P<review_id>\d+)$', views.delete_review, name="delete_review")
]
