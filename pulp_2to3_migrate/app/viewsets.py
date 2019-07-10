from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework.decorators import detail_route

from pulpcore.app.viewsets.custom_filters import HyperlinkRelatedFilter
from pulpcore.plugin.serializers import AsyncOperationResponseSerializer
from pulpcore.plugin.tasking import enqueue_with_reservation
from pulpcore.plugin.viewsets import (
    BaseFilterSet,
    NamedModelViewSet,
    OperationPostponedResponse,
)

from .constants import PULP_2TO3_MIGRATION_RESOURCE
from .models import MigrationPlan
from .serializers import (
    MigrationPlanSerializer,
    MigrationPlanRunSerializer,
)
from .tasks.migrate import migrate_from_pulp2


class MigrationPlanFilter(BaseFilterSet):
    tasks = HyperlinkRelatedFilter()

    class Meta:
        model = MigrationPlan
        fields = {
            'tasks': ['exact'],
        }


class MigrationPlanViewSet(NamedModelViewSet,
                           mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.ListModelMixin):
    endpoint_name = 'migration-plans'
    queryset = MigrationPlan.objects.all()
    serializer_class = MigrationPlanSerializer
    filter_class = MigrationPlanFilter

    @swagger_auto_schema(
        operation_summary="Run migration plan",
        operation_description="Trigger an asynchronous task to run a migration from Pulp 2.",
        responses={202: AsyncOperationResponseSerializer}
    )
    @detail_route(methods=('post',), serializer_class=MigrationPlanRunSerializer)
    def run(self, request, pk):
        migration_plan = self.get_object()
        serializer = MigrationPlanRunSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        dry_run = serializer.validated_data.get('dry_run', False)
        result = enqueue_with_reservation(
            migrate_from_pulp2,
            [PULP_2TO3_MIGRATION_RESOURCE],
            kwargs={
                'migration_plan_pk': migration_plan.pk,
                'dry_run': dry_run
            }
        )
        return OperationPostponedResponse(result, request)
