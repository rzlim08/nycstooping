from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions
from stooper.stooper_rest_framework.serializers import UserSerializer, GroupSerializer
from stooper.stooper_rest_framework.models import PostLocation
from stooper.stooper_rest_framework.serializers import PostLocationSerializer


class PostLocationViewSet(viewsets.ModelViewSet):
    queryset = PostLocation.objects.all()
    serializer_class = PostLocationSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
