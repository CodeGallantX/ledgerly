from rest_framework import serializers
from django.db import transaction
from .models import School, User

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'school')
        read_only_fields = ('school',)

class RegistrationSerializer(serializers.Serializer):
    school_name = serializers.CharField(max_length=255)
    school_slug = serializers.SlugField()
    school_email = serializers.EmailField()
    owner_username = serializers.CharField()
    owner_password = serializers.CharField(write_only=True)
    owner_email = serializers.EmailField()

    @transaction.atomic
    def create(self, validated_data):
        school = School.objects.create(
            name=validated_data['school_name'],
            slug=validated_data['school_slug'],
            email=validated_data['school_email']
        )
        owner = User.objects.create_user(
            username=validated_data['owner_username'],
            password=validated_data['owner_password'],
            email=validated_data['owner_email'],
            school=school,
            role='owner'
        )
        return {'school': school, 'owner': owner}
