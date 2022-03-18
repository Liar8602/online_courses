from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    profile_pic = models.ImageField(upload_to='profile_pics',blank=True)
    category = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.user.username


class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'category')
    list_filter = ('category',)
    fields = ['category', 'user']

class Course(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=400)
    number_of_lectures = models.IntegerField()
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)


class Lecture(models.Model):
    id = models.IntegerField(primary_key=True)
    course = models.ForeignKey(Course, related_name='lectures', on_delete=models.SET_NULL, null=True)
    number_in_course = models.IntegerField()


class LectureInline(admin.TabularInline):
    model = Lecture


class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'number_of_lectures', 'description', 'price')
    list_filter = ('id', 'number_of_lectures', 'price')
    fields = [('id', 'title', 'number_of_lectures', 'price'), 'description']
    inlines = [LectureInline,]


class LectureAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'number_in_course')
    list_filter = ('id', 'course')
    fields = [('id', 'number_in_course', 'title'), 'course']

class CourseRegistration(models.Model):
    id = models.IntegerField(primary_key=True)
    student = models.ForeignKey(StudentProfile, related_name='courses_registrations', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='registrations',on_delete=models.CASCADE)


class CourseRegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course')
    list_filter = ('id', 'course', 'student')
    fields = ['id', 'student', 'course']


class CourseShedule(models.Model):
    id = models.IntegerField(primary_key=True)
    course = models.ForeignKey('Course', related_name='shedules', on_delete=models.CASCADE)
    start_date = models.DateField()


class CourseSheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'start_date')
    list_filter = ('id', 'course', 'start_date')
    fields = ['id', 'course', 'start_date']