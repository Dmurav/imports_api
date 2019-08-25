from itertools import chain


def get_latin_russian_digit():
    ranges = [
        ['a', 'z'],
        ['A', 'Z'],
        ['а', 'я'],
        ['А', 'Я'],
        ['0', '9'],
    ]
    ords = chain(*(range(ord(first), ord(last) + 1) for first, last in ranges))
    letters = ''.join(chr(i) for i in ords)
    return letters


latin_russian_digit = get_latin_russian_digit()


def calculate_age(current_date, birth_date):
    years = current_date.year - birth_date.year
    if (birth_date.month, birth_date.day) < (current_date.month, current_date.day):
        years -= 1
    return years