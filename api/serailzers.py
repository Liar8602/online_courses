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
        exclude = ('password',)

class StudentUsernameSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = ('id', 'username',)
    
    @staticmethod
    def get_username(student_profile):
        return student_profile.user.username


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
        exclude = ('course',)


class CourseSheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseShedule
        exclude = ('course',)


class ShortCourseRegistrationSerializer(serializers.ModelSerializer):
    student = StudentUsernameSerializer()

    class Meta:
        model = CourseRegistration
        fields = ('id', 'student',)


class CourseSerializer(serializers.ModelSerializer):
    lectures = LectureSerializer(many=True)
    shedules = CourseSheduleSerializer(many=True)
    registrations = ShortCourseRegistrationSerializer(many=True)

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'price',
            'number_of_lectures',
            'description',
            'lectures',
            'schedules',
            'registrations',
        )


class CourseRegistrationSerializer(serializers.ModelSerializer):
    student = StudentUsernameSerializer()
    course = CourseSerializer()

    class Meta:
        model = CourseRegistration
        fields = ('id', 'student', 'course',)


class StudentProfileSerializer(serializers.ModelSerializer):
    user = StudentSerializer()
    courses_registrations = CourseRegistrationSerializer(many=True)

    class Meta:
        model = StudentProfile
        fields = ('user', 'courses_registrations',)