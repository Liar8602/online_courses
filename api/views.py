from django.db import transaction, IntegrityError, DatabaseError
from django.contrib.auth.models import User

from rest_framework.viewsets import ViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from courses.forms import StudentForm, StudentProfileForm

from courses.models import StudentProfile
from api.serailzers import StudentProfileSerializer, RegisterStudentSerializer, StudentUpdateSerializer

from settings.settings import django_logger

from rest_framework.authtoken.models import Token


for user in User.objects.all():
    if user.is_active:
        Token.objects.get_or_create(user=user)
class StudentProfileViewSet(ViewSet):
    authentication_classes = (TokenAuthentication,)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        django_logger.info(f'student profile action request: "{self.action}"')
        if self.action in ('create', 'destroy', 'update'):
            permission_classes = (IsAdminUser,)
        elif self.action in ('retrieve', ):
            permission_classes = (IsAuthenticated, )
        else:
            permission_classes = (AllowAny,)
        return [permission() for permission in permission_classes]

    queryset = StudentProfile.objects
    student_profile_serializer = StudentProfileSerializer
    student_register_serializer = RegisterStudentSerializer
    student_update_serializer = StudentUpdateSerializer

    def create(self, request):
        serializer = self.student_register_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                student_form = StudentForm(data=serializer.validated_data)
                profile_form = StudentProfileForm(data=dict(profile_pic=None, category='student'))
                new_student = student_form.save()
                new_student.set_password(new_student.password)
                new_student.save()
                profile = profile_form.save(commit=False)
                profile.student = new_student
                profile.save()
        except (IntegrityError, DatabaseError, Exception) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.validated_data)


    def list(self, request):
        serializer = self.student_profile_serializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        student_ = request.student
        student_profile = request.user.studentprofile
        if student_.is_staff or student_profile.id == int(pk):
            student_ = self.queryset.filter(id=pk).first()
            return Response(self.student_profile_serializer(student_).data)
        else:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)
    
    def update(self, request, pk=None):
        request.data.update(dict(pk=pk))
        serializer = self.student_update_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student_new_data = serializer.validated_data
        student_profile = student_new_data.pop('pk')
        student_ = student_profile.student
        try:
            with transaction.atomic():
                for attr, value in user_new_data.item():
                    if attr != 'password':
                        setattr(student_, attr, value)
                    else:
                        student_.set_password(value)
                student_.save()
        except(IntegrityError, DatabaseError, Exception) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.validated_data) 
     
    def destroy(self, request, pk=None):
        student_ = self.queryset.filter(pk=pk).first()
        if student_:
            student_.delete()
            return Response(self.student_profile_serializer(student_).data)
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)