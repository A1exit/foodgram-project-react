from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Follow, User
from .serializers import SubscriptionsSerializer


class ListSubscriptions(viewsets.ModelViewSet):
    serializer_class = SubscriptionsSerializer

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)


class Subscribe(APIView):

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = get_object_or_404(Follow, user=user,
                                         author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        Follow.objects.get_or_create(user=user, author=author)
        serializer = SubscriptionsSerializer(author, context={'request':
                                                              request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
