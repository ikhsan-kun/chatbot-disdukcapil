from app.chatbot.chatbot_ai import chatbot_response

while True:

    tanya = input("Anda: ")

    jawab = chatbot_response(tanya)

    print("Bot:", jawab)