from rest_framework import viewsets, permissions, status, response
from rest_framework.decorators import action
from .models import Invoice, Payment, LedgerEntry, FeeStructure
from .serializers import InvoiceSerializer, PaymentSerializer, LedgerEntrySerializer, FeeStructureSerializer
from .services import InvoiceService
from app.mixins import TenantViewSet
from app.permissions import IsAccountant

class FeeStructureViewSet(TenantViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAccountant]
    filterset_fields = ['class_room', 'term']

class InvoiceViewSet(TenantViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAccountant]
    filterset_fields = ['student', 'term', 'status']

    @action(detail=False, methods=['post'])
    def generate(self, request):
        student_id = request.data.get('student_id')
        term_id = request.data.get('term_id')
        if not student_id or not term_id:
            return response.Response({'error': 'student_id and term_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from students.models import Student
            from academics.models import Term
            student = Student.objects.get(id=student_id, school=request.user.school)
            term = Term.objects.get(id=term_id, school=request.user.school)
            invoice = InvoiceService.generate_invoice(student, term)
            return response.Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        student = self.get_object().student
        invoices = Invoice.objects.filter(student=student, school=request.user.school).order_by('-created_at')
        serializer = self.get_serializer(invoices, many=True)
        return response.Response(serializer.data)

class PaymentViewSet(TenantViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAccountant]
    filterset_fields = ['student', 'invoice', 'payment_method']

    def perform_create(self, serializer):
        # Manual payment
        serializer.save(school=self.request.user.school, matched=True)

    @action(detail=False, methods=['get'])
    def student_history(self, request):
        student_id = request.query_params.get('student_id')
        if not student_id:
            return response.Response({'error': 'student_id required'}, status=status.HTTP_400_BAD_REQUEST)
        payments = Payment.objects.filter(student_id=student_id, school=request.user.school).order_by('-transaction_date')
        serializer = self.get_serializer(payments, many=True)
        return response.Response(serializer.data)

class LedgerEntryViewSet(TenantViewSet):
    queryset = LedgerEntry.objects.all()
    serializer_class = LedgerEntrySerializer
    permission_classes = [IsAccountant]
    filterset_fields = ['student', 'entry_type']
