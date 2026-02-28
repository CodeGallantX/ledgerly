import uuid
from django.db import models

class BankTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('accounts.School', on_delete=models.CASCADE, related_name='bank_transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    narration = models.TextField()
    reference = models.CharField(max_length=100) # Unique per school handled in Meta
    transaction_date = models.DateTimeField()
    matched = models.BooleanField(default=False)
    confidence_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['school', 'reference'], name='unique_school_bank_reference')
        ]
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['transaction_date']),
        ]

    def __str__(self):
        return f"{self.reference} - {self.amount}"

class ReconciliationLog(models.Model):
    STATUS_CHOICES = (
        ('auto_matched', 'Auto Matched'),
        ('manual_review', 'Manual Review'),
        ('unmatched', 'Unmatched'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('accounts.School', on_delete=models.CASCADE, related_name='reconciliation_logs')
    bank_transaction = models.ForeignKey(BankTransaction, on_delete=models.CASCADE, related_name='reconciliation_logs')
    matched_student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='reconciliation_logs', null=True, blank=True)
    confidence_score = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.bank_transaction.reference} - {self.status}"
