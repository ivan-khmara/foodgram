import csv
import json
import sqlite3

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Заполняет базу данных'

    def handle(self, *args, **options):

        DELIMITER = ','  # Разделитель в файле с данными
        id_ingredient = 0
        to_ingredient = []
        # Подключаемся к БД в файле db.sqlite3
        con = sqlite3.connect('db.sqlite3')
        cur = con.cursor()

        # Открываем на чтение файл static/data/users.csv
        with open('../data/ingredients.json', 'r', encoding="utf8") as fin:
            file_data = json.load(fin)
            for i in file_data:
                id_ingredient += 1
                to_ingredient.append((id_ingredient, i.get('name'), i.get('measurement_unit')))
        try:
            cur.executemany(
                "INSERT INTO app_ingredient VALUES (?, ?, ?);",
                to_ingredient)
            print('База данных заполнена.')
        except Exception:

            print('При заполнении базы данных возникли ошибки.')

        con.commit()
        con.close()
