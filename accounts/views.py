from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from random import choices
from .serializers import UserSerializer, ChangePasswordSerializer


@api_view(['GET'])
def get_user(request):
    user = get_object_or_404(get_user_model(), pk=request.user.pk)
    user_serializer = UserSerializer(user)
    return Response(user_serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    password = request.data.get('password')
    password_confirmation = request.data.get('passwordConfirmation')
		
    if password != password_confirmation:
        return Response({'error': '비밀번호가 일치하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
		
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        user.set_password(request.data.get('password'))
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def profile(request, user_pk):
    user = get_object_or_404(get_user_model(), pk=user_pk)
    if request.method == 'GET':
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data)

    if request.method == 'PUT':
        nickname = request.data.get('nickname')

        if get_user_model().objects.filter(nickname=nickname).exists():
            return Response({'error': '이미 존재하는 닉네임입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    if request.method == 'DELETE':
        user.delete()
        data = {
            'delete': f'{user_pk}번 계정이 삭제되었습니다.'
        }
        return Response(data, status=status.HTTP_200_OK)


class ChangePasswordView(generics.UpdateAPIView):
    """
    다음 링크를 참고하였음
    https://medium.com/django-rest/django-rest-framework-change-password-and-update-profile-1db0c144c0a3
    """
    queryset = get_user_model().objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    
@api_view(['GET'])
def get_base_info_for_rec(request):
    user = get_object_or_404(get_user_model(), pk=request.user.pk)
    user_serializer = UserSerializer(user)
    liked_movies_picked = choices(user_serializer.data['like_movies'],k=3)
    
    liked_movie_pks = []
    for movie in liked_movies_picked:
        liked_movie_pks.append(movie['pk'])

    data = {
        'is_b_lover': user.is_b_lover,
        'is_hipster': user.is_hipster,
        'genre_preference': user.genre_preference,
        'watched_movies': user.watched_movies_dict,
        'liked_movies': liked_movie_pks
    }
    return Response(data)