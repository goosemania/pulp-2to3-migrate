import logging

from mongoengine import (
    BooleanField,
    DictField,
    IntField,
    ListField,
    StringField,
)

from pulp_2to3_migration.pulp2.base import (
    ContentUnit,
    FileContentUnit,
)

_logger = logging.getLogger(__name__)


class NonMetadataPackage(FileContentUnit):
    """
    An abstract Pulp 2 model to be subclassed by packages which are not metadata.
    """

    version = StringField(required=True)
    release = StringField(required=True)
    checksum = StringField(required=True)
    checksumtype = StringField(required=True)
    checksums = DictField()
    signing_key = StringField()  # not used in the migration plugin

    version_sort_index = StringField()  # not used in the migration plugin
    release_sort_index = StringField()  # not used in the migration plugin

    meta = {
        'abstract': True,
    }


class RpmBase(NonMetadataPackage):
    """
    An abstract model designed to be sub-classed by both RPM and SRPM.
     
    RPM amd SRPM package types are similar. Most fields map to metadata fields in the RPM package
    format.
    """

    # Unit Key Fields
    name = StringField(required=True)
    epoch = StringField(required=True)
    version = StringField(required=True)
    release = StringField(required=True)
    arch = StringField(required=True)

    # Other Fields
    build_time = IntField()  # not used in the migration plugin
    buildhost = StringField()  # not used in the migration plugin
    vendor = StringField()  # not used in the migration plugin
    size = IntField()
    base_url = StringField()  # not used in the migration plugin
    filename = StringField()
    relative_url_path = StringField()  # not used in the migration plugin
    relativepath = StringField()  # not used in the migration plugin
    group = StringField()  # not used in the migration plugin

    provides = ListField()  # not used in the migration plugin
    files = DictField()  # not used in the migration plugin
    repodata = DictField(default={})
    description = StringField()  # not used in the migration plugin
    header_range = DictField()  # not used in the migration plugin
    sourcerpm = StringField()  # not used in the migration plugin
    license = StringField()  # not used in the migration plugin
    changelog = ListField()  # not used in the migration plugin
    url = StringField()  # not used in the migration plugin
    summary = StringField()  # not used in the migration plugin
    time = IntField()  # not used in the migration plugin
    requires = ListField()  # not used in the migration plugin
    recommends = ListField()  # not used in the migration plugin

    unit_key_fields = ('name', 'epoch', 'version', 'release', 'arch', 'checksumtype', 'checksum')

    meta = {
        'indexes': [
            "name", "epoch", "version", "release", "arch", "filename", "checksum", "checksumtype", 
            "version_sort_index", ("version_sort_index", "release_sort_index")
        ],
        'abstract': True,
    }


class RPM(RpmBase):
    """
    A model for Pulp 2 RPM content type.

    It will become a Package content type in Pulp 3 world.
    """
    TYPE_ID = 'rpm'

    # For backward compatibility
    _ns = StringField(default='units_rpm')
    _content_type_id = StringField(required=True, default=TYPE_ID)

    unit_display_name = 'RPM'
    unit_description = 'RPM'
    unit_referenced_types = ['erratum']

    is_modular = BooleanField(default=False)

    meta = {
        'collection': 'units_rpm',
        'allow_inheritance': False,
    }


class Errata(ContentUnit):
    """
    A model for Pulp 2 Erratum content type.

    It will become an Advisory content type in Pulp 3 world.
    """
    errata_id = StringField(required=True)
    status = StringField()
    updated = StringField(required=True, default='')
    description = StringField()
    issued = StringField()
    pushcount = StringField()
    references = ListField()
    reboot_suggested = BooleanField()
    relogin_suggested = BooleanField()
    restart_suggested = BooleanField()
    errata_from = StringField(db_field='from')
    severity = StringField()
    rights = StringField()
    version = StringField()
    release = StringField()
    type = StringField()
    pkglist = ListField()
    title = StringField()
    solution = StringField()
    summary = StringField()

    # For backward compatibility
    _ns = StringField(default='units_erratum')
    _content_type_id = StringField(required=True, default='erratum')

    unit_key_fields = ('errata_id',)
    unit_display_name = 'Erratum'
    unit_description = 'Erratum advisory information'
    unit_referenced_types = ['rpm']

    meta = {
        'indexes': [
            "version", "release", "type", "status", "updated", "issued", "severity", "references"
        ],
        'collection': 'units_erratum',
        'allow_inheritance': False,
    }