.PHONY: build run all

build:
	docker build -t chat-mcp-server .

run:
	docker run -d -p 8001:8001 --env-file .env chat-mcp-server

all: build run