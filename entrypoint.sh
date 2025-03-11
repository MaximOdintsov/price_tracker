#!/bin/sh
set -e

echo "Ожидание PostgreSQL на $DB_HOST:$DB_PORT..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "PostgreSQL доступен!"

echo "Выполняем миграции..."
python manage.py migrate

echo "Запуск Daphne..."
exec daphne -b 0.0.0.0 -p 8000 price_tracker.routing:application