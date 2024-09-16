from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.pagination import UsersPagination
from user.serializers import (CustomUserSerializer, UserAvatarSerializer,
                              SubscribtionCreateSerializer,
                              SubscribtionListSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def subscribe(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        serializer = SubscribtionCreateSerializer(
            data={'person_id': request.user.id, 'sub_id': pk},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = SubscribtionListSerializer(user,
                                                context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        sub = request.user.user_person.filter(sub_id=pk)
        if sub.exists():
            sub.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'errors': ('Вы не подписаны на '
                                    'данного пользователя')},
                        status=status.HTTP_400_BAD_REQUEST)


class Subscriptions(generics.ListAPIView):
    pagination_class = UsersPagination
    serializer_class = SubscribtionListSerializer

    def get_queryset(self):
        users = self.request.user.user_person.all()
        data_user = []
        for user in users:
            data_user.append(user.sub_id)
        return data_user


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def set_user_avatar(request):
    serializer = UserAvatarSerializer(data=request.data, instance=request.user)
    if request.method == 'PUT':
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        user = get_object_or_404(User, pk=request.user.id)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
