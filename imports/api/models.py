from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField


class CreatedUpdatedMixin(models.Model):
    class Meta:
        abstract = True

    created_at = CreationDateTimeField(_('created_at'))
    updated_at = ModificationDateTimeField(_('created_at'))


class DataSet(CreatedUpdatedMixin, models.Model):
    id = models.BigIntegerField(primary_key=True)


class Citizen(CreatedUpdatedMixin, models.Model):
    class Meta:
        unique_together = (('data_set', 'citizen_id'),)

    GENDER_MALE = 'male'
    GENDER_FEMALE = 'female'
    GENDER_CHOICES = (
        (GENDER_MALE, GENDER_MALE),
        (GENDER_FEMALE, GENDER_FEMALE),
    )

    id = models.BigIntegerField(primary_key=True)  # surrogate id

    citizen_id = models.BigIntegerField(null=False)
    town = models.CharField(null=False, blank=False, max_length=2048)
    street = models.CharField(null=False, blank=False, max_length=2048)
    building = models.CharField(null=False, blank=False, max_length=2048)
    apartment = models.BigIntegerField(null=False)
    name = models.CharField(null=False, blank=False, max_length=2048)
    birth_date = models.DateField(null=False)
    gender = models.CharField(null=False, choices=GENDER_CHOICES, max_length=128)

    data_set = models.ForeignKey(to='DataSet', on_delete=models.CASCADE)
    relatives = models.ManyToManyField('self', symmetrical=True)