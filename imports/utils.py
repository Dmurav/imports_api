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
