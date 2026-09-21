.PHONY: demo build clean install-deps linux help

demo:
	chmod +x demo.sh
	./demo.sh

build: linux

linux:
	chmod +x build.sh
	./build.sh

clean:
	rm -rf dist/ build/ __pycache__ *.spec

install-deps:
	pip3 install -r requirements.txt

help:
	@echo "Available targets:"
	@echo "  demo         - Run demo launcher"
	@echo "  build        - Build Linux binary"
	@echo "  linux        - Build Linux binary"
	@echo "  clean        - Remove build artifacts"
	@echo "  install-deps - Install Python dependencies"
