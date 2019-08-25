makemigrations:
	sudo docker-compose run --rm dev_api python imports/manage.py makemigrations

migrate:
	sudo docker-compose run --rm dev_api python imports/manage.py migrate


mm: makemigrations migrate
	echo "Done"
