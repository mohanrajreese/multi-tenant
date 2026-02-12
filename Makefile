.PHONY: up down build migrate test shell

up:
	docker-compose up

down:
	docker-compose down

build:
	docker-compose build

migrate:
	docker-compose run --rm web python manage.py migrate
	docker-compose run --rm web python manage.py migrate_schemas

test:
	docker-compose run --rm web python manage.py test

shell:
	docker-compose run --rm web python manage.py shell

docs:
	mkdocs serve
