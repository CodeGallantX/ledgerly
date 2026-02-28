from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from accounts.views import RegistrationViewSet, SchoolViewSet, UserViewSet
from students.views import StudentViewSet, ParentViewSet
from finance.views import FeeStructureViewSet, InvoiceViewSet, PaymentViewSet, LedgerEntryViewSet
from reconciliation.views import BankTransactionViewSet, ReconciliationLogViewSet
from reports.views import ReportViewSet

router = DefaultRouter()
router.register(r'auth', RegistrationViewSet, basename='auth')
router.register(r'schools', SchoolViewSet, basename='school')
router.register(r'users', UserViewSet, basename='user')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'parents', ParentViewSet, basename='parent')
router.register(r'fee-structures', FeeStructureViewSet, basename='fee-structure')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'ledger', LedgerEntryViewSet, basename='ledger')
router.register(r'bank-transactions', BankTransactionViewSet, basename='bank-transaction')
router.register(r'reconciliation-logs', ReconciliationLogViewSet, basename='reconciliation-log')
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
