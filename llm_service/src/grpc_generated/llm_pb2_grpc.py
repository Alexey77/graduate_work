# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import llm_pb2 as llm__pb2

GRPC_GENERATED_VERSION = '1.67.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in llm_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class LlmServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetCompletion = channel.unary_unary(
                '/llmservice.LlmService/GetCompletion',
                request_serializer=llm__pb2.LLMRequest.SerializeToString,
                response_deserializer=llm__pb2.LLMResponse.FromString,
                _registered_method=True)
        self.GetFunctions = channel.unary_unary(
                '/llmservice.LlmService/GetFunctions',
                request_serializer=llm__pb2.LLMFunctionRequest.SerializeToString,
                response_deserializer=llm__pb2.LLMFunctionResponse.FromString,
                _registered_method=True)


class LlmServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetCompletion(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetFunctions(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_LlmServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetCompletion': grpc.unary_unary_rpc_method_handler(
                    servicer.GetCompletion,
                    request_deserializer=llm__pb2.LLMRequest.FromString,
                    response_serializer=llm__pb2.LLMResponse.SerializeToString,
            ),
            'GetFunctions': grpc.unary_unary_rpc_method_handler(
                    servicer.GetFunctions,
                    request_deserializer=llm__pb2.LLMFunctionRequest.FromString,
                    response_serializer=llm__pb2.LLMFunctionResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'llmservice.LlmService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('llmservice.LlmService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class LlmService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetCompletion(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/llmservice.LlmService/GetCompletion',
            llm__pb2.LLMRequest.SerializeToString,
            llm__pb2.LLMResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetFunctions(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/llmservice.LlmService/GetFunctions',
            llm__pb2.LLMFunctionRequest.SerializeToString,
            llm__pb2.LLMFunctionResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
