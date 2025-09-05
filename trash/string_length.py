from string import ascii_lowercase
from itertools import cycle

abc = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
ABC = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
result = ''

for char in cycle(abc + ABC):
    result += char
    if len(result) == 250:
        break


print(result)
