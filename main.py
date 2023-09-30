import collections
import json
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from lxml import html, etree
from dotenv import load_dotenv


def get_fake_browser_headers(api_key: str):
    response = requests.get(
        url='https://headers.scrapeops.io/v1/browser-headers',
        params={'api_key': api_key, 'num_headers': '1'})
    return response.json()


def generate_urls(year = 2022):
    urls = list()
    current_year = int(datetime.strftime(datetime.now(), '%Y'))
    for year in range(current_year, year-1, -1):
        for month in range(0, 13):
            current_url = f"https://wiki.glowbyteconsulting.com/rest/ia/1.0/pagetree/blog/subtree?spaceKey=IT&groupType=2&groupValue={month}%2F{year}"
            urls.append(current_url)
    return urls


def parse_pages_with_birthdays(session: requests.Session, urls: list[str]) -> list[str]:
    pages_with_birthday = list()
    for url in urls:
        response = session.get(url)
        if response.status_code == 200:
            data = response.json()
            for page in data:
                if 'Дни рождения' in page['title']:
                    pages_with_birthday.append(page)
    return pages_with_birthday


def parse_user_data(txt: str) -> list:
    tree = html.fromstring(txt)

    cells = tree.xpath(
        ".//table[contains(@class, 'confluenceTable')]//td[contains(@class, 'confluenceTd')]")

    users_json = list()
    if cells:
        for i, cell in enumerate(cells):
            current_user = dict()

            birth_day = cell.xpath(".//strong/text()")
            current_user.setdefault('day_of_birth', birth_day)

            img = cell.xpath(".//img/@data-image-src")
            current_user.setdefault('img', img)

            current_user['name_rus'] = cell.xpath('.//a/text()')
            link = cell.xpath(".//a")
            if isinstance(link, list) and len(link) > 0:
                for attrib, value in link[0].attrib.items():
                    current_user[attrib] = value

            users_json.append(current_user)

    return users_json


def get_year(tree):
    title = tree.xpath('.//meta[@name="wikilink"]/@content')
    pattern = '/(\d{4})/'
    matches = re.search(pattern, title[0])
    if matches:
        return int(matches[1])
    return False


def get_session():
    loginurl = 'https://wiki.glowbyteconsulting.com/dologin.action'
    payload = {"os_username": os.getenv('USER_NAME'),
               "os_password": os.getenv('USER_PASSWORD'), "login": "Войти",
               "os_destination": "/pages/viewpage.action?pageId=200938851"}
    s = requests.session()
    response = s.post(loginurl, data=payload, headers=headers)
    if response.status_code == 200:
        return s
    return False


def check_page(txt: str):
    tree = html.fromstring(txt)
    if 'Дни рождения' in tree.xpath('.//h1[@id="title-text"]/a/text()'):
        return True


def save_raw_content(content: str, postfix: str):
    current_dt = datetime.strftime(datetime.now(),
                                     '%Y-%m-%d-%H-%M-%S')
    log_filename = f"{current_dt}_{postfix}.html"
    with open(log_filename, 'a') as f:
        f.write(content)


if __name__ == '__main__':
    load_dotenv()
    dt_for_name = f"{datetime.strftime(datetime.now(), '%Y%m%d_%H%M_%S')}"
    json_filename = os.path.join(os.getcwd(), 'json', f"{dt_for_name}.json")

    loginurl = 'https://wiki.glowbyteconsulting.com/dologin.action'
    payload = {"os_username": os.getenv('USER_NAME'),
               "os_password": os.getenv('USER_PASSWORD'), "login": "Войти",
               "os_destination": "/pages/viewpage.action?pageId=200938851"}

    headers = {'user-agent':
                   get_fake_browser_headers(os.getenv('SCAPE_API_KEY'))[
                       'result'][0]['user-agent']}

    # генерируем адреса постов по шаблону
    blog_urls = generate_urls(year=2023)
    print(*blog_urls, sep='\n')

    # получаем только адреса постов с днями рождениями

    # создаем сессиию, в ней логинимся один раз, а потом всем функциям передаем контекст этой сессии
    # s = requests.session()
    # response = s.post(loginurl, data=payload, headers=headers)
    # if response.status_code == 200:
    #     print("we're logged in!")
    users_data = list()
    s = get_session()
    if not s:
        raise Exception("some shit with Session")

    birthdays_pages = parse_pages_with_birthdays(session=s, urls=blog_urls)
    print(f"just birthday blog pages: {len(birthdays_pages)}")
    # birthdays_pages = [{'url': '/pages/viewpage.action?pageId=197230835',
    #                     'title': 'just for test'}]
    result = list()
    for page in birthdays_pages:
        payload['os_destination'] = page['url']
        current_page_url = f'https://wiki.glowbyteconsulting.com{page["url"]}'
        print(f"{page['title']} - {current_page_url}")
        try:
            r = s.get(current_page_url, headers=headers)
            r.raise_for_status()
        except Exception as e:
            save_raw_content(r.content, 'error')
            print(e, e.args)

        else:
            current_page_data = parse_user_data(r.text)
            if current_page_data:
                print(f"Current page data length: {len(current_page_data)}")
                result.append(current_page_data)
            else:
                print(f"Page {page['title']} - {page['url']} is broken")
                save_raw_content(r.text, page['title'])
        time.sleep(0.5)

    result = str(result).replace('][', ',')
    with open(json_filename, 'a', encoding='utf-8') as ff:
        json.dump(result, ff, indent=4, ensure_ascii=False)
