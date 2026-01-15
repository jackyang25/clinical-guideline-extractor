.PHONY: start stop restart

# start docker containers
start:
	docker-compose up -d

# stop docker containers
stop:
	docker-compose down

# restart docker containers
restart:
	docker-compose restart
