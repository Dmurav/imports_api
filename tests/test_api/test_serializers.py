from datetime import date, datetime, timedelta

import pytest
from hamcrest import assert_that, has_entries

from imports.api.serializers import CreateCitizenSerializer
from imports.utils import latin_russian_digit


def test_latin_russian_digit():
    assert latin_russian_digit == ('abcdefghijklmnopqrstuvwxyz'
                                   'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                   'абвгдежзийклмнопрстуфхцчшщъыьэюя'
                                   'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ0'
                                   '123456789')


class TestCreateCitizenSerializer:
    @pytest.fixture()
    def gender(self):
        return 'male'

    @pytest.fixture()
    def citizen_data(self, gender):
        data = {
            'citizen_id': 1,
            'town': 'Москва',
            'street': 'Льва Толстого',
            'building': '16к2стр5',
            'apartment': 1,
            'name': 'Иванов Иван Иванович',
            'birth_date': '29.05.1990',
            'gender': gender,
            'relatives': [20],
        }
        return data

    @pytest.mark.parametrize('gender', ('male', 'female'))
    def test_valid_data(self, citizen_data, gender):
        s = CreateCitizenSerializer(data=citizen_data)
        s.is_valid()
        assert_that(s.validated_data, has_entries({
            'citizen_id': 1,
            'town': 'Москва',
            'street': 'Льва Толстого',
            'building': '16к2стр5',
            'apartment': 1,
            'name': 'Иванов Иван Иванович',
            'birth_date': date(year=1990, month=5, day=29),
            'gender': gender,
            'relatives': [20],
        }))

    @pytest.mark.parametrize(('action', 'field', 'value', 'is_valid'), [
        # citizen_id values
        ['delete', 'citizen_id', None, False],  # required
        ['set', 'citizen_id', None, False],  # non-null
        ['set', 'citizen_id', -1, False],  # non-negative

        # town values
        ['delete', 'town', None, False],
        ['set', 'town', 257 * 'a', False],
        ['set', 'town', '', False],
        ['set', 'town', None, False],
        ['set', 'town', '//*', False],
        ['set', 'town', 256 * 'a', True],
        ['set', 'town', 'Я', True],
        ['set', 'town', 'Z', True],
        ['set', 'town', '', False],  # non-blank

        # street values
        ['delete', 'street', None, False],
        ['set', 'street', 257 * 'a', False],
        ['set', 'street', '', False],
        ['set', 'street', None, False],
        ['set', 'street', '//*', False],
        ['set', 'street', 256 * 'a', True],
        ['set', 'street', 'Я', True],
        ['set', 'street', 'Z', True],
        ['set', 'street', '', False],  # non-blank

        # building values
        ['delete', 'building', None, False],
        ['set', 'building', 257 * 'a', False],
        ['set', 'building', '', False],
        ['set', 'building', None, False],
        ['set', 'building', '//*', False],
        ['set', 'building', 256 * 'a', True],
        ['set', 'building', 'Я', True],
        ['set', 'building', 'Z', True],
        ['set', 'building', '', False],  # non-blank

        # apartment values
        ['delete', 'apartment', None, False],  # required
        ['set', 'apartment', None, False],  # non-null
        ['set', 'apartment', -1, False],  # non-negative

        # name values
        ['delete', 'name', None, False],  # required
        ['set', 'name', None, False],  # non-null
        ['set', 'name', 257 * 'a', False],
        ['set', 'name', 256 * 'a', True],
        ['set', 'name', '', False],  # non-blank

        # birth_date values
        ['delete', 'birth_date', None, False],  # required
        ['set', 'birth_date', None, False],  # non-null
        ['set', 'birth_date', '01.01.2017', True],
        ['set', 'birth_date', '2017.01.01', False],
        ['set', 'birth_date', '34.78.2010', False],
        ['set', 'birth_date', '31.02.2019', False],
        ['set', 'birth_date', (datetime.utcnow() + timedelta(days=1)).strftime('%d.%m.%Y'), False],

        # gender values
        ['delete', 'gender', None, False],  # required
        ['set', 'gender', None, False],  # non-null
        ['set', 'gender', 'male', True],
        ['set', 'gender', 'female', True],
        ['set', 'gender', 'unknown', False],

        # gender values
        ['delete', 'gender', None, False],  # required
        ['set', 'gender', None, False],  # non-null
        ['set', 'gender', 'male', True],
        ['set', 'gender', 'female', True],
        ['set', 'gender', 'unknown', False],

        # gender values
        ['delete', 'relatives', None, False],  # required
        ['set', 'relatives', None, False],  # non-null
        ['set', 'relatives', None, False],  # non-null
        ['set', 'relatives', [1], False],  # can not be relative to itself

        # unknown field
        ['set', 'unknown', 1, False]
    ])
    def test_validation_errors(self, citizen_data, action, field, value, is_valid):
        if action == 'set':
            citizen_data[field] = value
        elif action == 'delete':
            citizen_data.pop(field, None)

        s = CreateCitizenSerializer(data=citizen_data)
        assert is_valid == s.is_valid(raise_exception=False)
