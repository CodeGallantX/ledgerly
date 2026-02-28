from rest_framework import viewsets, permissions, status, response
from rest_framework.decorators import action
from .models import BankTransaction, ReconciliationLog
from .serializers import BankTransactionSerializer, ReconciliationLogSerializer
from .services import ReconciliationService
from app.mixins import TenantViewSet
from app.permissions import IsAccountant

class BankTransactionViewSet(TenantViewSet):
    queryset = BankTransaction.objects.all()
    serializer_class = BankTransactionSerializer
    permission_classes = [IsAccountant]
    filterset_fields = ['matched', 'transaction_date']

    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return response.Response({'error': 'CSV file required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ReconciliationService.import_csv(request.user.school, file_obj)
            return response.Response({'message': 'Transactions imported successfully.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def run_matching(self, request):
        try:
            logs = ReconciliationService.match_transactions(request.user.school)
            serializer = ReconciliationLogSerializer(logs, many=True)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def approve_match(self, request, pk=None):
        tx = self.get_object()
        student_id = request.data.get('student_id')
        invoice_id = request.data.get('invoice_id')

        if not student_id:
            return response.Response({'error': 'student_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from students.models import Student
            from finance.models import Invoice
            student = Student.objects.get(id=student_id, school=request.user.school)
            invoice = Invoice.objects.filter(id=invoice_id, school=request.user.school).first() if invoice_id else None

            payment = ReconciliationService.create_payment_from_match(request.user.school, tx, student, invoice)
            if payment:
                return response.Response({'message': 'Match approved and payment created.'}, status=status.HTTP_201_CREATED)
            else:
                return response.Response({'error': 'Transaction already matched or error occurred.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ReconciliationLogViewSet(TenantViewSet):
    queryset = ReconciliationLog.objects.all()
    serializer_class = ReconciliationLogSerializer
    permission_classes = [IsAccountant]
    filterset_fields = ['status', 'matched_student']
