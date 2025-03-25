import grpc
from concurrent import futures
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cbt_bot_proto import cbt_bot_pb2,cbt_bot_pb2_grpc
# gRPC 서비스 구현
class CBTBotServicer(cbt_bot_pb2_grpc.CBTBotServiceServicer):
    def Chat(self, request, context):
        print(f"[클라이언트 요청] {request.message}")
        response_text = f"CBTBot 응답: {request.message}에 대해 답변드립니다."
        return cbt_bot_pb2.ChatResponse(response=response_text)

# gRPC 서버 실행
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # 최대 10개 동시 처리
    cbt_bot_pb2_grpc.add_CBTBotServiceServicer_to_server(CBTBotServicer(), server)
    server.add_insecure_port("[::]:50051")  # 포트 50051에서 실행
    server.start()
    print("CBTBot gRPC 서버 실행 중...")
    
    try:
        while True:
            time.sleep(86400)  # 하루 동안 실행 유지
    except KeyboardInterrupt:
        server.stop(0)
        print("서버 종료됨.")

if __name__ == "__main__":
    serve()
