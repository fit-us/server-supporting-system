import grpc
import time
import logging
from concurrent import futures
from cbt_bot_llm import CBTBotLLM
from cbt_bot_proto import cbt_bot_llm_pb2, cbt_bot_llm_pb2_grpc
from logging_config import setup_logging

class CBTBotServicer(cbt_bot_llm_pb2_grpc.CBTBotServiceServicer):
    def __init__(self):
        self.bot = CBTBotLLM()
        logging.info("CBTBotServicer 초기화 완료")

    def Chat(self, request, context):
        logging.info(f"Chat 요청 수신: user_id={request.user_id}, message={request.message}")
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
            logging.info(f"Chat 응답 생성: {cbt_response}")
            return cbt_bot_llm_pb2.ChatResponse(cbtDetails=cbt_response)
        except Exception as e:
            logging.error(f"Chat 처리 중 오류 발생: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return cbt_bot_llm_pb2.ChatResponse()

def serve():
    setup_logging()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # 최대 10개 동시 처리
    cbt_bot_llm_pb2_grpc.add_CBTBotServiceServicer_to_server(CBTBotServicer(), server)
    server.add_insecure_port("[::]:50051")  # 포트 50051에서 실행
    server.start()
    logging.info("CBTBot gRPC 서버 실행 중...")
    
    try:
        while True:
            time.sleep(86400)  # 하루 동안 실행 유지
    except KeyboardInterrupt:
        server.stop(0)
        logging.info("서버 종료됨.")

if __name__ == "__main__":
    serve()