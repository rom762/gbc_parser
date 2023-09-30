from datetime import datetime

import json
import os
from pprint import pprint
import requests
from dotenv import load_dotenv
from main import parse_user_data
load_dotenv()


def get_fake_browser_headers(api_key: str):
    response = requests.get(
      url='https://headers.scrapeops.io/v1/browser-headers',
      params={
          'api_key': api_key,
          'num_headers': '1'}
    )
    return response.json()

payload = {"os_username": os.getenv('USER_NAME'),
               "os_password": os.getenv('USER_PASSWORD'),
               "login": "Войти",
               "os_destination": "/pages/viewpage.action?pageId=200938851"}

SCAPE_API_KEY = os.getenv('SCAPE_API_KEY')
loginurl = 'https://wiki.glowbyteconsulting.com/dologin.action'
headers = {
    'user-agent': get_fake_browser_headers(SCAPE_API_KEY)['result'][0]['user-agent']}

print(headers)

url = 'https://wiki.glowbyteconsulting.com/pages/viewpage.action?pageId=197230835'
s = requests.session()
response = s.post(loginurl, headers=headers, data=payload)
print(f"Status code: {response.status_code}")
print('='*100)

parsed_birthdays = parse_user_data(response.text)

pprint(parsed_birthdays)

dt = datetime.strftime(datetime.now(), '%Y%m%d_%H%M_%S')
filename = f"{dt}.json"
full_path = os.path.join(os.getcwd(), 'json', filename)

with open(full_path, 'w', encoding='utf-8') as ff:
    json.dump(parsed_birthdays, ff, ensure_ascii=False)
