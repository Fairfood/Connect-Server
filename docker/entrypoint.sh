#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate
python manage.py collectstatic --noinput


if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    echo "Creating super user $DJANGO_SUPERUSER_USERNAME"
    {
        python manage.py createsuperuser \
          --noinput \
          --username $DJANGO_SUPERUSER_USERNAME \
          --email $DJANGO_SUPERUSER_EMAIL 2>/dev/null &&
          echo  "Created super user $DJANGO_SUPERUSER_USERNAME"
    } || {
          echo  "User $DJANGO_SUPERUSER_USERNAME already exists. Skipping."
    }

fi

$@

exec "$@"
