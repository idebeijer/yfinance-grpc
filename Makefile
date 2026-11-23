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
install: ## Install the package and dev dependencies
	uv sync

.PHONY: generate
generate: ## Generate protobuf code from .proto files
	buf generate

.PHONY: proto
proto: generate ## Alias for generate

.PHONY: run
run: ## Run the gRPC server locally (port: GRPC_PORT, default 50059)
	uv run yfinance-grpc --port $(GRPC_PORT)

.PHONY: example
example: ## Run the Python client example (needs a running server)
	uv run python examples/client_example.py

##@ Testing

.PHONY: test
test: ## Run unit tests (no server or network needed)
	uv run pytest

.PHONY: test-integration
test-integration: ## Run integration tests (needs `make run` in another terminal)
	uv run pytest -m integration

.PHONY: test-all
test-all: ## Run unit and integration tests
	uv run pytest -m ""

##@ Quality

.PHONY: lint
lint: ## Lint Python (ruff) and protos (buf)
	uv run ruff check .
	uv run ruff format --check .
	buf lint

.PHONY: typecheck
typecheck: ## Type-check Python (mypy)
	uv run mypy

.PHONY: format
format: ## Format Python and proto files
	uv run ruff check --fix .
	uv run ruff format .
	buf format -w

.PHONY: check
check: lint typecheck test ## Run every check CI runs except integration tests

.PHONY: breaking
breaking: ## Check for breaking changes in proto files
	buf breaking --against '.git#branch=main'

.PHONY: clean
clean: ## Remove caches and build artifacts
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache build dist

##@ Build

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
all: install generate check ## Install, generate and run all checks
