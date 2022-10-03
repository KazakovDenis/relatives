run:
	uvicorn main:app

precommit:
	flake8
	isort .

DIST_DIR="dist"
BACKEND_ZIP="relatives_backend.img"
LOCAL_COMPOSE="docker-compose.yml"
REMOTE_COMPOSE="/opt/relatives/docker-compose.yml"
BACKEND_IMAGE="relatives_backend:latest"
ARCHIVE="relatives.tar.gz"
SSH_HOST="vps"

build:
	docker compose -f ${LOCAL_COMPOSE} build backend
	docker save ${BACKEND_IMAGE} -o ${DIST_DIR}/${BACKEND_ZIP}
	cp ${LOCAL_COMPOSE} ${DIST_DIR}/${LOCAL_COMPOSE}
	tar -C ${DIST_DIR} -czvf ${DIST_DIR}/${ARCHIVE} ${BACKEND_ZIP} ${LOCAL_COMPOSE}
	rm ${DIST_DIR}/${BACKEND_ZIP} ${DIST_DIR}/${LOCAL_COMPOSE}
	@echo "Done!"

upload:
	scp ${DIST_DIR}/${ARCHIVE} ${SSH_HOST}:
	rm ${DIST_DIR}/${ARCHIVE}
	@echo "Done!"

deploy:
	ssh -t ${SSH_HOST} "\
		tar -xvf ${ARCHIVE} && \
		docker compose -f ${PROD_COMPOSE} rm --stop backend && \
		docker rmi ${BACKEND_IMAGE} && \
		docker load -i ${BACKEND_ZIP} && \
		sudo mv ${LOCAL_COMPOSE} ${REMOTE_COMPOSE} && \
		rm ${BACKEND_ZIP} ${BOT_ARCHIVE} && \
		docker compose -f ${PROD_COMPOSE} up -d --force-recreate backend \
	"
