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
    def validate(self, data):
        unknown_fields = set(self.initial_data.keys()) - set(self.fields.keys())
        if unknown_fields:
            raise serializers.ValidationError(f'Unknown fields for citizen {unknown_fields}')
        return super().validate(data)


class CreateCitizenSerializer(NoUnknownFieldsSerializer):
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

    relatives = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)

    def validate(self, data):
        if data['birth_date'] >= datetime.utcnow().date():
            raise serializers.ValidationError('Birth date must be less then current date.')
        if data['citizen_id'] in data['relatives']:
            raise serializers.ValidationError('Citizen can not be relative to itself.')
        return super().validate(data)
