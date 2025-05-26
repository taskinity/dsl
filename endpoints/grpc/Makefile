.PHONY: build test clean

build:
	docker build -t grpc-mock -f docker/Dockerfile .

test:
	ansible-playbook -i ../inventory.ini ansible/test.yml

clean:
	docker rmi -f grpc-mock || true

generate-protos:
	python -m grpc_tools.protoc -I protos/ --python_out=. --grpc_python_out=. protos/example.proto

run-server:
	cd docker && python server.py

run-client:
	cd docker && python client.py

docker-run:
	docker run -d --name grpc-mock -p 50051:50051 -p 8000:8000 grpc-mock

docker-logs:
	docker logs -f grpc-mock

docker-stop:
	docker stop grpc-mock || true

docker-rm:
	docker rm -f grpc-mock || true

docker-restart: docker-stop docker-rm docker-run
