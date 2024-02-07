import requests
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework import generics, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from app.models import Book, User
from app.serializers import UserCreateSerializer, BookSerializer, UserSerializer


class UserRegistrationAPIView(generics.CreateAPIView):
    """
    Class for registrations of users. Allowed for any user
    """

    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)


class OwnUser(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        user_id = request.user.id
        user = User.objects.filter(id=user_id).prefetch_related('books').first()
        serializer = self.get_serializer(user)

        return Response({'user': serializer.data})


class Login(LoginView):
    def dispatch(self, request, *args, **kwargs):
        query_dict = request.POST.copy()
        query_dict['next'] = '/api/v1/users/own'
        request.POST = query_dict
        return LoginView.as_view(template_name=self.template_name)(request)


class Logout(LogoutView):
    next_page = '/auth/api/v1/login/'

    def dispatch(self, request, *args, **kwargs):
        query_dict = request.GET.copy()
        query_dict['next'] = '/auth/api/v1/login/'
        request.POST = query_dict
        return LogoutView.as_view(next_page='/auth/api/v1/login/')(request)


class BookListCreateApiView(generics.CreateAPIView, generics.ListAPIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    serializer_class = BookSerializer
    permission_classes = (IsAuthenticated, )
    queryset = Book.objects.all().select_related('author')

    def post(self, request, *args, **kwargs):
        some_response = requests.get('https://www.onliner.by')
        if some_response.status_code != 200:
            return Response({'message': 'Can not create book. Invalid url'}, status=status.HTTP_400_BAD_REQUEST)
        book = super().post(request, args, kwargs)
        return book


class BookRetrieveUpdateApiView(generics.RetrieveUpdateAPIView):

    serializer_class = BookSerializer
    queryset = Book.objects.all().select_related('author')
    permission_classes = (IsAuthenticated, )

    def put(self, request, *args, **kwargs):
        user_id = request.user.id
        instance = self.get_object()
        if instance.author.id == user_id:
            updated = super().patch(request, args, kwargs)
            return updated
        return Response({'message': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
