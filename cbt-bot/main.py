from cbt_bot_llm import CBTBot

if __name__ == "__main__":
    bot = CBTBot()

    while True:
        # 사용자로부터 메시지 입력 받기
        user_message = input("사용자: ")
        if user_message.lower() == "exit":  # 사용자가 'exit' 입력 시 종료
            break

        # 봇의 응답 출력
        response = bot.invoke(user_message)
        print(f"봇: {response.content}")