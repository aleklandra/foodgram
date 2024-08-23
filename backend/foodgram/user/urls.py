from django.urls import include, path
from user.views import set_user_avatar

urlpatterns = [
    path('', include('djoser.urls')),
    path('users/me/avatar/', set_user_avatar, name='avatar'),
    path('auth/', include('djoser.urls.authtoken')),
]
