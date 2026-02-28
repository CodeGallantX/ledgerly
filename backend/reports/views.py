from rest_framework import viewsets, permissions, response, status
from rest_framework.decorators import action
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal
from finance.models import Invoice, Payment
from students.models import Student
from academics.models import Term, ClassRoom
from app.permissions import IsAccountant

class ReportViewSet(viewsets.ViewSet):
    """
    Reporting engine for school financials.

    Architecture:
    - Centralized logic using Django ORM aggregations to avoid N+1 queries.
    - All queries are filtered by request.user.school to ensure tenant isolation.
    """
    permission_classes = [IsAccountant]

    @action(detail=False, methods=['get'])
    def term_revenue(self, request):
        term_id = request.query_params.get('term_id')
        if not term_id:
            return response.Response({'error': 'term_id required'}, status=status.HTTP_400_BAD_REQUEST)

        total_revenue = Payment.objects.filter(
            school=request.user.school,
            invoice__term_id=term_id,
            matched=True
        ).aggregate(total=Coalesce(Sum('amount'), Decimal('0.00'), output_field=DecimalField()))['total']

        return response.Response({'term_id': term_id, 'total_revenue': total_revenue})

    @action(detail=False, methods=['get'])
    def outstanding_balances(self, request):
        total_outstanding = Invoice.objects.filter(
            school=request.user.school
        ).aggregate(total=Coalesce(Sum('balance'), Decimal('0.00'), output_field=DecimalField()))['total']

        return response.Response({'total_outstanding': total_outstanding})

    @action(detail=False, methods=['get'])
    def revenue_by_class(self, request):
        term_id = request.query_params.get('term_id')
        if not term_id:
            return response.Response({'error': 'term_id required'}, status=status.HTTP_400_BAD_REQUEST)

        # Optimization: Single Group-By query instead of iterating through classes
        results = ClassRoom.objects.filter(school=request.user.school).annotate(
            revenue=Coalesce(
                Sum(
                    'students__invoices__payments__amount',
                    filter=(
                        Invoice.objects.filter(
                            term_id=term_id,
                            payments__matched=True
                        ).values('id')
                    )
                ),
                Decimal('0.00'),
                output_field=DecimalField()
            )
        ).values('name', 'revenue')

        # Wait, the above join might be tricky. Let's simplify with a cleaner group by approach on Payment.
        revenue_data = Payment.objects.filter(
            school=request.user.school,
            invoice__term_id=term_id,
            matched=True
        ).values('student__class_room__name').annotate(
            total_revenue=Sum('amount')
        ).order_by('student__class_room__name')

        data = [{'class_name': item['student__class_room__name'], 'revenue': item['total_revenue']} for item in revenue_data]
        return response.Response(data)
