import grpc
import time
from concurrent import futures
from cbt_bot_llm import CBTBotLLM
from cbt_bot_proto import cbt_bot_llm_pb2, cbt_bot_llm_pb2_grpc

class CBTBotServicer(cbt_bot_llm_pb2_grpc.CBTBotServiceServicer):
    def __init__(self):
        self.bot = CBTBotLLM()

    def Chat(self, request, context):
        try:
            response = self.bot.invoke(request.user_id, request.message)
            cbt_response = cbt_bot_llm_pb2.CBTBotResponse(
                cbtCategory=response.cbt_category,
                consultationStage=response.consultation_stage,
                triggeringSituation=response.triggering_situation,
                automaticThoughts=response.automatic_thoughts,
                emotions=response.emotions,
                intensityOfEmotion=response.intensity_of_emotion,
                underlyingBeliefs=response.underlying_beliefs,
                cbtQuestion=response.cbt_question,
                userResponse=response.user_response,
                therapistNotes=response.therapist_notes,
                defaultResponse=response.default_response
            )
            return cbt_bot_llm_pb2.ChatResponse(cbtDetails=cbt_response)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return cbt_bot_llm_pb2.ChatResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # 최대 10개 동시 처리
    cbt_bot_llm_pb2_grpc.add_CBTBotServiceServicer_to_server(CBTBotServicer(), server)
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