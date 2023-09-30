import os
import sys
from datetime import datetime

filename = f"{datetime.strftime(datetime.now(), '%Y%m%d_%H%M_%S')}.json"

new_path = os.path.join(os.getcwd(), 'json', filename)
print(new_path)
# sys.exit()
with open(new_path, 'w') as f:
    f.write(new_path)


with open(new_path, 'r') as f:
    print(f.read())
