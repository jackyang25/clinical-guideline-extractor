.PHONY: start stop restart build

# start docker containers
start:
	docker-compose up -d

# stop docker containers
stop:
	docker-compose down

# restart docker containers (hot reload with volumes)
restart:
	docker-compose restart

# rebuild and start containers (for dependency changes)
build:
	docker-compose up -d --build
