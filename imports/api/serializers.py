import re
from datetime import datetime

from rest_framework import serializers

from imports.utils import latin_russian_digit


def validate_non_negative(value):
    if value < 0:
        raise serializers.ValidationError('Must be non-negative.')

    re.compile(r'a-zA-Z0-9')


def validate_has_letter_or_digit(string):
    if not set(latin_russian_digit) & set(string):
        raise serializers.ValidationError('Must contain digit or latin/russian letter.')


class NoUnknownFieldsSerializer(serializers.Serializer):
    _unknown_fields = None

    def to_internal_value(self, data):
        if isinstance(data, dict):
            self._unknown_fields = set(data.keys()) - set(self.fields.keys())
        return super().to_internal_value(data)

    def validate(self, data):
        if self._unknown_fields:
            raise serializers.ValidationError(f'Unknown fields: {self._unknown_fields}')
        return super().validate(data)


class CitizenRelativesField(serializers.ListField):
    def to_representation(self, mtm_manager):
        return list(mtm_manager.all().values_list('citizen_id', flat=True))


class CitizenSerializer(NoUnknownFieldsSerializer):
    citizen_id = serializers.IntegerField(required=True, validators=[validate_non_negative])

    town = serializers.CharField(required=True,
                                 allow_blank=False,
                                 max_length=256,
                                 validators=[validate_has_letter_or_digit])

    street = serializers.CharField(required=True,
                                   allow_blank=False,
                                   max_length=256,
                                   validators=[validate_has_letter_or_digit])

    building = serializers.CharField(required=True,
                                     allow_blank=False,
                                     max_length=256,
                                     validators=[validate_has_letter_or_digit])

    apartment = serializers.IntegerField(required=True, validators=[validate_non_negative])

    name = serializers.CharField(required=True, allow_blank=False, max_length=256)
    birth_date = serializers.DateField(required=True, format='%d.%m.%Y', input_formats=['%d.%m.%Y'])

    gender = serializers.ChoiceField(required=True,
                                     choices=(('male', 'male'), ('female', 'female')))

    relatives = CitizenRelativesField(child=serializers.IntegerField(), allow_empty=True)

    def validate_birth_date(self, value):
        if value >= datetime.utcnow().date():
            raise serializers.ValidationError('Birth date must be less then current date.')
        return value

    def validate(self, data):
        if not data:
            raise serializers.ValidationError('At last one field required')

        if self.partial and data:
            if 'citizen_id' in data:
                raise serializers.ValidationError('Citizen id is not allowed when updating citizen')

        citizen_id = data.get('citizen_id')
        relatives = data.get('relatives')
        if citizen_id and relatives and citizen_id in relatives:
            raise serializers.ValidationError('Citizen can not be relative to itself.')
        return super().validate(data)


class CreateDataSetSerializer(NoUnknownFieldsSerializer):
    citizens = serializers.ListSerializer(child=CitizenSerializer(),
                                          allow_null=False,
                                          allow_empty=False)

    def validate(self, data):
        citizens = data['citizens']

        citizen_ids = set()
        pairs = set()

        for c in citizens:
            # check uniqueness of citizen_id in dataset
            cid = c['citizen_id']
            if cid not in citizen_ids:
                citizen_ids.add(cid)
            else:
                raise serializers.ValidationError(f'Duplicated citizen id {cid}')

            # check relatives relation
            for rid in c['relatives']:
                pair = (min(cid, rid), max(cid, rid))
                if pair in pairs:
                    pairs.remove(pair)
                else:
                    pairs.add(pair)

        if pairs:
            raise serializers.ValidationError(
                    f'Relatives relation for citizen pairs {pairs} in unsymmetric.')

        del citizen_ids
        del pairs
        return super().validate(data)


class UpdateCitizenSerializer(NoUnknownFieldsSerializer):
    data_set_id = serializers.IntegerField(required=True, allow_null=False)
    citizen_id = serializers.IntegerField(required=True, validators=[validate_non_negative])
