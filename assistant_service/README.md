# Assistant service

### Generating client and server code

path \assistant_service

### LLM
* `python -m grpc_tools.protoc -I../common/protos --python_out=./src/grpc_generated --grpc_python_out=./src/grpc_generated ../common/protos/llm.proto`
#### EncoderService

`python -m grpc_tools.protoc -I../common/protos --python_out=./src/grpc_generated --grpc_python_out=./src/grpc_generated ../common/protos/encoder.proto`

#### SimilaritySearchService
`python -m grpc_tools.protoc -I../common/protos --python_out=./src/grpc_generated --grpc_python_out=./src/grpc_generated ../common/protos/similarity_search.proto`


### mongo
`docker run \
  --name mongodb \
  -e MONGO_INITDB_ROOT_USERNAME=user \
  -e MONGO_INITDB_ROOT_PASSWORD=1234 \
  -e MONGO_INITDB_DATABASE=test \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:8.0.1-noble`