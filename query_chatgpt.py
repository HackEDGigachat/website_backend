#this would hopefully be replaced when chatgpt releases an api

from revChatGPT.Official import Chatbot
import config
import pymongo
import storage
import time
import os
from serpapi import GoogleSearch
import config
from ai_gen_pic import ai_gen_pic
import uuid
from newsapi import NewsApiClient
from datetime import datetime, timedelta
newsapi = NewsApiClient(api_key=config.news_api)
def start_chatgpt():
    chatbot = Chatbot(api_key = config.open_api_key)
    return chatbot

def create_new_conv(chatbot):
    uuid_chat = str(uuid.uuid4())
    chatbot.make_conversation(uuid_chat)
    return uuid_chat

def send_message(message,conversation_id,chatbot):
    response = chatbot.ask(message, conversation_id=conversation_id)["choices"][0]["text"]
    return response

class WeatherGoogle():
  def __init__(self, answer_box):
    temperature = answer_box["temperature"]
    unit = answer_box["unit"]
    precipitation = answer_box["precipitation"]
    humidity = answer_box["humidity"]
    wind = answer_box["wind"]
    self.result = f"The weather is {temperature} {unit}, the precipitation is {precipitation}, humidity is {humidity}, wind speed is {wind}"
  def get_answer(self):
    return self.result

class TimeGoogle():
  def __init__(self, answer_box):
    result = answer_box["result"]
    self.result = f"Time is {result}"
  def get_answer(self):
    return self.result

class Calculator():
  def __init__(self, answer_box):
    result = answer_box["result"]
    self.result = f"The value is {result}"
  def get_answer(self):
    return self.result

def check_google_search(text):
  search = GoogleSearch({
    "q": text, 
    "location": "Edmonton,Alberta,Canada",
    "api_key": config.google_api_key
  })
  result = search.get_dict()
  if "answer_box" in result:
    if result["answer_box"]["type"] == "weather_result":
      return WeatherGoogle(result["answer_box"]).get_answer()
    elif result["answer_box"]["type"] == "local_time":
      return TimeGoogle(result["answer_box"]).get_answer()
    elif result["answer_box"]["type"] == "calculator_result":
      return Calculator(result["answer_box"]).get_answer()
    else:
      return None
  else:
    return None
def add_chat_hist(user_msg,bot_msg,chatbot):
  chatbot.prompt.add_to_chat_history("User: "
            + user_msg
            + "\n\n\n"
            + "ChatGPT: "
            + bot_msg
            + "<|im_end|>\n",)
  return chatbot

def main_query(doc,chatbot,conversation_id): #doc is dictionary with user and name
  user_msg_col = storage.get_msg_col()
  gpt_msg_col = storage.get_gpt_msg_col()
  user_msg_time = int(time.time())
  response_type = "String"
  if(doc["text"].lower().split()[:2] == ['ai', 'picture']):
    prompt = " ".join(doc["text"].lower().split()[2:])
    picture = ai_gen_pic(prompt)["data"][0]["url"]
    print(picture)
    resp_msg = storage.Message(user_name = doc["username"], time_stamp = int(time.time()), text = picture,conversation_id = conversation_id)
    chatbot = add_chat_hist(doc["text"],"picture url from DALL·E"+str(resp_msg),chatbot)

  elif(doc["text"].lower().split()[0]=="news" ):
    prompt = " ".join(doc["text"].lower().split()[1:])
    all_articles = newsapi.get_everything(q=prompt,from_param=datetime.today().date() - timedelta(days=1),
                                      to=datetime.today().date(),sources='bbc-news,abc-news,bloomberg,espn,fox-sports,google-news')['articles'][:9]
    response_type ="news"
    resp_msg = storage.Message(user_name = doc["username"], time_stamp = int(time.time()), text = all_articles,conversation_id =conversation_id,response_type=response_type)
    chatbot = add_chat_hist(doc["text"],"here is the a set of news articles you asked for"+str(all_articles),chatbot)

  else:
    response_google = check_google_search(doc["text"])


    if(response_google == None): 
      response_gpt = send_message(doc["text"],conversation_id,chatbot) 
      resp_msg = storage.Message(user_name = doc["username"], time_stamp = int(time.time()), text = response_gpt,conversation_id =conversation_id,response_type=response_type)

    else:
      
      resp_msg = storage.Message(user_name = doc["username"], time_stamp = int(time.time()), text = response_google,conversation_id = conversation_id)
      chatbot = add_chat_hist(doc["text"],response_google,chatbot)

    

  user_msg = storage.Message(user_name = doc["username"],time_stamp = user_msg_time,text =doc["text"],conversation_id = conversation_id)
  
  # print(resp_msg.text)
 
  user_msg_col.insert_one(user_msg.get_document())
  gpt_msg_col.insert_one(resp_msg.get_document())
  return resp_msg.get_document(),response_type

if __name__ == "__main__":
  chatbot = start_chatgpt()
  doc ={
    "username" :"rpi_user",
    "text" : "news bitcoin"
  }
  answer,response_type = main_query(doc,chatbot,"22")
  print(response_type)