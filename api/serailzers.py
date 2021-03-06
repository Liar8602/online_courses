from datetime import date
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
        fields = '__all__'


class ShortScheduleSerializer(serializers.ModelSerializer):    
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
    shedules = ShortScheduleSerializer(many=True)
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


class ShortCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'price',
            'number_of_lectures',
            'description',
        )


class CourseRegistrationSerializer(serializers.ModelSerializer):
    student = StudentUsernameSerializer()
    course = ShortCourseSerializer()

    class Meta:
        model = CourseRegistration
        fields = '__all__'


class CourseRegistrationParamsSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects)

    class Meta:
        fields = ('student', 'course')


class StudentProfileSerializer(serializers.ModelSerializer):
    user = StudentSerializer()
    courses_registrations = CourseRegistrationSerializer(many=True)

    class Meta:
        model = StudentProfile
        fields = ('user', 'courses_registrations',)


class MonthYearSerializer(serializers.Serializer):
    month = serializers.IntegerField(required=False, min_value=1, max_value=12)
    year = serializers.IntegerField(
        required=False,
        min_value=date.today().year,
        max_value=date.today().year + 1
    )

    def validate(self, attrs):
        if attrs.get('month') is None:
            attrs['month'] = date.today().month
        if attrs.get('year') is None:
            attrs['year'] = date.today().year
        return attrs