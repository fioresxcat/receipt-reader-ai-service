# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Scanit_OCRService.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17Scanit_OCRService.proto\x12\x18scanit.ocr.receipt.proto\"2\n\x05\x45rror\x12\x12\n\nerror_code\x18\x01 \x01(\x05\x12\x15\n\rerror_message\x18\x02 \x01(\t\"5\n\x0f\x41ppCheckRequest\x12\x0e\n\x06images\x18\x01 \x03(\t\x12\x12\n\nrequest_id\x18\x02 \x01(\t\"g\n\x10\x41ppCheckResponse\x12.\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x1f.scanit.ocr.receipt.proto.Error\x12\x11\n\tjson_data\x18\x02 \x01(\t\x12\x10\n\x08metadata\x18\x03 \x01(\t\" \n\nOCRRequest\x12\x12\n\nrequest_id\x18\x01 \x01(\t\"b\n\x0bOCRResponse\x12.\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x1f.scanit.ocr.receipt.proto.Error\x12\x11\n\tjson_data\x18\x02 \x01(\t\x12\x10\n\x08metadata\x18\x03 \x01(\t2\xce\x01\n\x11ScanitOCRServices\x12\x63\n\x08\x41ppCheck\x12).scanit.ocr.receipt.proto.AppCheckRequest\x1a*.scanit.ocr.receipt.proto.AppCheckResponse\"\x00\x12T\n\x03OCR\x12$.scanit.ocr.receipt.proto.OCRRequest\x1a%.scanit.ocr.receipt.proto.OCRResponse\"\x00\x42\x33\n\x18scanit.ocr.receipt.protoB\x15ScanitOCRServiceProtoP\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Scanit_OCRService_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\030scanit.ocr.receipt.protoB\025ScanitOCRServiceProtoP\001'
  _globals['_ERROR']._serialized_start=53
  _globals['_ERROR']._serialized_end=103
  _globals['_APPCHECKREQUEST']._serialized_start=105
  _globals['_APPCHECKREQUEST']._serialized_end=158
  _globals['_APPCHECKRESPONSE']._serialized_start=160
  _globals['_APPCHECKRESPONSE']._serialized_end=263
  _globals['_OCRREQUEST']._serialized_start=265
  _globals['_OCRREQUEST']._serialized_end=297
  _globals['_OCRRESPONSE']._serialized_start=299
  _globals['_OCRRESPONSE']._serialized_end=397
  _globals['_SCANITOCRSERVICES']._serialized_start=400
  _globals['_SCANITOCRSERVICES']._serialized_end=606
# @@protoc_insertion_point(module_scope)