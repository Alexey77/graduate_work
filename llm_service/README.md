# LLM Service

### Generating client and server code

llm_service

`python -m grpc_tools.protoc -I../common/protos --python_out=./src/grpc_generated --grpc_python_out=./src/grpc_generated ../common/protos/llm.proto`


`cd llm_service`
`export PYTHONPATH=$PWD`
`python src/server.py`

