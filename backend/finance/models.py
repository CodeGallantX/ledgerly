import uuid
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class FeeStructure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('accounts.School', on_delete=models.CASCADE, related_name='fee_structures')
    class_room = models.ForeignKey('academics.ClassRoom', on_delete=models.CASCADE, related_name='fee_structures')
    term = models.ForeignKey('academics.Term', on_delete=models.CASCADE, related_name='fee_structures')
    tuition_fee = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    other_fees = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['class_room', 'term', 'school'], name='unique_class_term_school_fee')
        ]

    def __str__(self):
        return f"{self.class_room.name} - {self.term.name}"

class Invoice(models.Model):
    STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('unpaid', 'Unpaid'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('accounts.School', on_delete=models.CASCADE, related_name='invoices')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='invoices')
    term = models.ForeignKey('academics.Term', on_delete=models.CASCADE, related_name='invoices')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'term', 'school'], name='unique_student_term_school_invoice')
        ]

    def save(self, *args, **kwargs):
        self.balance = self.total_amount - self.amount_paid
        if self.balance <= 0:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        else:
            self.status = 'unpaid'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice for {self.student.full_name} - {self.term.name}"

class Payment(models.Model):
    METHOD_CHOICES = (
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('card', 'Card'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('accounts.School', on_delete=models.CASCADE, related_name='payments')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    reference = models.CharField(max_length=100, unique=True) # Overall unique reference
    narration = models.TextField(blank=True)
    transaction_date = models.DateTimeField()
    matched = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.reference} - {self.amount}"

class LedgerEntry(models.Model):
    ENTRY_TYPE_CHOICES = (
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('accounts.School', on_delete=models.CASCADE, related_name='ledger_entries')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='ledger_entries')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='ledger_entries', null=True, blank=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='ledger_entries', null=True, blank=True)
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.entry_type.upper()} {self.amount} - {self.student.full_name}"
