# Text Vector Service

### Generating client and server code
__________________________
#### EncoderService

root path \text_vector_service

`python -m grpc_tools.protoc -I../common/protos --python_out=./src/grpc_generated --grpc_python_out=./src/grpc_generated ../common/protos/encoder.proto`

#### SimilaritySearchService
`python -m grpc_tools.protoc -I../common/protos --python_out=./src/grpc_generated --grpc_python_out=./src/grpc_generated ../common/protos/similarity_search.proto`


`docker build -t text_vector_service .`
`docker build -t text_vector_service2 .`


### Lets run this
service
`docker run --env-file .env -p 50051:50051 text_vector_service`

qdrant
`docker run -p 6333:6333 qdrant/qdrant`

______________________
!!!!!!!! не работает!!!!!!!!!!!!!
ETL test script
`docker run --env-file .env text_vector_service3 python3 src/_test_etl_qdrant.py`

!!!!!! работает !!!!!!!!!!
надо локально запускать
`венв, cd src, python _test_etl_qdrant.py`

### Клиент для теста сервиса
!!!!!!!! не работает!!!!!!!!!!!!!
`docker run --network text_vector_network --env-file .env service_client python3 src/async_client.py
`

!!!!!! работает !!!!!!!!!!
надо локально запускать
`венв, cd src, python async_client.py`