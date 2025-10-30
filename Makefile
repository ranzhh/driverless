SHELL := /bin/bash

help:
	@grep -E '^[.a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# Install dependencies using Homebrew on macOS
install:
	brew install cmake
	brew install pkg-config
	brew install opencv

# Build the project (from scratch)
build:
	mkdir -p build
	cd build && cmake ..
	cd build && make

clean:
	rm -rf build

# Run the first task (loading and displaying an image)
task1:
	./build/task1

task2:
	./build/task2

run:
	./build/driverless

serve:
	./start.sh