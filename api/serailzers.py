from rest_framework import serializers

from django.contrib.auth.models import User
from courses.models import (
    StudentProfile, 
    Course, 
    Lecture, 
    CourseShedule, 
    CourseRegistration
)

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CourseRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRegistration
        fields = '__all__'


class StudentProfileSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    courses_registrations = CourseRegistrationSerializer(many=True)

    class Meta:
        model = StudentProfile
        fields = '__all__'


class RegisterStudentSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=20)
    first_name = serializers.CharField(max_length=80)
    last_name = serializers.CharField(max_length=80)
    email = serializers.CharField(
        max_length=70,   
        )


class StudentUpdateSerializer(serializers.Serializer):
    pk = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects)
    username = serializers.CharField(max_length=30, required=False)
    password = serializers.CharField(max_length=20, required=False)
    first_name = serializers.CharField(max_length=70,required=False)
    last_name = serializers.CharField(max_length=70, required=False)
    email= serializers.CharField(max_length=70, required=False)


class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = '__all__'


class CourseSheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseShedule
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    lectures = LectureSerializer(many=True)
    shedules = CourseSheduleSerializer(many=True)
    registrations = CourseRegistrationSerializer(many=True)

    class Meta:
        model = Course
        fields = '__all__'