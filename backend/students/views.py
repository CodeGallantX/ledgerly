from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal
from rest_framework import viewsets, permissions
from .models import Student, Parent
from .serializers import StudentSerializer, ParentSerializer
from app.mixins import TenantViewSet
from app.permissions import IsSchoolMember, IsAccountant

class StudentViewSet(TenantViewSet):
    """
    ViewSet for Student CRUD.

    Performance:
    - Uses annotate to calculate outstanding_balance in a single SQL query to avoid N+1 issues.
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsSchoolMember]
    filterset_fields = ['class_room', 'is_active']

    def get_queryset(self):
        return super().get_queryset().annotate(
            annotated_outstanding_balance=Coalesce(
                Sum('invoices__balance'),
                Decimal('0.00'),
                output_field=DecimalField()
            )
        )

class ParentViewSet(TenantViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [IsSchoolMember]
