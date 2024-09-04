from django.urls import include, path
from user.views import set_user_avatar, subscribe, Subscriptions

urlpatterns = [
    path('users/subscriptions/', Subscriptions.as_view(), name='subscriptions'),
    path('users/me/avatar/', set_user_avatar, name='avatar'),
    path('users/<int:pk>/subscribe/', subscribe, name='subscribe'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
