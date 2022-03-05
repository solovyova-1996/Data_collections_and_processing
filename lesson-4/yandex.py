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
from transliterate import translit

client = MongoClient('localhost', 27017)
database = client['news_db']
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
url = 'https://yandex.ru/news'
response = requests.get(url, headers=headers)
dom = html.fromstring(response.text)
news = dom.xpath(
    "//div[contains(@class,'news-top-flexible-stories')]//a[@class='mg-card__source-link']")
list_news = list()


def main():
    for item in news:
        link = item.xpath(".//@href")[0]
        origin = item.xpath(".//@aria-label")[0].split(':')[1]
        name = link.replace('_', ' ')
        start = name.find('story') + 6
        end = name.find('--')
        name = translit(name[start:end], 'ru')
        list_news.append({'name': name, 'link': link, 'origin': origin})
        try:
            database.yandex.insert_one(
                {'_id': name, 'name': name, 'link': link, 'origin': origin})
        except DuplicateKeyError:
            print(f"Новость {name} уже существует")


if __name__ == '__main__':
    main()
    # pprint(list_news)
    pprint([news for news in database.yandex.find({})])
