from revChatGPT.Official import Chatbot
api_key = "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"

x = Chatbot(api_key = api_key)
x.make_conversation("1")
print(x.ask("call me bob"))
x.make_conversation("2")
x.ask("call me zi",conversation_id="2")
x.ask("what is my name?",conversation_id="1")["choices"]["text"]

