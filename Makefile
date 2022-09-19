run:
	uvicorn main:app

precommit:
	flake8
	isort .

DIST_DIR="dist"
BACKEND_ZIP="relatives_backend.img"
LOCAL_COMPOSE="docker-compose.yml"
BACKEND_IMAGE="relatives_backend:latest"
ARCHIVE="relatives.tar.gz"

build:
	docker compose -f ${LOCAL_COMPOSE} build backend
	docker save ${BACKEND_IMAGE} -o ${DIST_DIR}/${BACKEND_ZIP}
	cp ${LOCAL_COMPOSE} ${DIST_DIR}/${LOCAL_COMPOSE}
	tar -czvf ${DIST_DIR}/${ARCHIVE} ${DIST_DIR}/${BACKEND_ZIP} ${DIST_DIR}/${LOCAL_COMPOSE}
	rm ${DIST_DIR}/${BACKEND_ZIP} ${DIST_DIR}/${LOCAL_COMPOSE}
