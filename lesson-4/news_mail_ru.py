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
url = 'https://news.mail.ru/'
response = requests.get(url, headers=headers)
dom = html.fromstring(response.text)
news = dom.xpath("//div[contains(@class,'daynews__')]")
list_news = list()


def handler_name(name_news):
    return name_news.replace('\xa0', ' ').strip()


def main():
    for item in news:
        name_news = handler_name(item.xpath(".//span/text()")[0])
        link = item.xpath(".//a/@href")[0]
        response_item = requests.get(link, headers)
        dom_item = html.fromstring(response_item.text)
        date = dom_item.xpath("//span[contains(@class,'js-ago')]/@datetime")[0]
        origin_link = dom_item.xpath(
            "//a[contains(@class,'link color_gray breadcrumbs__link')]/@href")[
            0]
        list_news.append(
            {'name_news': name_news,
             'link': link,
             'date': date,
             'origin_link': origin_link})
        try:
            database.mail.insert_one(
                {'_id': name_news,
                 'name_news': name_news,
                 'link': link,
                 'date': date,
                 'origin_link': origin_link})
        except DuplicateKeyError:
            print(f"Новость {name_news} уже существует")


if __name__ == '__main__':
    main()
    result_db = [news for news in database.mail.find({})]
    pprint(list_news)
    # pprint(result_db)
