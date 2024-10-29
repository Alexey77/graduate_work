# Assistant service

### Generating client and server code

path \assistant_service

### LLM
* `python -m grpc_tools.protoc -I../common/protos --python_out=./src/grpc_generated --grpc_python_out=./src/grpc_generated ../common/protos/llm.proto`