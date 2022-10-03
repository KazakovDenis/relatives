run:
	uvicorn main:app

precommit:
	flake8
	isort .

DIST_DIR="dist"
BACKEND_ZIP="relatives_backend.img"
COMPOSE_FILE="docker-compose.yml"
BACKEND_IMAGE="relatives_backend:latest"
ARCHIVE="relatives.tar.gz"
SSH_HOST="vps"

build:
	docker compose -f ${COMPOSE_FILE} build backend
	docker save ${BACKEND_IMAGE} -o ${DIST_DIR}/${BACKEND_ZIP}
	cp ${COMPOSE_FILE} ${DIST_DIR}/${COMPOSE_FILE}
	tar -C ${DIST_DIR} -czvf ${DIST_DIR}/${ARCHIVE} ${BACKEND_ZIP} ${COMPOSE_FILE}
	rm ${DIST_DIR}/${BACKEND_ZIP} ${DIST_DIR}/${COMPOSE_FILE}
	@echo "Done!"

upload:
	scp ${DIST_DIR}/${ARCHIVE} ${SSH_HOST}:
	rm ${DIST_DIR}/${ARCHIVE}
	@echo "Done!"
