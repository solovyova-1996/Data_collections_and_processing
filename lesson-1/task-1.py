# 1. Посмотреть документацию к API GitHub, разобраться как вывести список
# репозиториев для конкретного пользователя, сохранить JSON-вывод в файле *.json.

import requests
from json import loads

# запрос имени пользователя
name_user = input('Чтобы посмотреть список репозиториев пользователя,'
                  ' введите имя пользователя: ')


# мой репозиторий, для теста
# name_user = 'solovyova-1996'

# формирование url для запроса репозиториев, которые принадлежат пользователю
url = f"https://api.github.com/users/{name_user}/repos?type=owner"


# формирование url для запроса всех репозиториев пользователя
# url = f"https://api.github.com/users/{name_user}/repos"


# отправка запроса на Github
response = requests.get(url)

# Проверка статуса ответа, если пользователь не зарегистрирован на github
# программа завершается
if not response.ok:
    print(f'Пользователь: {name_user} не зарегистрирован на Github')
    exit(1)

# получение ответа в виде строки
response_str = response.content

# запись ответа в файл
with open('github_data.json', 'wb') as file:
    file.write(response_str)

# чтение ответа из файла и создание Python объекта из json
with open('github_data.json', 'r') as file:
    response = file.read()
    repo_list_all_info = loads(response)

# создание списка название репозиториев пользователя
repo_name_list = [repo['name'] for repo in repo_list_all_info]

print(f'Список репозиториев пользователя: {name_user}\n'
      f'Количество репозиториев: {len(repo_name_list)}\n'
      f'Репозитории: ')
for num, repo in enumerate(repo_name_list, start=1):
    print(f'{num}) {repo}')
