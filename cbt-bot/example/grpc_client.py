import grpc
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cbt_bot_proto import cbt_bot_pb2,cbt_bot_pb2_grpc
def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = cbt_bot_pb2_grpc.CBTBotServiceStub(channel)
        
        while True:
            user_input = input("사용자: ")
            if user_input.lower() == "exit":  # exit 입력 시 종료
                break

            response = stub.Chat(cbt_bot_pb2.ChatRequest(message=user_input))
            print(f"봇 응답: {response.response}")

if __name__ == "__main__":
    run()
