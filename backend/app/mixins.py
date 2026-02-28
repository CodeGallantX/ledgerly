from rest_framework import viewsets

class TenantMixin:
    """
    Mixin to filter by the user's school.
    """
    def get_queryset(self):
        return super().get_queryset().filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class TenantViewSet(TenantMixin, viewsets.ModelViewSet):
    pass
