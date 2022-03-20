from datetime import timedelta, date
from django_rq import job, enqueue

from django.core.mail import send_mass_mail, send_mail
from settings.settings import DEFAULT_FROM_EMAIL, django_logger
from .models import CourseShedule, CourseRegistration


def send_registration_confirmation_mail(username: str=None, email: str = None):
    subject = 'Thank you for registering!'
    message = f"""
        Thank You for registering!"""
    enqueue(
        send_mail_to_student,
        user_mail=email,
        subject=subject,
        message=message
    )

@job('default')
def send_mail_to_student(user_mail: str = None, subject: str = None, message: str = None):
    send_mail(subject, message, DEFAULT_FROM_EMAIL, [user_mail, ], fail_silently=True)
    django_logger.info(f'\nsending confilrmation mail to {user_mail if user_mail else " - "}')
    return True


def send_course_begin_mails():
    days = 30
    today = date.today()
    tomorrow = today + timedelta(days=days)
    schedules = CourseShedule.objects.select_related('course').filter(
        start_date__lte=tomorrow,
        start_date__gt=today,
    ).all()
    courses = {sch.course for sch in schedules}
    registrations = CourseRegistration.objects.select_related('student', 'course').filter(course__in=courses).all()
    mail_templates = [(rg.student.user.email, rg.student.user.first_name, rg.course.title) for rg in registrations]
    message_tupples = []
    for mt in mail_templates:
        subject = f'{mt[2]} will start in {days} day'
        message = f'Dear {mt[1]}, \nyou are registered for the {mt[2]} course, which start in {days}'
        to_mail = mt[0]
        message_tupples.append((subject, message, DEFAULT_FROM_EMAIL, [to_mail, ],))

    django_logger.info(f'sending {len(message_tupples)} course begins mails')
    send_mass_mail(message_tupples, fail_silently=True)
    return True

send_course_begin_mails()