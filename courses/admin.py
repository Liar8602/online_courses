from django.contrib import admin
from courses.models import (
    StudentProfile,
    StudentProfileAdmin,
    Course,
    CourseAdmin,
    Lecture,
    LectureAdmin,
    CourseRegistration,
    CourseRegistrationAdmin,
    CourseShedule,
    CourseSheduleAdmin
)


admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lecture, LectureAdmin)
admin.site.register(CourseRegistration, CourseRegistrationAdmin)
admin.site.register(CourseShedule, CourseSheduleAdmin)