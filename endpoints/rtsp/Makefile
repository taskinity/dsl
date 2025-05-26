.PHONY: build test clean

build:
	docker build -t rtsp-mock -f docker/Dockerfile .

test:
	ansible-playbook -i ../inventory.ini ansible/test.yml

clean:
	docker rmi -f rtsp-mock || true
	rm -f test_stream.mp4
