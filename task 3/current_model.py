from langchain.chat_models import ChatGoogleGenerativeAI
chat = ChatGoogleGenerativeAI()
print(chat.list_models())
