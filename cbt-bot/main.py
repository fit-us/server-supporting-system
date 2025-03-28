import asyncio
import grpc
import time
import logging
from concurrent import futures
from cbt_bot_llm import CBTBotLLM
from cbt_bot_proto import cbt_bot_llm_stream_pb2, cbt_bot_llm_stream_pb2_grpc
from logging_config import setup_logging
class CBTBotServicer(cbt_bot_llm_stream_pb2_grpc.CBTBotServiceServicer):
    def __init__(self):
        self.bot = CBTBotLLM()
        logging.info("CBTBotServicer 초기화 완료")

    async def handle_consultation(self, chunk):
        return cbt_bot_llm_stream_pb2.ChatResponse(consultationResponse=chunk)

    async def handle_cbt(self, chunk):
        responses = []
        for question in chunk.cbt_question:
            responses.append(
                cbt_bot_llm_stream_pb2.ChatResponse(
                    cbtResponse=cbt_bot_llm_stream_pb2.CBTQuestion(
                        type=question.type,
                        question=question.question,
                        choices=question.choices
                    )
                )
            )
        return responses

    async def handle_analysis(self, chunk):
        return cbt_bot_llm_stream_pb2.ChatResponse(
            analysisResponse=cbt_bot_llm_stream_pb2.ConsultationAnalysisReport(
                cbtCategory=chunk.cbt_category or "",
                consultationStage=chunk.consultation_stage or "",
                triggeringSituation=chunk.triggering_situation or "",
                automaticThoughts=chunk.automatic_thoughts or "",
                emotions=chunk.emotions or [],
                intensityOfEmotion=chunk.intensity_of_emotion or {},
                underlyingBeliefs=chunk.underlying_beliefs or "",
                userResponse=chunk.user_request or "",
                therapistNotes=chunk.therapist_notes or ""
            )
        )

    async def Chat(self, request, context):
        logging.info(f"Chat 요청 수신: user_id={request.user_id}, message={request.message}")
        try:
            async for prompt_type, chunk in self.bot.invoke_stream(request.user_id, request.message):
                if chunk is None:
                    logging.warning(f"chunk가 None입니다. prompt_type: {prompt_type}")
                    continue

                if prompt_type == "consultation":
                    yield await self.handle_consultation(chunk)
                elif prompt_type == "cbt":
                    for response in await self.handle_cbt(chunk):
                        yield response
                elif prompt_type == "analysis":
                    yield await self.handle_analysis(chunk)
                await asyncio.sleep(0)
        except Exception as e:
            logging.error(f"Chat 처리 중 오류 발생: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
async def serve():
    setup_logging()
    # 비동기 서버 구현을 위해 grpcio-tools로 생성된 코드를 사용하는 경우, 비동기 서버를 사용할 수 있어야 합니다.
    server = grpc.aio.server()  # 비동기 서버
    cbt_bot_llm_stream_pb2_grpc.add_CBTBotServiceServicer_to_server(CBTBotServicer(), server)
    server.add_insecure_port("[::]:50051")
    await server.start()  # 비동기 방식으로 서버 시작
    logging.info("CBTBot gRPC 서버 실행 중...")
    
    try:
        while True:
            await asyncio.sleep(86400)  # 비동기 방식으로 대기
    except KeyboardInterrupt:
        await server.stop(0)  # 서버 종료
        logging.info("서버 종료됨.")

if __name__ == "__main__":
    asyncio.run(serve())  # 이벤트 루프에서 실행
