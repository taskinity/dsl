.PHONY: build test clean

build:
	docker build -t http-mock -f docker/Dockerfile .

test:
	ansible-playbook -i ../inventory.ini ansible/test.yml

clean:
	docker rmi -f http-mock || true
