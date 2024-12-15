# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import grpc_classes.Scanit_OCRService_pb2 as Scanit__OCRService__pb2


class ScanitOCRServicesStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.AppCheck = channel.unary_unary(
                '/scanit.ocr.receipt.proto.ScanitOCRServices/AppCheck',
                request_serializer=Scanit__OCRService__pb2.AppCheckRequest.SerializeToString,
                response_deserializer=Scanit__OCRService__pb2.AppCheckResponse.FromString,
                )
        self.OCR = channel.unary_unary(
                '/scanit.ocr.receipt.proto.ScanitOCRServices/OCR',
                request_serializer=Scanit__OCRService__pb2.OCRRequest.SerializeToString,
                response_deserializer=Scanit__OCRService__pb2.OCRResponse.FromString,
                )


class ScanitOCRServicesServicer(object):
    """Missing associated documentation comment in .proto file."""

    def AppCheck(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def OCR(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ScanitOCRServicesServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'AppCheck': grpc.unary_unary_rpc_method_handler(
                    servicer.AppCheck,
                    request_deserializer=Scanit__OCRService__pb2.AppCheckRequest.FromString,
                    response_serializer=Scanit__OCRService__pb2.AppCheckResponse.SerializeToString,
            ),
            'OCR': grpc.unary_unary_rpc_method_handler(
                    servicer.OCR,
                    request_deserializer=Scanit__OCRService__pb2.OCRRequest.FromString,
                    response_serializer=Scanit__OCRService__pb2.OCRResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'scanit.ocr.receipt.proto.ScanitOCRServices', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ScanitOCRServices(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def AppCheck(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/scanit.ocr.receipt.proto.ScanitOCRServices/AppCheck',
            Scanit__OCRService__pb2.AppCheckRequest.SerializeToString,
            Scanit__OCRService__pb2.AppCheckResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def OCR(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/scanit.ocr.receipt.proto.ScanitOCRServices/OCR',
            Scanit__OCRService__pb2.OCRRequest.SerializeToString,
            Scanit__OCRService__pb2.OCRResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)