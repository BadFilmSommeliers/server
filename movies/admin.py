from django.contrib import admin
from .models import Movie, Review, ReviewComment, Collection, CollectionComment


admin.site.register(Movie)
admin.site.register(Review)
admin.site.register(ReviewComment)
admin.site.register(Collection)
admin.site.register(CollectionComment)