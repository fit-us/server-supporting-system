package main

import (
	"context"
	"fmt"
	"log"

	pb "fitus-chat-service/proto"

	"google.golang.org/grpc"
)

func main() {
    // gRPC 서버 주소
    serverAddr := "localhost:50051"

    // gRPC 연결 설정
    conn, err := grpc.Dial(serverAddr, grpc.WithInsecure())
    if err != nil {
        log.Fatalf("gRPC 연결 실패: %v", err)
    }
    defer conn.Close()

    // gRPC 클라이언트 생성
    client := pb.NewCBTBotServiceClient(conn)

    // 요청 생성
    req := &pb.ChatRequest{
        UserId:  12345,
        Message: "나 너무 우울하고 힘들어..  김대건이라는 사람이 나를 괴롭혀.. 못된 악덕 업주야",
    }

    // 서버 스트림 호출
    stream, err := client.Chat(context.Background(), req)
    if err != nil {
        log.Fatalf("Chat 호출 실패: %v", err)
    }

    // 스트림 응답 처리
    log.Println("서버 스트림 응답 시작:")
    for {
        resp, err := stream.Recv()
        if err != nil {
            if err.Error() == "EOF" {
                log.Println("서버 스트림 종료")
                break
            }
            log.Fatalf("스트림 응답 처리 중 오류 발생: %v", err)
        }

        // 스트림 응답 출력
        fmt.Printf("%s", resp.ConsultationResponse)
        if resp.CbtResponse != nil {
            fmt.Printf("\n\nCBT 질문: %s\n", resp)
        }
        if resp.AnalysisResponse != nil {
            fmt.Printf("\n\n분석 결과: %s\n", resp)
        }
    }
}