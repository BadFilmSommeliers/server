from rest_framework import serializers
from django.contrib.auth import get_user_model
from movies.serializers import (
    MovieSerializer,
    ReviewListSerializer, 
    ReviewCommentSerializer, 
    CollectionListSerializer, 
    CollectionCommentSerializer,
    BookmarkSerializer
    )
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    like_movies = MovieSerializer(many=True, read_only=True)

    review_set = ReviewListSerializer(many=True, read_only=True)
    like_reviews = ReviewListSerializer(many=True, read_only=True)

    reviewcomment_set = ReviewCommentSerializer(many=True, read_only=True)

    collection_set = CollectionListSerializer(many=True, read_only=True)
    like_collections = CollectionListSerializer(many=True, read_only=True)

    collectioncomment_set = CollectionCommentSerializer(many=True, read_only=True)

    bookmark_set = BookmarkSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            'pk', 'username', 'password', 'nickname', 'like_movies',
            'review_set', 'reviewcomment_set', 'collection_set',
            'collectioncomment_set', 'is_b_lover', 'is_hipster',
            'genre_preference',  'watched_movies_dict',
            'like_reviews', 'like_collections', 'bookmark_set'
            )
        read_only_fields = ('genre_preference', 'watched_movies_dict',) 

        

class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    oldPassword = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ('oldPassword', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def validate_oldPassword(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"oldPassword": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data['password'])
        instance.save()

        return instance