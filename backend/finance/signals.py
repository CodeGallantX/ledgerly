from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment, Invoice, LedgerEntry

@receiver(post_save, sender=Payment)
def update_invoice_on_payment_creation(sender, instance, created, **kwargs):
    """
    Updates the Invoice when a Payment is created and matched.
    """
    if created and instance.matched and instance.invoice:
        from .services import InvoiceService
        InvoiceService.update_invoice_balance(instance.invoice)

@receiver(post_save, sender=Payment)
def create_ledger_entry_for_payment(sender, instance, created, **kwargs):
    """
    Automatically creates a LedgerEntry for a Payment.
    """
    if created and instance.matched:
        LedgerEntry.objects.create(
            school=instance.school,
            student=instance.student,
            payment=instance,
            invoice=instance.invoice,
            entry_type='credit',
            amount=instance.amount,
            description=f"Payment received: {instance.reference}. {instance.narration}"
        )

@receiver(post_save, sender=Invoice)
def create_ledger_entry_for_invoice(sender, instance, created, **kwargs):
    """
    Automatically creates a LedgerEntry for an Invoice.
    """
    if created:
        LedgerEntry.objects.create(
            school=instance.school,
            student=instance.student,
            invoice=instance,
            entry_type='debit',
            amount=instance.total_amount,
            description=f"Invoice generated for {instance.term.name}"
        )
