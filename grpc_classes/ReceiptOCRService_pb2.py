# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: ReceiptOCRService.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'ReceiptOCRService.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17ReceiptOCRService.proto\x12\x18\x66iores.ocr.receipt.proto\"4\n\x11ReceiptOCRRequest\x12\x0e\n\x06\x61\x63tion\x18\x01 \x01(\t\x12\x0f\n\x07payload\x18\x02 \x01(\t\"B\n\x12ReceiptOCRResponse\x12\x0c\n\x04\x63ode\x18\x01 \x01(\x05\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\t\x12\x10\n\x08metadata\x18\x03 \x01(\t2\x7f\n\x12ReceiptOCRServices\x12i\n\nReceiptOCR\x12+.fiores.ocr.receipt.proto.ReceiptOCRRequest\x1a,.fiores.ocr.receipt.proto.ReceiptOCRResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ReceiptOCRService_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_RECEIPTOCRREQUEST']._serialized_start=53
  _globals['_RECEIPTOCRREQUEST']._serialized_end=105
  _globals['_RECEIPTOCRRESPONSE']._serialized_start=107
  _globals['_RECEIPTOCRRESPONSE']._serialized_end=173
  _globals['_RECEIPTOCRSERVICES']._serialized_start=175
  _globals['_RECEIPTOCRSERVICES']._serialized_end=302
# @@protoc_insertion_point(module_scope)
