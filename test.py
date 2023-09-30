import json
import os
import sys
from datetime import datetime
from pprint import pprint
import glob

files = glob.glob(os.path.join(os.getcwd(), 'json', '*'))
newest = max(files, key=os.path.getctime)
print(newest)


with open(newest, 'r', encoding='utf-8') as ff:
    data = ff.read()

data = data.replace('][', ',')
data = json.loads(data)

print(type(data))


# filename = f"{datetime.strftime(datetime.now(), '%Y%m%d_%H%M_%S')}.json"

# new_path = os.path.join(os.getcwd(), 'json', filename)
# print(new_path)
# # sys.exit()
# with open(new_path, 'w') as f:
#     f.write(new_path)
#
#
# with open(new_path, 'r') as f:
#     print(f.read())
