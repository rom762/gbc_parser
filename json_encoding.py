from pprint import pprint

import json

filename = r'Q:\TEMP\gbc_parser\json\20230930_1340_13.json'
new_filename = r'Q:\TEMP\gbc_parser\json\20230930_1340_13_encoded.json'

with open(filename, 'r', encoding='utf-8') as ff:
    data = ff.read()
    data = data.replace('][', ',')
    json_data = json.loads(data)

# pprint(json_data)

with open(new_filename, 'w', encoding='utf-8') as ff:
    ff.write(str(json_data))
    # json.dump(data, ff, ensure_ascii=False)
