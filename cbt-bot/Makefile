.PHONY: proto-build venv

proto-build:
    @echo "=========================================="
    @echo "Compiling protobuf files..."
    @echo "=========================================="
	py -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. cbt_bot_llm.proto

venv:
	@echo "=========================================="
	@echo "Creating virtual environment..."
	@echo "=========================================="
	source venv/bin/activate