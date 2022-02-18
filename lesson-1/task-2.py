# 2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
# Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
# Если нет желания заморачиваться с поиском, возьмите API вконтакте
# (https://vk.com/dev/first_guide). Сделайте запрос, чтобы получить список
# всех сообществ на которые вы подписаны.

from json import loads
import requests

# токен бессрочный
token = '769c9a7c5e54fb70e9da138b190e49fbe7a89830889ac5590f4a6ff150c2cf013a8b67c5682dbf4c5b9c5'
user_id = 257305135
method_groups_get = 'groups.get'
method_get_profile_info = 'account.getProfileInfo'
url = 'https://api.vk.com/method/'

params = {
    'access_token': token,
    'v': '5.131',
    'extended': 1,
    'user_id': user_id
}

params_only_token = {
    'access_token': token,
    'v': '5.131'
}

response_group = requests.get(f'{url}{method_groups_get}', params=params)
encoding_response = response_group.encoding
with open('data.json', 'wb') as file:
    file.write(response_group.content)

# чтение ответа из файла и создание Python объекта из json
with open('data.json', 'r', encoding=encoding_response) as file:
    response = file.read()
    list_info_groups_all = loads(response)

# список названий сообществ
list_name_group = [group['name'] for group in list_info_groups_all['response']['items']]

# запрос данных профиля пользователя для получения имени и фамилии(для красивого вывода)
response_name_user = requests.get(url+method_get_profile_info,params=params_only_token)
response_name_user_json = response_name_user.json()

# вывод результатов
print(f" Количество сообществ пользователя-"
      f"({response_name_user_json['response']['first_name']} "
      f"{response_name_user_json['response']['last_name']}) : "
      f"{list_info_groups_all['response']['count']}")
for num,name_group in enumerate(list_name_group,start=1):
    print(f'{num} {name_group}')
