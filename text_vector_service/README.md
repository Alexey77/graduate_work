# Text Vector Service

### Generating client and server code

## EncoderService

root path \text_vector_service

`python -m grpc_tools.protoc -I../common/protos --python_out=./src/grpc_generated --grpc_python_out=./src/grpc_generated ../common/protos/encoder.proto`

## SimilaritySearchService
`python -m grpc_tools.protoc -I../common/protos --python_out=./src/grpc_generated --grpc_python_out=./src/grpc_generated ../common/protos/similarity_search.proto`


`docker build -t llm_service .`

`docker run --env-file .env -p 50051:50051 llm_service`