from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions
from stooper.stooper_rest_framework.serializers import UserSerializer, GroupSerializer
from stooper.stooper_rest_framework.models import PostLocation
from stooper.stooper_rest_framework.serializers import PostLocationSerializer
from rest_framework import status
from rest_framework.response import Response


class PostLocationViewSet(viewsets.ModelViewSet):
    queryset = PostLocation.objects.all().order_by("-posted_at")
    serializer_class = PostLocationSerializer
    permission_classes = [permissions.BasePermission]
    http_method_names = ['get', 'post', 'patch']

    def patch(self, request, pk):
        postlocation = PostLocation.get(pk)
        serializer = PostLocationSerializer(postlocation, data=request.data,
                                         partial=True)  # set partial=True to update a data partially
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


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
