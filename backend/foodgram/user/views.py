from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomUserSerializer, UserAvatarSerializer
from user.models import UserSubscription
from user.pagination import UsersPagination


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def subscribe(request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = CustomUserSerializer(user, context={'request': request, })
        if user == request.user:
            return Response({'errors': 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
        try:
            tmp = UserSubscription.objects.get(sub_id=user,
                                              person_id=request.user,)
        except UserSubscription.DoesNotExist:
            tmp = None
        if request.method == 'POST':
            if tmp is None:
                UserSubscription.objects.create(
                    sub_id=user,
                    person_id=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'errors': 'Вы уже подписаны на данного пользователя'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            if tmp is None:
                return Response({'errors': 'Вы не подписаны на данного пользователя'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    tmp.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                except Exception:
                    return Response({'errors': Exception},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Subscriptions(generics.ListAPIView):
    pagination_class = UsersPagination
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        users = UserSubscription.objects.filter(person_id=self.request.user)
        data_user = []
        for user in users:
            data_user.append(user.sub_id)
        return data_user



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
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
