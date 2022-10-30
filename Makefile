run:
	uvicorn main:app

migrate:
	cd src/backend && poetry run alembic upgrade head

style:
	poetry run flake8
	poetry run isort -c .

test:
	poetry run coverage run
	poetry run coverage report

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
	ssh -t ${SSH_HOST} "\
		tar -xvf ${ARCHIVE} && \
		docker compose -f ${REMOTE_COMPOSE} rm -f --stop backend && \
		docker rmi -f ${BACKEND_IMAGE} && \
		docker load -i ${DIST_DIR}/${BACKEND_ZIP} && \
		sudo mv ${DIST_DIR}/${LOCAL_COMPOSE} ${REMOTE_COMPOSE} && \
		rm -rf ${DIST_DIR} && \
		sudo rm -rf ${DIST_DIR}/static && \
		docker compose -f ${REMOTE_COMPOSE} up -d --force-recreate backend && \
		sleep 3 && \
		docker compose -f ${REMOTE_COMPOSE} cp backend:/app/static . \
	"
	@echo "Done!"

full_deploy: build upload deploy
