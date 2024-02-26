from django.contrib.auth.models import Group, User
from rest_framework import serializers

from apiview.models import *

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class SeismicDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationInfo
        fields = "__all__"

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadFile
        fields = ('id', 'file', 'string_data')