# Foodgram – онлайн сервис для публикации рецептов
```
host:  130.193.41.20
```
## Описание
Это онлайн-сервис, где пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Доступные эндпоинты
| Наименование               |Тип запроса |URL                       | Доступ                |
|:---------------------------|:-----------|:-------------------------|:----------------------|
| Список пользователей       |GET         | /api/users/              | Token                 |
| Регистрация пользователя   |POST        | /api/users/              | Token                 |
| Профиль пользователя       |GET         | /api/users/{id}/         | Token                 |
| Текущий пользователь       |GET         | /api/users/me/           | Token                 |
| Изменение пароля           |GET         | /api/users/set_password/ | Token                 |
| Получить токен авторизации |POST        | /api/auth/token/login/   |                       |
| Удаление токена            |POST        | /api/auth/token/logout/  | Token                 |
| Cписок тегов               | GET        | /api/tags/               |                       |
| Получение тега             | GET        | /api/tags/{id}/          |                       |
| Список ингредиентов        |GET         |api/ingredients/          |                       |
| Получение ингредиента      |GET         |api/ingredients/{id}/     |                       |
| Список рецептов            | GET        | /api/recipes/            |                       |
| Создание рецепта           | POST       | /api/recipes/            | Token                 |
| Получение рецепта          | GET        | /api/recipes/{id}/       |                       |
| Обновление рецепта         | PATCH      | /api/recipes/{id}/       | Token, Author         |
| Удаление рецепта           | DEL        | /api/recipes/{id}/       | Token, Author         |
| Список покупок                   | GET        | /api/recipes/download_shopping_cart/| Token                 |
| Добавить рецепт в список покупок | POST       | /api/recipes/{id}/shopping_cart/    | Token                 |
| Удалить рецепт из списка покупок | DEL        | /api/recipes/{id}/shopping_cart/    | Token                 |
| Добавить рецепт в избранное  | POST       | /api/recipes/{id}/favorite/| Token                 |
| Удалить рецепт из избранного | DEL        | /api/recipes/{id}/favorite/| Token                 |
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
