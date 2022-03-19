from datetime import date
from calendar import monthrange

from django.shortcuts import render
from django.db import transaction, IntegrityError, DatabaseError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from rest_framework.authtoken.models import Token

from .forms import StudentForm, StudentProfileForm, MonthYearForm
from settings.settings import django_logger
from courses.models import (
    Course, 
    CourseRegistration,
    CourseShedule
)


def index(request):
    context = {'active': "home"}
    return render (request, 'index.html', context=context)


@login_required
def user_logout(request):
    logout(request)
    django_logger.info(f'successful user logout: "{request.user.username}"')
    return HttpResponseRedirect(reverse('index'))


def user_login(request):
    errors_string = None
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                django_logger.info((f'successful user login: "{user.username}"'))
                return HttpResponseRedirect(reverse('index'))
            else:
                django_logger.info(f'try to login not active user: "{user.username}"')
                errors_string = 'WRONG ACCOUNT'
        else:
            django_logger.info(f'invalid login: "{username}" password: "{password}"')
            errors_string = 'INVALID USERNAME OR PASSWORD!'
    
    context = {'active': "login", 'errors': errors_string}
    return render(request, 'login.html', context=context)


def user_register(request):
    registered = False
    errors_string = None
    all_errors = []

    if request.method == "POST":
        user_form = StudentForm(data=request.POST)        

        if user_form.is_valid():
            try:
                with transaction.atomic():
                    user = user_form.save()
                    user.set_password(user.password)
                    user.save()
                    
                    profile_form = StudentProfileForm(data={'category': 'student'})
                    profile = profile_form.save(commit=False)
                    profile.user = user            
                    profile.save()
                    Token.objects.get_or_create(user=user)
                    registered = True
                    django_logger.info('successful student registration!')
            except (IntegrityError, DatabaseError, Exception) as e:
                all_errors.append(str(e))
                registered = False
        else:
            for err_list in user_form.errors.values():
                all_errors.append(' '.join(err_list))
        errors_string = ' '.join(all_errors)
    else:
        registered = True if request.user.username else False
        user_form = StudentForm()
    
    context = {
        'active': 'register',
        'errors': errors_string,
        'user_form': user_form,
        'registered': registered
    }
    return render(request, 'registration.html', context=context)


@login_required
def courses_list(request):
    user = request.user
    student = user.student_profile if hasattr(user, 'student_profile') else None
    courses = list(Course.objects.prefetch_related('registrations').all())
    if student:
        student_registrations = {course.id for course in courses if course.student_registered(student.id)}
    else:
        student_registrations = []
    context = {
        'courses': courses,
        'student_id': student.id if student else None,
        'student_registrations': student_registrations,
    }
    return render(request, 'courses_list.html', context=context)


@login_required
def course_detail(request, pk):
    user = request.user
    student = user.student_profile if hasattr(user, 'student_profile') else None
    course = Course.objects \
        .prefetch_related('lectures', 'schedules', 'registrations') \
        .order_by('lectures__number_in_course') \
        .get(pk=pk)
    lectures = course.lectures.all()
    registrations = course.registrations.all()
    schedules = course.schedules.all()
    for schedule in schedules:
        if date.today() <= schedule.start_date:
            scheduled = schedule.start_date
            break
    else:
        scheduled = None
    student_registered = False
    for registration in registrations:
        if registration.student.pk == student.pk:
            student_registered = True
    context = {
        'student': student,
        'course': course,
        'lectures': lectures,
        'registrations': len(registrations) if registrations else 0,
        'scheduled': scheduled,
        'student_registered': student_registered,
    }
    return render(request, 'course_detail.html', context=context)


def get_course_registration(course_id=None, student_id=None):
    course_registration = CourseRegistration.objects.select_related('course', 'student').filter(
        student_id=student_id,
        course_id=course_id
    ).first()
    return course_registration


@login_required
def course_register(request, course_id, student_id):
    user =request.user
    student = user.student_profile if hasattr(user, 'student_profile') else None
    course_registration = get_course_registration(course_id=course_id, student_id=student_id)
    course = Course.objects.filter(pk=course_id).first()
    if student_id == student.id and not course_registration and course:
        CourseRegistration(student=student, course=course).save()
    return HttpResponseRedirect(reverse('courses_app:course_detail', args={course_id}))
    


@login_required
def cancel_course_registration(request, course_id, student_id):
    user = request.user
    student = user.student_profile if hasattr(user, 'student_profile') else None
    course_registration = get_course_registration(course_id=course_id, student_id=student_id)
    if student_id == student.id and course_registration:
        course_registration.delete()
    return HttpResponseRedirect(reverse('courses_app:course_detail', args={course_id}))


@login_required
def courses_calendar(request):
    user = request.user
    student = user.student_profile if hasattr(user, 'student_profile') else None
    today = date.today()
    this_year = today.year
    year = this_year
    month = today.month
    all_errors = []
    if request.method == 'POST':
        month_year_form = MonthYearForm(data=request.POST)
        if month_year_form.is_valid():
            year = month_year_form.cleaned_data['year']
            month = month_year_form.cleaned_data['month']
        else:
            for err_list in month_year_form.errors.values():
                all_errors.append(' '.join(err_list))
    errors_string = ' '.join(all_errors)
    schedules = CourseSchedule.objects.select_related('course').filter(
        start_date__gte=date(year=year, month=month, day=1),
        start_date__lt=date(year=year + 2, month=month, day=monthrange(year, month)[1]),
    )
    scheduled_courses = []
    for sch in schedules:
        course_data = {
            'start_date': sch.start_date,
            'id': sch.course.id,
            'title': sch.course.title,
            'student_registered': 'you are registered' if student and sch.course.student_registered(
                student.id) else ''
        }
        scheduled_courses.append(course_data)
    context = {
        'month': month,
        'year': year,
        'all_months': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        'all_years': [this_year, this_year + 1, this_year + 2],
        'courses': scheduled_courses,
        "errors": errors_string,
    }
    return render(request, 'calendar.html', context=context)