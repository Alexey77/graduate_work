# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: similarity_search.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'similarity_search.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17similarity_search.proto\x12\x11similarity_search\"@\n\rSearchRequest\x12\x0c\n\x04text\x18\x01 \x01(\t\x12\x12\n\ncollection\x18\x02 \x01(\t\x12\r\n\x05limit\x18\x03 \x01(\x05\";\n\x0e\x46ragmentResult\x12\x0c\n\x04text\x18\x01 \x01(\t\x12\x0c\n\x04meta\x18\x02 \x01(\t\x12\r\n\x05score\x18\x03 \x01(\x02\"N\n\x0eSearchResponse\x12<\n\x11similar_fragments\x18\x01 \x03(\x0b\x32!.similarity_search.FragmentResult2x\n\x17SimilaritySearchService\x12]\n\x16SearchSimilarFragments\x12 .similarity_search.SearchRequest\x1a!.similarity_search.SearchResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'similarity_search_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SEARCHREQUEST']._serialized_start=46
  _globals['_SEARCHREQUEST']._serialized_end=110
  _globals['_FRAGMENTRESULT']._serialized_start=112
  _globals['_FRAGMENTRESULT']._serialized_end=171
  _globals['_SEARCHRESPONSE']._serialized_start=173
  _globals['_SEARCHRESPONSE']._serialized_end=251
  _globals['_SIMILARITYSEARCHSERVICE']._serialized_start=253
  _globals['_SIMILARITYSEARCHSERVICE']._serialized_end=373
# @@protoc_insertion_point(module_scope)
