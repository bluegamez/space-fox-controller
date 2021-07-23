from concurrent import futures
import time
import math
import logging

import grpc

import controller_pb2
import controller_pb2_grpc

class SpaceFoxServicer(controller_pb2_grpc.SpaceFoxServicer):
    """Provides methods that implement functionality of route guide server."""

    def __init__(self):
        pass

    def ControllerActions(self, request_iterator, context):
        for action in request_iterator:
            print(action)
        
        return controller_pb2.EndOfStream()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    controller_pb2_grpc.add_SpaceFoxServicer_to_server(
        SpaceFoxServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
