# Text Vector Service

### Generating client and server code

`python -m grpc_tools.protoc -I./common/protos --python_out=./text_vector_service/src/grpc_generated --grpc_python_out=./text_vector_service/src/grpc_generated ./common/protos/encoder.proto`