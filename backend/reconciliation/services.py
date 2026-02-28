import csv
from decimal import Decimal
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from rapidfuzz import process, fuzz
from students.models import Student
from finance.models import Invoice, Payment
from .models import BankTransaction, ReconciliationLog

class ReconciliationService:
    @staticmethod
    def import_csv(school, file_content):
        """
        Imports transactions from a CSV file.
        Expects CSV with: date, amount, reference, narration
        """
        # Read file_content from the file-like object
        decoded_file = file_content.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        for row in reader:
            # Parse date and ensure it's timezone aware
            dt = datetime.fromisoformat(row['date'])
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt)

            BankTransaction.objects.update_or_create(
                school=school,
                reference=row['reference'],
                defaults={
                    'amount': Decimal(row['amount']),
                    'narration': row['narration'],
                    'transaction_date': dt,
                    'matched': False
                }
            )

    @staticmethod
    @transaction.atomic
    def match_transactions(school):
        """
        Attempts to match unmatched bank transactions with students based on narration and amount.
        Assigns confidence scores and auto-matches if score > 85.
        """
        unmatched_txs = BankTransaction.objects.filter(school=school, matched=False)
        students = Student.objects.filter(school=school, is_active=True)
        student_names = [s.full_name for s in students]
        student_map = {s.full_name: s for s in students}

        logs = []

        for tx in unmatched_txs:
            # Simple match by amount and fuzzy name matching in narration
            best_match = process.extractOne(tx.narration, student_names, scorer=fuzz.partial_ratio)

            if best_match:
                match_name, score, index = best_match
                student = student_map[match_name]

                # Further refine score based on outstanding balance comparison
                matching_invoice = Invoice.objects.filter(
                    school=school,
                    student=student,
                    balance=tx.amount,
                    status__in=['unpaid', 'partial']
                ).first()

                confidence = float(score)
                if matching_invoice:
                    confidence = min(100.0, confidence + 20.0)

                status = 'unmatched'
                if confidence > 85.0:
                    status = 'auto_matched'
                    ReconciliationService.create_payment_from_match(school, tx, student, matching_invoice)
                elif confidence >= 60.0:
                    status = 'manual_review'

                log = ReconciliationLog.objects.create(
                    school=school,
                    bank_transaction=tx,
                    matched_student=student,
                    confidence_score=confidence,
                    status=status
                )
                logs.append(log)
            else:
                log = ReconciliationLog.objects.create(
                    school=school,
                    bank_transaction=tx,
                    confidence_score=0.0,
                    status='unmatched'
                )
                logs.append(log)

        return logs

    @staticmethod
    @transaction.atomic
    def create_payment_from_match(school, bank_transaction, student, invoice=None):
        """
        Creates a payment record from a successful match.
        """
        if bank_transaction.matched:
            return None

        payment = Payment.objects.create(
            school=school,
            student=student,
            invoice=invoice,
            amount=bank_transaction.amount,
            payment_method='bank_transfer',
            reference=bank_transaction.reference,
            narration=bank_transaction.narration,
            transaction_date=bank_transaction.transaction_date,
            matched=True
        )

        bank_transaction.matched = True
        bank_transaction.save()

        if invoice:
            from finance.services import InvoiceService
            InvoiceService.update_invoice_balance(invoice)

        return payment

    @staticmethod
    def calculate_confidence(narration, amount):
        pass
