﻿# praktikum_new_diplom

```
 GET  http://localhost/api/users/              Список пользователей  AUTHORIZATIONS:Token integer; limit
 POST http://localhost/api/users/              Регистрация пользователя
 GET  http://localhost/api/users/{id}/         Профиль пользователя AUTHORIZATIONS:Token
 GET  http://localhost/api/users/me/           Текущий пользователь AUTHORIZATIONS:Token
 GET  http://localhost/api/users/set_password/ Изменение пароля AUTHORIZATIONS:Token
 
 
 POST http://localhost/api/auth/token/login/   Получить токен авторизации
 POST http://localhost/api/auth/token/logout/  Удаление токена  AUTHORIZATIONS:Token                                    
```

## Теги
```
 GET  http://localhost/api/tags/               Cписок тегов
 GET  http://localhost/api/tags/{id}/          Получение тега
```

## Ингредиенты
```
 GET  http://localhost/api/ingredients/        Список ингредиентов
 GET  http://localhost/api/ingredients/{id}/   Получение ингредиента
```

## Рецепты
```
 GET       http://localhost/api/recipes/           Список рецептов         Страница доступна всем пользователям. Доступна фильтрация по избранному, автору, списку покупок и тегам.
 POST      http://localhost/api/recipes/           Создание рецепта                                         Доступно только авторизованным пользователям
 GET       http://localhost/api/recipes/{id}/      Получение рецепта
 PATCH     http://localhost/api/recipes/{id}/      Обновление рецепта                                       Доступно только автору данного рецепта
 DEL       http://localhost/api/recipes/{id}/      Удаление рецепта                                         Доступно только автору данного рецепта
```

## Список покупок
```
 GET        http://localhost/api/recipes/download_shopping_cart/  Список покупок                            Доступно только авторизованным пользователям
 POST       http://localhost/api/recipes/{id}/shopping_cart/      Добавить рецепт в список покупок          Доступно только авторизованным пользователям
 DEL        http://localhost/api/recipes/{id}/shopping_cart/      Удалить рецепт из списка покупок          Доступно только авторизованным пользователям
```

## Избранное
```
 POST       http://localhost/api/recipes/{id}/favorite/          Добавить рецепт в избранное                Доступно только авторизованным пользователям
 DEL        http://localhost/api/recipes/{id}/favorite/          Удалить рецепт из избранного               Доступно только авторизованным пользователям
```

## Подписки
```
 GET        http://localhost/api/users/subscriptions/            Мои подписки                               Доступно только авторизованным пользователям
 POST       http://localhost/api/users/{id}/subscribe/           Подписаться на пользователя                Доступно только авторизованным пользователям
 DEL        http://localhost/api/users/{id}/subscribe/           Отписаться от пользователя                 Доступно только авторизованным пользователям
```
```
docker build -t ikhmara/backend .  
docker run --name web -it -p 8000:8000 ikhmara/backend


CMD python3 manage.py migrate
CMD python3 manage.py collectstatic --no-input

docker-compose up -d --build 
docker-compose exec web python3 manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python3 manage.py collectstatic --no-input


python manage.py dumpdata > dump.json

python3 manage.py shell  
# выполнить в открывшемся терминале:
>>> from django.contrib.contenttypes.models import ContentType
>>> ContentType.objects.all().delete()
>>> quit()

python manage.py loaddata dump.json
python manage.py pull_bd 
```