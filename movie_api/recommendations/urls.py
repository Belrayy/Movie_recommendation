from django.urls import path # type: ignore
from .views import *

urlpatterns = [
    path('movies/', add_movie),
    path('moviesfull/<int:movie_id>/', get_movie_full_by_id),
    path('moviesshort/<int:movie_id>/', get_movie_short_by_id),
    path('link/<int:movie_id>/', get_link_by_id),
    path('keywords/<int:movie_id>/', get_keyword_by_id),
    path('credit/<int:movie_id>/', get_credit_by_id),
    path('rating/<int:movie_id>/<int:user_id>/', get_rating_by_movieid_userid),
]
