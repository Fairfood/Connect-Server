web:
	docker compose -p trace_connect -f ./docker/docker-compose.yml up --build

djshell:
	docker compose -p trace_connect -f ./docker/docker-compose.yml exec web python manage.py shell_plus --settings=trace_connect.settings.local

shell:
	docker compose -p trace_connect -f ./docker/docker-compose.yml exec web /bin/bash

test:
	docker compose -p trace_connect -f ./docker/docker-compose.yml exec web python manage.py test --settings=trace_connect.settings.local

down:
	docker compose -p trace_connect -f ./docker/docker-compose.yml down

logs:
	docker compose -p trace_connect -f ./docker/docker-compose.yml logs -f

db:
	docker compose -p trace_connect -f ./docker/docker-compose.yml exec db -it -u postgres postgres psql
