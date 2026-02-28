from rest_framework import viewsets, permissions, status, response
from rest_framework.decorators import action
from .models import School, User
from .serializers import SchoolSerializer, UserSerializer, RegistrationSerializer

class RegistrationViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegistrationSerializer

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return response.Response({
            'school': SchoolSerializer(data['school']).data,
            'owner': UserSerializer(data['owner']).data,
            'message': 'School and owner registered successfully.'
        }, status=status.HTTP_201_CREATED)

class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(id=self.request.user.school.id)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(school=self.request.user.school)
