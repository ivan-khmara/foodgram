# Foodgram – онлайн сервис для публикации рецептов
```
host:  130.193.41.20
login: admin
pass:  qwER1234
```
# Доступные эндпоинты
## Пользователи
| Наименование               |Тип запроса |URL                       | Доступ                |
|:---------------------------|:-----------|:-------------------------|:----------------------|
| Список пользователей       |GET         | /api/users/              | Token                 |
| Регистрация пользователя   |POST        | /api/users/              | Token                 |
| Профиль пользователя       |GET         | /api/users/{id}/         | Token                 |
| Текущий пользователь       |GET         | /api/users/me/           | Token                 |
| Изменение пароля           |GET         | /api/users/set_password/ | Token                 |
| Получить токен авторизации |POST        | /api/auth/token/login/   |                       |
| Удаление токена            |POST        | /api/auth/token/logout/  | Token                 |

## Теги
| Наименование               |Тип запроса |URL                       | Доступ                |
|:---------------------------|:-----------|:-------------------------|:----------------------|
| Cписок тегов               | GET        | /api/tags/               |                       |
| Получение тега             | GET        | /api/tags/{id}/          |                       |


## Ингредиенты
| Наименование               |Тип запроса |URL                       | Доступ                |
|:---------------------------|:-----------|:-------------------------|:----------------------|
| Список ингредиентов        |GET         |api/ingredients/          |                       |
| Получение ингредиента      |GET         |api/ingredients/{id}/     |                       |

## Рецепты
| Наименование               |Тип запроса |URL                       | Доступ                |
|:---------------------------|:-----------|:-------------------------|:----------------------|
| Список рецептов            | GET        | /api/recipes/            |                       |
| Создание рецепта           | POST       | /api/recipes/            | Token                 |
| Получение рецепта          | GET        | /api/recipes/{id}/       |                       |
| Обновление рецепта         | PATCH      | /api/recipes/{id}/       | Token, Author         |
| Удаление рецепта           | DEL        | /api/recipes/{id}/       | Token, Author         |

## Список покупок
| Наименование                     |Тип запроса |URL                       | Доступ                |
|:---------------------------------|:-----------|:-------------------------|:----------------------|
| Список покупок                   | GET        | /api/recipes/download_shopping_cart/| Token                 |
| Добавить рецепт в список покупок | POST       | /api/recipes/{id}/shopping_cart/    | Token                 |
| Удалить рецепт из списка покупок | DEL        | /api/recipes/{id}/shopping_cart/    | Token                 |

## Избранное
| Наименование                 |Тип запроса |URL                       | Доступ                |
|:-----------------------------|:-----------|:-------------------------|:----------------------|
| Добавить рецепт в избранное  | POST       | /api/recipes/{id}/favorite/| Token                 |
| Удалить рецепт из избранного | DEL        | /api/recipes/{id}/favorite/| Token                 |

## Подписки
| Наименование               |Тип запроса |URL                       | Доступ                |
|:---------------------------|:-----------|:-------------------------|:----------------------|
| Мои подписки               | GET        | /api/users/subscriptions/ | Token                 |
| Подписаться на пользователя| POST       | /api/users/{id}/subscribe/| Token                 |
| Отписаться от пользователя | DEL        | /api/users/{id}/subscribe/| Token                 |

## Запуск и наполнение базы данных
```
docker-compose up -d --build
docker-compose exec web python3 manage.py makemigrations
docker-compose exec web python3 manage.py migrate
docker-compose exec web python3 manage.py createsuperuser
docker-compose exec web python3 manage.py collectstatic --no-input
docker-compose exec web python3 manage.py loaddata dump.json
```
