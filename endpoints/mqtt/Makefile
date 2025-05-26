.PHONY: build test clean

build:
	docker build -t mqtt-mock -f docker/Dockerfile .

test:
	ansible-playbook -i ../inventory.ini ansible/test.yml

clean:
	docker rmi -f mqtt-mock || true
