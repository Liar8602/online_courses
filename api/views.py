from django.db import transaction, IntegrityError, DatabaseError

from rest_framework.viewsets import ViewSet
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from courses.forms import StudentForm, StudentProfileForm

from courses.models import StudentProfile
from api.serailzers import StudentProfileSerializer

from api.serailzers import StudentProfileSerializer, RegisterStudentSerializer


class StudentProfileViewSet(ViewSet):
    authentication_classes = (SessionAuthentication,)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ('create', 'destroy', 'update'):
            permission_classes = [IsAdminUser]
        elif self.action in ('retrieve', ):
            permission_classes = [IsAuthenticated, ]
        else:
            permission_classes = [AllowAny,]
        return [permission() for permission in permission_classes]

    queryset = StudentProfile.objects
    student_serializer = StudentProfileSerializer
    student_register_serializer = RegisterStudentSerializer

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
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.validated_data)


    def list(self, request):
        serializer = self.student_serializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = self.queryset.filter(id=pk).first()
        return Response(self.student_serializer(user).data)

    def update(self, request, pk=None):
        user =self.queryset.filter(pk=pk).first()
        if user:
            serializer = self.student_register_serializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request, pk=None):
        user = self.queryset.filter(pk=pk).first()
        if user:
            user.delete()
            return Response(self.student_serializer(user).data)
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)