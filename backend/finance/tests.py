from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from accounts.models import School
from academics.models import AcademicSession, Term, ClassRoom
from students.models import Student, Parent
from .models import FeeStructure, Invoice, Payment, LedgerEntry
from .services import InvoiceService

class FinanceTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="Test School", slug="test-school")
        self.session = AcademicSession.objects.create(school=self.school, name="2023/2024")
        self.term = Term.objects.create(
            school=self.school,
            session=self.session,
            name="First Term",
            start_date="2023-09-01",
            end_date="2023-12-15"
        )
        self.class_room = ClassRoom.objects.create(school=self.school, name="Primary 1")
        self.parent = Parent.objects.create(school=self.school, full_name="John Doe")
        self.student = Student.objects.create(
            school=self.school,
            parent=self.parent,
            class_room=self.class_room,
            admission_number="001",
            first_name="Junior",
            last_name="Doe"
        )
        self.fee = FeeStructure.objects.create(
            school=self.school,
            class_room=self.class_room,
            term=self.term,
            tuition_fee=Decimal('50000.00'),
            other_fees=Decimal('10000.00')
        )

    def test_invoice_generation(self):
        invoice = InvoiceService.generate_invoice(self.student, self.term)
        self.assertEqual(invoice.total_amount, Decimal('60000.00'))
        self.assertEqual(invoice.balance, Decimal('60000.00'))
        self.assertEqual(invoice.status, 'unpaid')

        # Check LedgerEntry for Invoice
        self.assertTrue(LedgerEntry.objects.filter(invoice=invoice, entry_type='debit').exists())

    def test_payment_and_ledger(self):
        invoice = InvoiceService.generate_invoice(self.student, self.term)
        payment = Payment.objects.create(
            school=self.school,
            student=self.student,
            invoice=invoice,
            amount=Decimal('20000.00'),
            payment_method='cash',
            reference='REF001',
            transaction_date=timezone.now(),
            matched=True
        )

        invoice.refresh_from_db()
        self.assertEqual(invoice.amount_paid, Decimal('20000.00'))
        self.assertEqual(invoice.balance, Decimal('40000.00'))
        self.assertEqual(invoice.status, 'partial')

        # Check LedgerEntry for Payment
        self.assertTrue(LedgerEntry.objects.filter(payment=payment, entry_type='credit').exists())
