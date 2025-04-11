NETWORK=mcpnet

network:
	docker network create $(NETWORK) || true

build:
	docker build -t chat-mcp-server .

run: network
	docker run --rm -d --name mcp-server --network $(NETWORK) -p 8001:8001 --env-file .env chat-mcp-server

all: build run