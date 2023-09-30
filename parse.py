from pprint import pprint

from lxml import html
import json
from main import parse_user_data

with open(r'Q:\TEMP\gbc_parser\2023-09-30-10-37-39_Дни рождения 24.04.23 - 07.05.23.html', 'r') as f:
    txt = f.read()

data = parse_user_data(txt)

pprint(data)
