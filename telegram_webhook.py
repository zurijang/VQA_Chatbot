import telegram
from VQA_Chatbot import settings
bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
# updates = bot.getUpdates()

# bot.set_webhook("https://vqachatbot.herokuapp.com/Chatbot/webhook")
bot.set_webhook("https://0aa70e4d74f7.ngrok.io/Chatbot/webhook")

# updater = Updater(token=settings.TELEGRAM_TOKEN)
# dispatcher = updater.dispatcher # 이벤트가 왔을때 처리해주는 객체


# def help(bot, update):
#     bot.send_message(chat_id=update.message.chat_id, text=\
#         '''사용순서는 다음과 같습니다.
#         1. 이미지 업로드
#         2. 질문 입력
#         3. 질문에 대한 답변 입력
# 사진으로 판단할 수 있는 질문과 답을 입력해야합니다.
# 이미지를 업로드하면 질문 입력이 시작됩니다.''')

# help_handler = CommandHandler('help', help)
# dispatcher.add_handler(help_handler)

# updater.start_polling()