VERSION=0.0.1

install:
	sudo apt install gettext
	poetry install

run:
	uvicorn main:app

makemigrations:
	cd src/backend && poetry run alembic revision --autogenerate -m "xxx_message"

migrate:
	cd src/backend && poetry run alembic upgrade head

style:
	poetry run flake8
	poetry run isort -c .

test:
	poetry run coverage run
	poetry run coverage report

PO_FILE=src/backend/locale/ru/LC_MESSAGES/messages.po
MO_FILE=src/backend/locale/ru/LC_MESSAGES/messages.mo

DIST_DIR=dist
BACKEND_ZIP=relatives_backend.img
LOCAL_COMPOSE=docker-compose.yml
REMOTE_DIR=/opt/relatives
REMOTE_COMPOSE=${REMOTE_DIR}/docker-compose.yml
BACKEND_IMAGE=relatives_backend:latest
ARCHIVE=relatives.tar.gz
SSH_HOST=vps

build:
	docker compose -f ${LOCAL_COMPOSE} build backend
	docker save ${BACKEND_IMAGE} -o ${DIST_DIR}/${BACKEND_ZIP}
	cp ${LOCAL_COMPOSE} ${DIST_DIR}/${LOCAL_COMPOSE}
	tar -czvf ${DIST_DIR}/${ARCHIVE} ${DIST_DIR}/${BACKEND_ZIP} ${DIST_DIR}/${LOCAL_COMPOSE}
	rm ${DIST_DIR}/${BACKEND_ZIP} ${DIST_DIR}/${LOCAL_COMPOSE}
	@echo "Done!"

upload:
	scp ${DIST_DIR}/${ARCHIVE} ${SSH_HOST}:
	rm ${DIST_DIR}/${ARCHIVE}
	@echo "Done!"

deploy:
	ssh ${SSH_HOST} "\
		tar -xvf ${ARCHIVE} && \
		docker compose -f ${REMOTE_COMPOSE} rm -f --stop backend && \
		docker rmi -f ${BACKEND_IMAGE} && \
		docker load -i ${DIST_DIR}/${BACKEND_ZIP} && \
		mv ${DIST_DIR}/${LOCAL_COMPOSE} ${REMOTE_COMPOSE} && \
		rm -rf ${DIST_DIR} && \
		rm -rf ${DIST_DIR}/static && \
		docker compose -f ${REMOTE_COMPOSE} up -d --force-recreate backend && \
		docker compose -f ${REMOTE_COMPOSE} exec backend alembic upgrade head && \
		rm -rf ${REMOTE_DIR}/static && \
		docker compose -f ${REMOTE_COMPOSE} cp backend:/app/static . \
	"
	@echo "Done!"

full_deploy: build upload deploy

tunnel:
	ssh -L 127.0.0.1:5432:127.0.0.1:5432 vps -N

DUMP_LOC=/opt/relatives/dump/postgresql/relatives.tar

pgdump:
	ssh ${SSH_HOST} "\
		cd /opt/relatives && \
		docker compose exec postgres sh -c \"pg_dump -U relatives -F t relatives > /opt/dump/relatives.tar\" \
	"
	scp ${SSH_HOST}:${DUMP_LOC} ./dump/postgresql
	@echo "Done!"

loaddump: migrate
	pg_restore -d relatives -c -U relatives -h localhost -p 5432 ./dump/postgresql/relatives.tar
