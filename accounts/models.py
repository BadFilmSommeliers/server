from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    nickname = models.CharField(max_length=150)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='interested_in')
    is_b_lover = models.BooleanField(default=True)
    is_hipster = models.BooleanField(default=False)

    genre_preference = models.JSONField(default=dict)
    watched_movies_dict = models.JSONField(default=dict)

    def add_movie_to_watched(self, movie_pk) -> None:
        movie_pk = str(movie_pk)
        if movie_pk in self.watched_movies_dict:
            self.watched_movies_dict[movie_pk] += 1
        else:
            self.watched_movies_dict[movie_pk] = 1
        return None

    def delete_movie_from_watched(self, movie_pk) -> None:
        movie_pk = str(movie_pk)
        if movie_pk in self.watched_movies_dict:
            if self.watched_movies_dict[movie_pk] == 1:
                self.watched_movies_dict.pop(movie_pk)    
            else:                  
                self.watched_movies_dict[movie_pk] -= 1
        return None

    def add_movie_to_genre_preference(self, movie_pk, genre_list, star_rating=False) -> None:
        priority = 10
        if star_rating and star_rating != 2.5:
            priority = int(star_rating - 2.5) * 4

        for genre in genre_list:
            if genre in self.genre_preference:
                self.genre_preference[genre] += priority
            else:
                self.genre_preference[genre] = priority
        return None

    def delete_movie_from_genre_preference(self, movie_pk, genre_list, star_rating=False):        
        priority = 10
        if star_rating and star_rating != 2.5:
            priority = int(star_rating - 2.5) * 4

        for genre in genre_list:
            if genre in self.genre_preference:
                self.genre_preference[genre] -= priority
            else:
                self.genre_preference[genre] = -priority
        return None

    def update_movie_to_genre_preference(self, movie_pk, genre_list, original_rating, updated_rating):        
        original_priority = int(original_rating - 2.5) * 4
        updated_priority = int(updated_rating - 2.5) * 4

        for genre in genre_list:
            if genre in self.genre_preference:
                self.genre_preference[genre] += (updated_priority - original_priority) 

        return None