# Написать приложение, которое собирает основные новости с сайта на выбор
# news.mail.ru, lenta.ru, yandex-новости. Для парсинга использовать XPath.
# Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.
# Сложить собранные новости в БД - проверка есть ли запись в бд
from pprint import pprint
from lxml import html
import requests
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient('localhost', 27017)
database = client['news_db']
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
url = 'https://lenta.ru'
response = requests.get(url, headers=headers)
dom = html.fromstring(response.text)
name_origin = 'https://lenta.ru/'
news = dom.xpath("//a[contains(@class,'topnews')]")
list_news = list()


def handler_date(date_list):
    if not 'https:' in date_list:
        try:
            return f'{date_list[4]}-{date_list[3]}-{date_list[2]}'
        except IndexError:
            return None
    else:
        date_start = date_list[5].find('-') + 1
        date_end = date_list[5].find('.')
        return date_list[5][date_start:date_end]


def handler_link(link):
    if 'https' in link:
        return link
    else:
        return url + link


def main():
    for item in news:
        try:
            name_news = item.xpath(".//span/text()")[0]
        except IndexError:
            name_news = None
        link = item.xpath("./@href")[0]
        date_list = link.split('/')
        info_dict = {'name_origin': name_origin, 'name_news': name_news,
                     'link': handler_link(link),
                     'date': handler_date(date_list)}
        if name_news:
            list_news.append(info_dict)
            try:
                database.lenta.insert_one(
                    {'_id': name_news, 'name_origin': name_origin,
                     'name_news': name_news, 'link': handler_link(link),
                     'date': handler_date(date_list)})
            except DuplicateKeyError:
                print(f"Новость {name_news} уже существует")


if __name__ == '__main__':
    main()
    # pprint(list_news)
    res_db = database.lenta.find({})
    res_db_list = [news for news in res_db]
    pprint(res_db_list)
