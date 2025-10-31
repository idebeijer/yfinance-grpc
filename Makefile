# Image URL to use for building/pushing image targets
IMG ?= yfinance-grpc:latest

# CONTAINER_TOOL defines the container tool to be used for building images.
CONTAINER_TOOL ?= docker

# Container name for running the server
CONTAINER_NAME ?= yfinance-grpc

# Port to expose
GRPC_PORT ?= 50059

# Setting SHELL to bash allows bash commands to be executed by recipes.
SHELL = /usr/bin/env bash -o pipefail
.SHELLFLAGS = -ec

##@ General

# The help target prints out all targets with their descriptions organized
# beneath their categories. The categories are represented by '##@' and the
# target descriptions by '##'. The awk command is responsible for reading the
# entire set of makefiles included in this invocation, looking for lines of the
# file as xyz: ## something, and then pretty-format the target and help.
.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

.PHONY: install
install: ## Install Python dependencies using uv
	uv sync

.PHONY: generate
generate: ## Generate protobuf code from .proto files
	buf generate

.PHONY: proto
proto: generate ## Alias for generate

.PHONY: run
run: ## Run the gRPC server locally
	uv run python main.py

.PHONY: test
test: ## Run the client example
	uv run python client_example.py

.PHONY: lint
lint: ## Run buf lint on proto files
	buf lint

.PHONY: format
format: ## Format proto files
	buf format -w

.PHONY: breaking
breaking: ## Check for breaking changes in proto files
	buf breaking --against '.git#branch=main'

.PHONY: clean
clean: ## Clean generated files and cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

##@ Build

.PHONY: build
build: generate ## Generate proto files (no compilation needed for Python)

.PHONY: docker-build
docker-build: ## Build docker image
	$(CONTAINER_TOOL) build -t ${IMG} .

.PHONY: docker-push
docker-push: ## Push docker image
	$(CONTAINER_TOOL) push ${IMG}

# PLATFORMS defines the target platforms for the image to be built to provide support to multiple architectures.
PLATFORMS ?= linux/arm64,linux/amd64

.PHONY: docker-buildx
docker-buildx: ## Build and push docker image for cross-platform support
	# Copy existing Dockerfile and insert --platform=${BUILDPLATFORM}
	sed -e '1 s/\(^FROM\)/FROM --platform=\$$\{BUILDPLATFORM\}/; t' -e ' 1,// s//FROM --platform=\$$\{BUILDPLATFORM\}/' Dockerfile > Dockerfile.cross
	- $(CONTAINER_TOOL) buildx create --name yfinance-grpc-builder
	$(CONTAINER_TOOL) buildx use yfinance-grpc-builder
	- $(CONTAINER_TOOL) buildx build --push --platform=$(PLATFORMS) --tag ${IMG} -f Dockerfile.cross .
	- $(CONTAINER_TOOL) buildx rm yfinance-grpc-builder
	rm Dockerfile.cross

##@ Docker Compose

.PHONY: up
up: ## Start services with docker-compose
	docker compose up -d

.PHONY: down
down: ## Stop services with docker-compose
	docker compose down -v

.PHONY: logs
logs: ## View docker-compose logs
	docker compose logs -f

##@ All

.PHONY: all
all: install generate ## Install dependencies and generate proto files
