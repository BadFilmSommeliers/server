from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Movie, Review, ReviewComment, Collection, CollectionComment, Bookmark


class MovieSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(
        source = 'like_users.count',
        read_only = True
    )
    bookmark_count = serializers.IntegerField(
        source = 'bookmark_set.count',
        read_only = True
    )

    class Meta:
        model = Movie
        fields = ('pk', 'title', 'poster_path', 'like_users', 'like_count', 'bookmark_count')
        read_only_fields = ('title', 'poster_path', 'like_users', 'bookmark_count')


class ReviewCommentSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(
        source = 'like_users.count',
        read_only = True
    )
    
    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = get_user_model()
            fields = ('pk', 'username', 'nickname')

    user = UserSerializer(read_only=True)

    class Meta:
        model = ReviewComment
        fields = ('pk', 'user', 'review', 'content', 'like_count', 'created_at', 'updated_at',)
        read_only_fields = ('user', 'review',)


class ReviewListSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(
        source = 'like_users.count',
        read_only = True
    )
    comment_count = serializers.IntegerField(
        source = 'reviewcomment_set.count',
        read_only = True
    )

    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = get_user_model()
            fields = ('pk', 'username', 'nickname')

    user = UserSerializer(read_only=True)
    reviewcomment_set = ReviewCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Review
        fields = ('pk', 'content', 'user', 'movie', 'rating', 'like_count', 'created_at', 'updated_at', 'reviewcomment_set', 'comment_count')


class ReviewSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(
        source = 'like_users.count',
        read_only = True
    )
    comment_count = serializers.IntegerField(
        source = 'reviewcomment_set.count',
        read_only = True
    )

    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = get_user_model()
            fields = ('pk', 'username', 'nickname')

    user = UserSerializer(read_only=True)
    reviewcomment_set = ReviewCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = ('pk', 'user', 'like_users', 'movie', 'content', 'rating', 'like_count', 'reviewcomment_set', 'comment_count', 'created_at', 'updated_at')
        read_only_fields = ('user', 'movie', 'like_users', )


class CollectionListSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(
        source = 'like_users.count',
        read_only = True
    )
    comment_count = serializers.IntegerField(
        source = 'collectioncomment_set.count',
        read_only=True
    )

    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = get_user_model()
            fields = ('pk', 'username', 'nickname')

    user = UserSerializer(read_only=True)

    class Meta:
        model = Collection
        fields = ('pk', 'user', 'title', 'content', 'like_users', 'like_count', 'comment_count', 'movies', 'created_at', 'updated_at',)
        read_only_fields = ('user',)



class CollectionCommentSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(
        source = 'like_users.count',
        read_only = True
    )

    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = get_user_model()
            fields = ('pk', 'username', 'nickname')

    user = UserSerializer(read_only=True)

    class Meta:
        model = CollectionComment
        fields = ('pk', 'user', 'content', 'like_count', 'like_users', 'created_at', 'updated_at',)
        read_only_fields = ('user', 'collection', 'like_users', 'created_at', 'updated_at',)


class CollectionSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(
        source = 'like_users.count',
        read_only = True
    )
    comment_count = serializers.IntegerField(
        source = 'collectioncomment_set.count',
        read_only = True
    )

    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = get_user_model()
            fields = ('pk', 'username', 'nickname')

    user = UserSerializer(read_only=True)
    movie_pks = serializers.ListField(write_only=True)
    collectioncomment_set = CollectionCommentSerializer(many=True, read_only=True)

    def create(self, validated_data):
        movie_pks = validated_data.pop('movie_pks')
        collection = Collection.objects.create(**validated_data)
        for movie_pk in movie_pks:
            collection.movies.add(movie_pk)
        return collection

    def update(self, collection, validated_data):
        movie_pks = validated_data.pop('movie_pks')
        for attr, value in validated_data.items():
            setattr(collection, attr, value)
            collection.save()
        collection.movies.clear()
        for movie_pk in movie_pks:
            collection.movies.add(movie_pk)
        return collection

    class Meta:
        model = Collection
        fields = ('pk', 'title', 'user', 'content', 'movies', 'like_users', 'movie_pks', 'like_count', 'comment_count' ,'collectioncomment_set', 'created_at', 'updated_at',)
        read_only_fields = ('like_users', 'movies', 'user',)


class UserLikeMovieSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = get_user_model()
        fields = ('pk', 'username', 'nickname', 'like_movies')
        read_only_fields = ('pk', 'username', 'nickname', 'like_movies')


class BookmarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bookmark
        fields = ('pk', 'user', 'movie', 'content', 'created_at', 'updated_at')
        read_only_fields = ('user', 'movie', )
