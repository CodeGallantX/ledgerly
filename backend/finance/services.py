"""
Finance Service Layer.

Architecture:
- Encapsulates complex business logic (Invoice generation, balance recalculation).
- Ensures atomic transactions for financial integrity.
- Decouples business rules from Views/Models for better testability and maintenance.
"""
from decimal import Decimal
from django.db import transaction
from .models import Invoice, FeeStructure

class InvoiceService:
    @staticmethod
    @transaction.atomic
    def generate_invoice(student, term):
        """
        Generates an invoice for a student for a specific term based on FeeStructure.
        Implementation of automatic student invoicing.
        """
        # Multi-tenant check: ensure we only look at the student's school
        if Invoice.objects.filter(student=student, term=term, school=student.school).exists():
            return Invoice.objects.get(student=student, term=term, school=student.school)

        fee_structure = FeeStructure.objects.filter(
            school=student.school,
            class_room=student.class_room,
            term=term
        ).first()

        if not fee_structure:
            raise ValueError(f"No fee structure found for {student.class_room.name} in {term.name}")

        total_amount = fee_structure.tuition_fee + fee_structure.other_fees

        invoice = Invoice.objects.create(
            school=student.school,
            student=student,
            term=term,
            total_amount=total_amount,
            amount_paid=Decimal('0.00'),
            balance=total_amount
        )
        return invoice

    @staticmethod
    def update_invoice_balance(invoice):
        """
        Recalculates amount_paid and balance based on associated matched payments.
        """
        from .models import Payment
        payments = Payment.objects.filter(invoice=invoice, matched=True)
        total_paid = sum(p.amount for p in payments)
        invoice.amount_paid = total_paid
        invoice.save() # save() handles status and balance calculation
        return invoice
