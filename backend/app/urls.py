from django.urls import path, include

from app.views import UserRegistrationAPIView, BookListCreateApiView, BookRetrieveUpdateApiView, OwnUser

user_urls = [
    path('create_user/', UserRegistrationAPIView.as_view(), name='create-user'),
    path('own/', OwnUser.as_view(), name='own'),
]

book_urls = [
    path('', BookListCreateApiView.as_view(), name='books-all'),
    path('create_book/', BookListCreateApiView.as_view(), name='create-book'),
    path('<int:pk>/', BookRetrieveUpdateApiView.as_view(), name='book'),
    path('<int:pk>/', BookRetrieveUpdateApiView.as_view(), name='update_book'),
]

urlpatterns = [
    path('users/', include(user_urls)),
    path('books/', include(book_urls)),
]
