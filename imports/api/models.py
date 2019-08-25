from django.db import models
from django.db.models import F
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField


class CreatedUpdatedMixin(models.Model):
    class Meta:
        abstract = True

    created_at = CreationDateTimeField(_('created_at'))
    updated_at = ModificationDateTimeField(_('created_at'))


class DataSet(CreatedUpdatedMixin, models.Model):
    objects = models.Manager()


class Citizen(CreatedUpdatedMixin, models.Model):
    class Meta:
        unique_together = (('data_set', 'citizen_id'),)

    GENDER_MALE = 'male'
    GENDER_FEMALE = 'female'
    GENDER_CHOICES = (
        (GENDER_MALE, GENDER_MALE),
        (GENDER_FEMALE, GENDER_FEMALE),
    )

    citizen_id = models.BigIntegerField(null=False)
    town = models.CharField(null=False, blank=False, max_length=2048)
    street = models.CharField(null=False, blank=False, max_length=2048)
    building = models.CharField(null=False, blank=False, max_length=2048)
    apartment = models.BigIntegerField(null=False)
    name = models.CharField(null=False, blank=False, max_length=2048)
    birth_date = models.DateField(null=False)
    gender = models.CharField(null=False, choices=GENDER_CHOICES, max_length=128)

    data_set = models.ForeignKey(to='DataSet', on_delete=models.CASCADE, related_name='citizens')
    relatives = models.ManyToManyField(through='CitizenRelative', to='Citizen')

    @property
    def relatives_ids(self):
        return list(self.relatives.values_list('citizen_id', flat=True))

    def __str__(self):
        return (f"<Citizen dataset: {self.data_set_id}, "
                f"citizen_id: {self.citizen_id}, "
                f"_id: {self.id})>")


class CitizenRelativeManager(models.Manager):
    def get_birthdays(self, data_set_id):
        data = list(self.filter(
                citizen__data_set_id=data_set_id).annotate(
                relative_birth_date=F('relative__birth_date'),
                cid=F('citizen__citizen_id'),
                rid=F('relative__citizen_id')
        ).values('cid', 'rid', 'relative_birth_date').distinct())

        for d in data:
            d['citizen_id'] = d['cid']
            d.pop('cid')
            d['relative_id'] = d['rid']
            d.pop('rid')

        return sorted(data,
                      key=lambda d: (d['citizen_id'], d['relative_id'], d['relative_birth_date']))


class CitizenRelative(CreatedUpdatedMixin, models.Model):
    class Meta:
        unique_together = (('citizen', 'relative'),)

    citizen = models.ForeignKey('Citizen', null=False, on_delete=models.CASCADE,
                                related_name='to_citizen_relatives')
    relative = models.ForeignKey('Citizen', null=False, on_delete=models.CASCADE,
                                 related_name='from_citizen_relatives')

    objects = CitizenRelativeManager()
