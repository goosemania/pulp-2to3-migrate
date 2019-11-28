from django.contrib.postgres.fields import JSONField
from django.db import models

from pulp_2to3_migration.app.models import Pulp2to3Content

from pulp_rpm.app.models import (
    Package,
    UpdateRecord,
)

from .pulp2_models import (
    Errata,
    RPM,
)


class Pulp2Rpm(Pulp2to3Content):
    """
    Pulp 2to3 detail content model to store Pulp 2 RPM content details for Pulp 3 content creation.
    """

    name = models.TextField()
    epoch = models.TextField()
    version = models.TextField()
    release = models.TextField()
    arch = models.TextField()
    checksum = models.TextField()
    checksumtype = models.TextField()

    repodata = JSONField(dict)
    is_modular =models.BooleanField(default=False)
    size = models.IntField()
    filename = models.TextField()

    type = 'rpm'

    class Meta:
        unique_together = (
            'name', 'epoch', 'version', 'release', 'arch', 'checksumtype', 'checksum',
            'pulp2content')
        default_related_name = 'rpm_detail_model'

    @property
    def expected_digests(self):
        """Return expected digests."""
        return {self.checksumtype: self.checksum}

    @property
    def expected_size(self):
        """Return expected size."""
        return self.size

    @property
    def relative_path_for_content_artifact(self):
        """Return relative path."""
        return self.filename

    @classmethod
    async def pre_migrate_content_detail(cls, content_batch):
        """
        Pre-migrate Pulp 2 RPM content with all the fields needed to create a Pulp 3 Package.

        Args:
             content_batch(list of Pulp2Content): pre-migrated generic data for Pulp 2 content.

        """
        pulp2_id_obj_map = {pulp2content.pulp2_id: pulp2content for pulp2content in content_batch}
        pulp2_ids = pulp2_id_obj_map.keys()
        pulp2_rpm_content_batch = RPM.objects.filter(id__in=pulp2_ids)
        pulp2rpm_to_save = [
            Pulp2Rpm(name=rpm.name,
                     epoch = rpm.epoch,
                     version = rpm.version,
                     release = rpm.release,
                     arch = rpm.arch,
                     checksum = rpm.checksum,
                     checksumtype = rpm.checksumtype,
                     repodata = rpm.repodata,
                     is_modular = rpm.is_modular,
                     size = rpm.size,
                     filename = rpm.filename,
                     checksum=rpm.checksum,
                     size=rpm.size,
                     pulp2content=pulp2_id_obj_map[rpm.id])
            for rpm in pulp2_rpm_content_batch]
        cls.objects.bulk_create(pulp2rpm_to_save, ignore_conflicts=True)

    def create_pulp3_content(self):
        """
        Create a Pulp 3 Package content for saving it later in a bulk operation.
        """

        # TODO: figure out
        #   - how to get decompressed metadata snippets
        #   - how to "untemplatize" all the snippets
        #   - how much createrepo_c likes and can process those snippets to extract all data we need

        return Package(
            name=self.name,
            epoch=self.epoch,
            version=self.version,
            release=self.release,
            arch=self.arch,
            # more fields to go
        )

