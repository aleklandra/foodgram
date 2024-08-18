from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from djoser.views import UserViewSet
from .serializers import CustomUserSerializer, UserAvatarSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .pagination import UsersPagination


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def set_user_avatar(request):
    instance = User.objects.get(username=request.user.username)
    serializer = UserAvatarSerializer(data=request.data, instance=instance)
    if request.method == 'PUT':
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        user = get_object_or_404(User, username=request.user.username)
        user.avatar = None
        user.save()
        return Response({"detail": "Учетные данные не были предоставлены."},
                        status=status.HTTP_204_NO_CONTENT)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
