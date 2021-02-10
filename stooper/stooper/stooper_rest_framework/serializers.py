from django.contrib.auth.models import User, Group
from stooper.stooper_rest_framework.models import PostLocation
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class PostLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLocation
        fields = [
            "id",
            "created",
            "posted_at",
            "display_url",
            "insta_account",
            "caption",
            "lat",
            "long",
        ]
