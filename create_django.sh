export x="STARTREC"
django-admin startproject django_beginner
cd django_beginner
django-admin startapp quickstart
python manage.py migrate
python manage.py createsuperuser --email ryanl888@gmail.com --username roylam
# Make Serializers
echo "from django.contrib.auth.models import User, Group from rest_framework import serializers class UserSerializer(serializers.HyperlinkedModelSerializer): class Meta: model = User fields = ['url', 'username', 'email', 'groups'] class GroupSerializer(serializers.HyperlinkedModelSerializer): class Meta: model = Group fields = ['url', 'name']" >> serializers.py
mv serializers.py quickstart/
# Create Views
echo 'from django.contrib.auth.models import User, Group from rest_framework import viewsets from rest_framework import permissions from tutorial.quickstart.serializers import UserSerializer, GroupSerializer class UserViewSet(viewsets.ModelViewSet): """ API endpoint that allows users to be viewed or edited. """ queryset = User.objects.all().order_by('-date_joined') serializer_class = UserSerializer permission_classes = [permissions.IsAuthenticated] class GroupViewSet(viewsets.ModelViewSet): """ API endpoint that allows groups to be viewed or edited. """ queryset = Group.objects.all() serializer_class = GroupSerializer permission_classes = [permissions.IsAuthenticated]' >> quickstart/views.py
