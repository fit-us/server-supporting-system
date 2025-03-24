.PHONY: chat-build chat-start cbt-bot-start start-all

# Go 기반 chat 서비스 빌드
chat-build:
	@echo "=========================================="
	@echo "Building chat service (Go)..."
	@echo "=========================================="
	cd chat/cmd && go build -o chat-service main.go

# Go 기반 chat 서비스 실행
chat-start: chat-build
	@echo "=========================================="
	@echo "Starting chat service (Go)..."
	@echo "=========================================="
	cd chat/cmd && ./chat-service

# Python 기반 CBT Bot 서비스 실행
cbt-bot-start:
	@echo "=========================================="
	@echo "Starting CBT Bot service (Python)..."
	@echo "=========================================="
	cd cbt-bot && py main.py

# 두 서비스를 모두 실행
start-all: chat-start cbt-bot-start
	@echo "=========================================="
	@echo "Starting all services..."
	@echo "=========================================="
