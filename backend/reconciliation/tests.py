import csv
import io
from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from accounts.models import School
from academics.models import AcademicSession, Term, ClassRoom
from students.models import Student, Parent
from finance.models import FeeStructure, Invoice, Payment, LedgerEntry
from finance.services import InvoiceService
from .models import BankTransaction, ReconciliationLog
from .services import ReconciliationService

class ReconciliationTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="Match School", slug="match-school")
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
            admission_number="ADM001",
            first_name="Alice",
            last_name="Johnson"
        )
        # Alice Johnson has an invoice for 50000.00
        self.fee = FeeStructure.objects.create(
            school=self.school,
            class_room=self.class_room,
            term=self.term,
            tuition_fee=Decimal('40000.00'),
            other_fees=Decimal('10000.00')
        )
        self.invoice = InvoiceService.generate_invoice(self.student, self.term)

    def test_auto_match(self):
        # Create bank transaction with narration including name
        tx = BankTransaction.objects.create(
            school=self.school,
            amount=Decimal('50000.00'),
            narration="Payment for Alice Johnson First Term",
            reference="TXREF001",
            transaction_date=timezone.now()
        )

        logs = ReconciliationService.match_transactions(self.school)
        self.assertEqual(len(logs), 1)
        # Check if score is high enough for auto_matched
        # Given fuzz.partial_ratio "Alice Johnson" in "Payment for Alice Johnson First Term" should be 100.
        # Plus 20 boost (capped at 100).
        self.assertEqual(logs[0].status, 'auto_matched')
        self.assertEqual(logs[0].matched_student, self.student)

        tx.refresh_from_db()
        self.assertTrue(tx.matched)

        # Check Payment created
        self.assertTrue(Payment.objects.filter(school=self.school, student=self.student, reference="TXREF001").exists())

        # Check Invoice updated
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, 'paid')
        self.assertEqual(self.invoice.balance, Decimal('0.00'))

    def test_manual_review(self):
        # Narration with only partial name
        tx = BankTransaction.objects.create(
            school=self.school,
            amount=Decimal('45000.00'), # amount doesn't match exactly
            narration="Alice J. school fees",
            reference="TXREF002",
            transaction_date=timezone.now()
        )

        logs = ReconciliationService.match_transactions(self.school)
        self.assertEqual(len(logs), 1)
        # With "Alice J." and amount 45000.00 (invoice is 50000.00), score should be between 60 and 85
        self.assertEqual(logs[0].status, 'manual_review')

    def test_unmatched(self):
        tx = BankTransaction.objects.create(
            school=self.school,
            amount=Decimal('50000.00'),
            narration="Unknown Payer Fees",
            reference="TXREF003",
            transaction_date=timezone.now()
        )
        logs = ReconciliationService.match_transactions(self.school)
        self.assertEqual(logs[0].status, 'unmatched')
