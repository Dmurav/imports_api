from datetime import date, datetime, timedelta

import pytest
from hamcrest import assert_that, has_entries

from imports.api.serializers import CitizenSerializer, CreateDataSetSerializer
from imports.utils import latin_russian_digit


def test_latin_russian_digit():
    assert latin_russian_digit == ('abcdefghijklmnopqrstuvwxyz'
                                   'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                   'абвгдежзийклмнопрстуфхцчшщъыьэюя'
                                   'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ0'
                                   '123456789')


class TestCitizenSerializer:
    @pytest.fixture()
    def citizen(self, citizens):
        """Valid citizen data."""
        return citizens[0]

    def test_valid_data(self, citizen):
        s = CitizenSerializer(data=citizen)
        s.is_valid()
        assert_that(s.validated_data, has_entries({
            'citizen_id': 1,
            'town': 'Москва',
            'street': 'Льва Толстого',
            'building': '16к2стр5',
            'apartment': 1,
            'name': 'Иванов Иван Иванович',
            'birth_date': date(year=1990, month=5, day=29),
            'gender': 'male',
            'relatives': [2],
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
    def test_validation_errors(self, citizen, action, field, value, is_valid):
        if action == 'set':
            citizen[field] = value
        elif action == 'delete':
            citizen.pop(field, None)

        s = CitizenSerializer(data=citizen)
        assert is_valid == s.is_valid(raise_exception=False)

    @pytest.mark.parametrize('data', [
        {'town': 'Москва', 'birth_date': '23.03.1990'},
        {'apartment': 4},
        {'relatives': []},
    ])
    def test_partial_data_validation(self, data):
        s = CitizenSerializer(data=data, partial=True)
        assert s.is_valid(raise_exception=False)

    def test_partial_forbids_citizen_id(self):
        s = CitizenSerializer(data={'citizen_id': 1, 'town': 'Москва'}, partial=True)
        assert not s.is_valid(raise_exception=False)

    def test_partial_requires_at_least_one_field(self):
        s = CitizenSerializer(data={}, partial=True)
        assert not s.is_valid(raise_exception=False)

    def test_partial_unknown_fields(self):
        s = CitizenSerializer(data={'unknown': 1}, partial=True)
        assert not s.is_valid(raise_exception=False)


class TestDataSetSerializer:
    def test_valid(self, citizens):
        data = {
            'citizens': citizens
        }
        s = CreateDataSetSerializer(data=data)
        assert s.is_valid(raise_exception=False)

    def test_no_empty_citizens(self):
        data = {'citizens': []}
        s = CreateDataSetSerializer(data=data)
        assert not s.is_valid(raise_exception=False)

    def test_repeated_citizen_ids(self, citizens):
        citizens[0]['citizen_id'] = 1
        citizens[0]['relatives'] = []
        citizens[1]['citizen_id'] = 1
        citizens[1]['relatives'] = []
        data = {'citizens': citizens}
        s = CreateDataSetSerializer(data=data)
        assert not s.is_valid(raise_exception=False)

    def test_bad_relatives(self, citizens):
        citizens[0]['citizen_id'] = 1
        citizens[0]['relatives'] = []
        citizens[1]['citizen_id'] = 2
        citizens[1]['relatives'] = [1]
        data = {'citizens': citizens}
        s = CreateDataSetSerializer(data=data)
        assert not s.is_valid(raise_exception=False)
