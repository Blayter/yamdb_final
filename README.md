# Api_yamdb

## Workflow status badge

![example workflow](https://github.com/Blayter/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

## Description

Проект YaMDb собирает отзывы пользователей на произведения. Произведения делятся на категории: «Книги», «Фильмы», «Музыка».

## Env file srtucture

DB_ENGINE
DB_NAME
POSTGRES_USER
POSTGRES_PASSWORD
DB_HOST
DB_PORT

SECRET_KEY

ALLOWED_HOSTS

## Docker install manual

Visit https://www.digitalocean.com/community/tutorials/docker-ubuntu-18-04-1-ru

## Cmd for clone image

```bash
docker pull blayter/infra_sp2:v1
```

## Cmd for start app

```bash
docker-compose up -d --build 
```

## Cmd for filling database
```bash
docker-compose exec web python manage.py migrate
```

## Cmd for create superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

## Cmd for collect static
```bash
docker-compose exec web python manage.py collectstatic --no-input
```

## Cmd for stop and delete containers
```bash
docker-compose down -v
```

## Technology 

- Docker
- Nginx
- Gunicorn
- Postgres
- Django

## Project address 

http://84.201.175.62/admin/

## Author

Mishenin Sergey