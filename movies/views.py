from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Bookmark, Movie, Review, ReviewComment, Collection, CollectionComment   
from .serializers import (
    CollectionCommentSerializer, 
    ReviewListSerializer, 
    ReviewSerializer, 
    ReviewCommentSerializer, 
    CollectionListSerializer, 
    CollectionSerializer,
    MovieSerializer,
    BookmarkSerializer
    )
import tmdbsimple as tmdb


tmdb.API_KEY = 'YOUR_API_KEY_HERE'


@api_view(['GET'])
@permission_classes([AllowAny])
def movie_detail(request, movie_pk):
    if not Movie.objects.filter(pk=movie_pk):
        tmdb_movie_info = tmdb.Movies(movie_pk).info(language='ko')
        title = tmdb_movie_info['title']
        poster_path = tmdb_movie_info['poster_path']

        movie, created = Movie.objects.get_or_create(
            pk=movie_pk, 
            title=title, 
            poster_path = poster_path
            )
    else:
        movie = Movie.objects.get(pk=movie_pk)

    reviews = Review.objects.filter(movie_id=movie_pk).all()
    reviews_serializer = ReviewListSerializer(reviews, many=True)
    movie_serializer = MovieSerializer(movie)

    movie_info = {
        'pk': movie_pk,
        'reviews': reviews_serializer.data,
        'movie_serializer': movie_serializer.data
    }
    return JsonResponse(movie_info)


@api_view(['GET'])
@permission_classes([AllowAny])
def review_list(request):
    reviews = Review.objects.all().order_by('-created_at')
    serializer = ReviewListSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def user_review(request, movie_pk, user_pk):
    '''
    해당 유저가 작성한 해당 영화의 리뷰 반환
    '''
    user = get_object_or_404(get_user_model(), pk=user_pk)
    if user.review_set.filter(movie=movie_pk).exists():
        user_review = user.review_set.get(movie=movie_pk)
        serializer = ReviewListSerializer(user_review)
        return Response(serializer.data)
    return Response(None)



@api_view(['GET'])
def user_reviews(request, user_pk):
    '''
    해당 유저가 작성한 모든 리뷰 반환
    '''
    reviews = Review.objects.filter(user_id=user_pk).annotate(comment_count=Count('reviewcomment'))
    serializer = ReviewListSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def review_create(request, movie_pk):
    movie_title = request.data['movie_title']
    poster_path = request.data['poster_path']
    genre_list = request.data['genre_list']

    movie, created = Movie.objects.get_or_create(
        pk=movie_pk,
        title=movie_title,
        poster_path = poster_path
        )
    
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        rating = request.data['rating']
        user = get_object_or_404(get_user_model(), pk=request.user.pk)
        user.add_movie_to_watched(movie_pk = movie_pk)
        user.add_movie_to_genre_preference(movie_pk = movie_pk, genre_list = genre_list, star_rating = rating)
        user.save()

        serializer.save(user=request.user, movie=movie)
        return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def review_detail(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)

    if request.method == 'GET':
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    if request.method == 'PUT':
        original_rating = review.rating 
        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid(raise_exception=True):
            updated_rating = request.data['rating']
            if original_rating != updated_rating:
                user = get_object_or_404(get_user_model(), pk=request.user.pk)
                user.update_movie_to_genre_preference(
                    movie_pk = review.movie.pk,
                    genre_list = request.data['genre_list'],
                    original_rating = original_rating,
                    updated_rating = updated_rating,
                    )
                user.save()
            serializer.save()
            return Response(serializer.data)
    
    if request.method == 'DELETE':
        user = get_object_or_404(get_user_model(), pk=request.user.pk)
        user.delete_movie_from_watched(movie_pk = review.movie.pk)
        user.delete_movie_from_genre_preference(
            movie_pk = review.movie.pk, 
            genre_list = request.data['genre_list'], 
            star_rating = review.rating
            )
        user.save()

        review.delete()
        data = {
            'delete': f'{review_pk}번 리뷰가 삭제되었습니다.'
        }
        return Response(data, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def review_comment_list_create(request, review_pk):
    if request.method == 'GET':
        review_comments = ReviewComment.objects.filter(review_id=review_pk)
        serializer = ReviewCommentSerializer(review_comments, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        review = get_object_or_404(Review, pk=review_pk)

        serializer = ReviewCommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user, review=review)
            return Response(serializer.data)


@api_view(['PUT', 'DELETE'])
def review_comment_detail(request, comment_pk):
    comment = get_object_or_404(ReviewComment, pk=comment_pk)

    if not request.user.reviewcomment_set.filter(pk=comment_pk).exists():
        return Response({'detail': '권한이 없습니다'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = ReviewCommentSerializer(comment, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    
    if request.method == 'DELETE':
        comment.delete()
        data = {
            'delete': f'{comment_pk}번 리뷰 코멘트가 삭제되었습니다.'
        }
        return Response(data, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def collection_list_create(request):
    if request.method == 'GET':
        collections = Collection.objects.all()
        serializer = CollectionListSerializer(collections, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        print('creating collection')
        movie_infos = request.data.pop('movie_infos')
        if not movie_infos:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        movie_pks = []
        for movie_pk, poster_path, title in movie_infos:
            movie_pks.append(movie_pk)
            movie = Movie.objects.get_or_create(pk=movie_pk, title=title, poster_path = poster_path)
        request.data['movie_pks'] = movie_pks

        serializer = CollectionSerializer(data=request.data)
        user = get_object_or_404(get_user_model(), pk=request.user.pk)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=user)
            return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def collection_detail(request, collection_pk):
    collection = get_object_or_404(Collection, pk=collection_pk)

    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)

    if collection.user != request.user:
        return Response({'detail': '권한이 없습니다'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    
    if request.method == 'DELETE':
        collection.delete()
        data = {
            'delete': f'{collection_pk}번 컬렉션이 삭제되었습니다.'
        }
        return Response(data, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def collection_comment_list_create(request, collection_pk):
    if request.method == 'GET':
        collection_comments = CollectionComment.objects.filter(collection_id=collection_pk)
        serializer = CollectionCommentSerializer(collection_comments, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        collection = get_object_or_404(Collection, pk=collection_pk)
        user = get_object_or_404(get_user_model(), pk=request.user.pk)
        serializer = CollectionCommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=user, collection=collection)
            return Response(serializer.data)


@api_view(['PUT', 'DELETE'])
def collection_comment_detail(request, comment_pk):
    collection_comment = get_object_or_404(CollectionComment, pk=comment_pk)
    
    if collection_comment.user != request.user:
        return Response({'detail': '권한이 없습니다'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = CollectionCommentSerializer(collection_comment, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    
    if request.method == 'DELETE':
        collection_comment.delete()
        data = {
            'delete': f'{comment_pk}번 컬렉션 코멘트가 삭제되었습니다.'
        }
        return Response(data, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def movie_like(request, movie_pk):
    user = get_object_or_404(get_user_model(), pk=request.user.pk)

    title = request.data['title']
    poster_path = request.data['poster_path']
    movie, created = Movie.objects.get_or_create(
        pk=movie_pk,
        title=title,
        poster_path = poster_path)

    genre_list = request.data['movie_genre']

    if movie.like_users.filter(pk=request.user.pk).exists(): 
        movie.like_users.remove(request.user)  # 좋아요 취소
        user.delete_movie_from_genre_preference(movie_pk = movie_pk, genre_list = genre_list)
        user.delete_movie_from_watched(movie_pk = movie_pk)
        user.save()

        data = {
            'like': False,
            'like_count': movie.like_users.count()
        }
    else:
        movie.like_users.add(request.user)  # 좋아요 하기
        user.add_movie_to_genre_preference(movie_pk = movie_pk, genre_list = genre_list)
        user.add_movie_to_watched(movie_pk = movie_pk)
        user.save()

        data = {
            'like': True,
            'like_count': movie.like_users.count()
        }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def movie_like_only(request, movie_pk):
    genre_list = request.data['genre_list']
    movie_title = request.data['title']
    movie_poster_path = request.data['poster_path']
    movie_pk = request.data['pk']

    movie, created = Movie.objects.get_or_create(
        pk=movie_pk, 
        title=movie_title, 
        poster_path = movie_poster_path)

    if movie.like_users.filter(pk=request.user.pk).exists(): 
        pass
    else:
        movie.like_users.add(request.user)  # 좋아요 하기
        user = get_object_or_404(get_user_model(), pk=request.user.pk)
        user.add_movie_to_genre_preference(movie_pk = movie_pk, genre_list = genre_list)
        user.add_movie_to_watched(movie_pk = movie_pk)
        user.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def review_like(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)

    if review.like_users.filter(pk=request.user.pk).exists(): 
        review.like_users.remove(request.user)  # 좋아요 취소
        data = {
            'like': False,
            'like_count': review.like_users.count()
        }
    else:
        review.like_users.add(request.user)  # 좋아요 하기
        data = {
            'like': True,
            'like_count': review.like_users.count()
        }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def collection_like(request, collection_pk):
    collection = get_object_or_404(Collection, pk=collection_pk)

    if collection.like_users.filter(pk=request.user.pk).exists(): 
        collection.like_users.remove(request.user)  # 좋아요 취소
        data = {
            'like': False,
            'like_count': collection.like_users.count()
        }
    else:
        collection.like_users.add(request.user)  # 좋아요 하기
        data = {
            'like': True,
            'like_count': collection.like_users.count()
        }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def collection_comment_like(request, comment_pk):

    collection_comment = get_object_or_404(CollectionComment, pk=comment_pk)

    if collection_comment.like_users.filter(pk=request.user.pk).exists(): 
        collection_comment.like_users.remove(request.user)  # 좋아요 취소
        data = {
            'like': False,
            'like_count': collection_comment.like_users.count()
        }
    else:
        collection_comment.like_users.add(request.user)  # 좋아요 하기
        data = {
            'like': True,
            'like_count': collection_comment.like_users.count()
        }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def search(request):
    keyword = request.GET.get('keyword')

    reviews = Review.objects.filter(content__icontains=keyword)
    review_serializer = ReviewListSerializer(reviews, many=True)

    collections = Collection.objects.filter(
        Q(title__icontains=keyword) | Q(content__icontains=keyword)
    )
    collection_serializer = CollectionListSerializer(collections, many=True)

    search_results = {
        'review_serializer': review_serializer.data,
        'collection_serializer': collection_serializer.data
    }
    return JsonResponse(search_results)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def bookmark_create(request, movie_pk):
    if request.method == 'GET':
        if Bookmark.objects.filter(movie_id=movie_pk).filter(user_id=request.user.pk).exists():
            bookmark = Bookmark.objects.filter(movie_id=movie_pk).filter(user_id=request.user.pk).get()
            serializer = BookmarkSerializer(instance=bookmark)
            return Response(serializer.data)
        return Response(False)

    if request.method == 'POST':
        movie = get_object_or_404(Movie, pk=movie_pk)
        serializer = BookmarkSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user, movie=movie)
            return Response(serializer.data)

    if request.method == 'PUT':
        bookmark = Bookmark.objects.filter(movie_id=movie_pk).filter(user_id=request.user.pk).get()
        serializer = BookmarkSerializer(bookmark, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    if request.method == 'DELETE':
        bookmark = Bookmark.objects.filter(movie_id=movie_pk).filter(user_id=request.user.pk).get()
        bookmark.delete()
        data = {
            'delete': '북마크가 삭제되었습니다.'
        }
        return Response(data, status=status.HTTP_204_NO_CONTENT)
