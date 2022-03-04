import json
import pandas
import json

from pymongo.errors import DuplicateKeyError
from transliterate import translit
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
database = client['vacancy_db']

base_url = 'https://omsk.hh.ru/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}

vacancy_all_info_params = {
    'class': 'vacancy-serp-item vacancy-serp-item_redesigned'}
vacancy_title_params = {'data-qa': 'vacancy-serp__vacancy-title'}
vacancy_employer_params = {'data-qa': 'vacancy-serp__vacancy-employer'}
vacancy_address_params = {'data-qa': 'vacancy-serp__vacancy-address'}
vacancy_description_params = {'class': 'g-user-content'}
vacancy_name = input(
    'Введите название вакансии(название вакансии на латинице,например,слесарь-slesar,бухгалтер-bukhgalter,программист-programmist,стоматолог-stomatolog,учитель-uchitel): ')

add_url = f'/vacancies/{vacancy_name}'

vacancy_info_storage = list()


def handler_salary(salary_list):
    if 'от' in salary_list and len(salary_list) == 4:
        min_price = int(salary_list[1] + salary_list[2])
        max_price = None
        currency = salary_list[3][:3] if len(salary_list[3]) == 4 else \
        salary_list[3]
        return min_price, max_price, currency
    elif 'до' in salary_list and len(salary_list) == 4:
        min_price = None
        max_price = int(salary_list[1] + salary_list[2])
        currency = salary_list[3][:3] if len(salary_list[3]) == 4 else \
        salary_list[3]
        return min_price, max_price, currency
    elif len(salary_list) == 6:
        min_price = int(salary_list[0] + salary_list[1])
        max_price = int(salary_list[3] + salary_list[4])
        currency = salary_list[5][:3] if len(salary_list[5]) == 4 else \
        salary_list[5]
        return min_price, max_price, currency


def filling_dict(title, link, employer, vacancy_address, description, min_price,
                 max_price, currency):
    return {'title': title, 'link': link, 'employer': employer,
        'vacancy_address': vacancy_address, 'description': description,
        'min_price': min_price, 'max_price': max_price, 'currency': currency,
        'site': base_url, }


while add_url:
    response = requests.get(base_url + add_url, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    list_vacancy = dom.find_all('div', vacancy_all_info_params)
    try:
        add_url = dom.find('a', {'data-qa': 'pager-next'}).get('href')
    except AttributeError:
        add_url = None
    for vacancy in list_vacancy:
        vacancy_link_plus_title = vacancy.find('a', vacancy_title_params)
        link = vacancy_link_plus_title.get('href')
        title = vacancy_link_plus_title.getText()
        description = vacancy.find('div', vacancy_description_params).getText()
        try:
            employer = vacancy.find('a', vacancy_employer_params).getText()
            employer_list = employer.split()
            if len(employer_list) > 1:
                employer = ' '.join(employer_list)
        except AttributeError:
            employer = None
        try:
            vacancy_address = vacancy.find('div',
                                           vacancy_address_params).getText()
        except AttributeError:
            vacancy_address = None
        try:
            salary = vacancy.find('span', {
                'data-qa': 'vacancy-serp__vacancy-compensation'}).getText()
            salary_list = salary.split()
            l = handler_salary(salary_list)
            min_price, max_price, currency = l[0], l[1], l[2]
        except AttributeError:
            max_price = None
            min_price = None
            currency = None
        except TypeError:
            max_price = None
            min_price = None
            currency = None
        try:
            database.vacancy.insert_one(
                filling_dict(title, link, employer, vacancy_address,
                             description, min_price, max_price, currency))
        except DuplicateKeyError:
            print(filling_dict(title, link, employer, vacancy_address,
                               description, min_price, max_price, currency))
        vacancy_info_storage.append(
            filling_dict(title, link, employer, vacancy_address, description,
                         min_price, max_price, currency))

print(f'Количество вакансий: {len(vacancy_info_storage)}')
with open('vacancy.json', mode='w', encoding='utf-8') as file:
    json.dump(vacancy_info_storage, file)
with open('vacancy.json', mode='r', encoding='utf-8') as file:
    vac = json.load(file)
dataframe_vacacy = pandas.DataFrame(vac, columns=['title', 'link', 'employer',
                                                  'vacancy_address',
                                                  'description', 'min_price',
                                                  'max_price', 'currency',
                                                  'site'])
writer = pandas.ExcelWriter('vacancy.xlsx')
dataframe_vacacy.to_excel(writer)
writer.save()

salary = 30000
def searh_vacancy(salary):
    res = database.vacancy.find({'$or':[{'min_price': {'$gt': salary}}, {
        'max_price': {'$gt': salary}}]})
    res = [result for result in res]
    return res
res = searh_vacancy(salary)
print(res)
# print(dataframe_vacacy)
