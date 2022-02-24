"""
Необходимо собрать информацию о вакансиях на вводимую должность
(используем input или через аргументы получаем должность) с сайтов HH(обязательно)
 и/или Superjob(по желанию). Приложение должно анализировать несколько страниц сайта
 (также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:
Наименование вакансии.
Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
Ссылку на саму вакансию.
Сайт, откуда собрана вакансия.
По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
Структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат
можно вывести с помощью dataFrame через pandas. Сохраните в json либо csv.
"""
import asyncio
import json
import pandas
import json
from transliterate import translit
import requests
from bs4 import BeautifulSoup

###########################   Параметры    ##############################
base_url = 'https://omsk.hh.ru/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
vacancy_all_info_params = {
    'class': 'vacancy-serp-item vacancy-serp-item_redesigned'}
vacancy_title_params = {'data-qa': 'vacancy-serp__vacancy-title'}
vacancy_employer_params = {'data-qa': 'vacancy-serp__vacancy-employer'}
vacancy_address_params = {'data-qa': 'vacancy-serp__vacancy-address'}
vacancy_description_params = {'class': 'g-user-content'}
######################     Список с итоговыми результатами  ####################
vacancy_all_list = list()


############################   Функции     #################################
def handler_salary(salary_list):
    """
    получает список полученный в результате split строки зарплаты и возвращает
    минимальную и максимальную зарплату и валюту
    :param salary_list: список полученный в результате split строки зарплаты
    :return: (min_price, max_price, currency)
    """
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
    '''
    Возвращает словарь состоящий из переданных в параметры значений
    :param title: название вакансии
    :param link: ссылка на вакансию
    :param employer: работадатель
    :param vacancy_address: местоположение вакансии(город)
    :param description: краткое описание вакансии
    :param min_price: минимальная зарплата
    :param max_price: максимальная зарплата
    :param currency: валюта
    :return:
    '''
    return {'title': title, 'link': link, 'employer': employer,
        'vacancy_address': vacancy_address, 'description': description,
        'min_price': min_price, 'max_price': max_price, 'currency': currency,
        'site': base_url, }


async def get_list_vacancy_dict(one_page, last_page, add_url):
    '''
    отправляет на сайт hh.ru на определенную вакансию и проходит по всем страницам этой вакансии
    :param one_page: номер страницы, с которой начинать парсинг
    :param last_page: номер страницы, до которой продолжать парсинг
    :param add_url: добавленный адрес, который содержит название вакансии, которое ввел пользователь
    :return: список словарей с информацией о вакансиях
    '''
    vacancy_info_storage = list()

    for page in range(one_page, last_page):
        params = {'page': page, 'hhtmFrom': 'vacancy_search_catalog'}
        response = requests.get(base_url + add_url, headers=headers,
                                params=params)
        dom = BeautifulSoup(response.text, 'html.parser')
        list_vacancy = dom.find_all('div', vacancy_all_info_params)
        for vacancy in list_vacancy:
            vacancy_link_plus_title = vacancy.find('a', vacancy_title_params)
            link = vacancy_link_plus_title.get('href')
            title = vacancy_link_plus_title.getText()
            description = vacancy.find('div',
                                       vacancy_description_params).getText()
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
            vacancy_info_storage.append(
                filling_dict(title, link, employer, vacancy_address,
                             description, min_price, max_price, currency))
    vacancy_all_list.extend(vacancy_info_storage)


def lst_namber_page(num):
    '''
    возвращает список с номерами страниц
    :param num: номер количества страниц
    :return:
    '''
    list_page = [page for page in range(0, num, 3)]
    if num not in list_page:
        list_page.pop()
        list_page.append(num)

    return list_page


def add_url_func():
    '''
    возвращает строку адреса с введенной пользователем вакансией
    :return:
    '''
    vacancy_name = input(
        'Введите название вакансии(название вакансии на латинице,например,слесарь-slesar,бухгалтер-bukhgalter,программист-programmist,стоматолог-stomatolog,учитель-uchitel): ')
    return f'/vacancies/{vacancy_name}'


async def event_loop():
    '''
    Событийный цикл
    :return:
    '''
    add_url = add_url_func()
    response = requests.get(base_url + add_url, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    last_page = int(dom.find_all('a', {'data-qa': 'pager-page'})[-1].getText())
    print(f'Количество страниц вакансий: {last_page}')
    list_page = lst_namber_page(last_page)
    # список асинхронных задач
    tasks = list()
    while list_page:
        # создание задачи
        task = asyncio.create_task(
            get_list_vacancy_dict(list_page.pop(0), list_page[0], add_url))
        tasks.append(task)
        if len(list_page) == 1:
            list_page.pop()
    await asyncio.wait(tasks)
# запуск программы
asyncio.run(event_loop())
print(f'Количество вакансий: {len(vacancy_all_list)}')
# запись вакансий в файл
with open('vacancy.json',mode='w',encoding='utf-8') as file:
    json.dump(vacancy_all_list,file)
# чтение из файла
with open('vacancy.json',mode='r',encoding='utf-8') as file:
    vac = json.load(file)
# создание фрейма для вывода данных и для записи их в exel
dataframe_vacacy = pandas.DataFrame(vac,columns=['title','link','employer','vacancy_address','description','min_price','max_price','currency','site'])
writer = pandas.ExcelWriter('vacancy.xlsx')
dataframe_vacacy.to_excel(writer)
writer.save()

print(dataframe_vacacy)