NAME=media-analyzer
TAG=$$(git log -1 --pretty=%h)
IMG=${NAME}:${TAG}
LATEST=${NAME}:latest

processing:
	kubectl apply -f infrastructure.yaml
	-kubectl delete job publisher
	sleep 15
	kubectl apply -f processing.yaml

build: Dockerfile
	# @docker build -t ${IMG} -f Dockerfile.build .
	@docker build -t ${IMG} .
	@docker tag ${IMG} ${LATEST}

push:
	@docker push ${NAME}

login:
	@docker log -u ${DOCKER_USER} -p ${DOCKER_PASS}

publish:
	pipenv run python -m media_analyzer.core.publish &

pull:
	pipenv run python -m media_analyzer.core.pull &

process:
	pipenv run python -m media_analyzer.core.process &

store:
	pipenv run python -m media_analyzer.core.store &
