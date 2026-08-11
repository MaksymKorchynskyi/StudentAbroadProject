.PHONY: test-data build up down restart logs shell bash

test-data:
	docker-compose exec web python manage.py setup_test_data

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec web python manage.py shell

bash:
	docker-compose exec web bash
