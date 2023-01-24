import openai
import pymongo
import storage
import time
import os
from serpapi import GoogleSearch
import config
openai.api_key = config.open_api_key
# query the db for any new request 
# if yes
# send it to gpt
# get the response
# update the pymongo db
cur_document = 0

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
def main_query(doc): #doc is dictionary with user and name
  user_msg_col = storage.get_msg_col()
  gpt_msg_col = storage.get_gpt_msg_col()
  user_msg = storage.Message(doc["username"],int(time.time()),doc["text"])
  response = check_google_search(doc["text"])
  if(response == None):
    response = openai.Completion.create(model="text-davinci-001", prompt=doc["text"], temperature=0, max_tokens=50)
    resp_msg = storage.Message(doc["username"], int(time.time()), response["choices"][0]["text"])
  else:
    resp_msg = storage.Message(doc["username"], int(time.time()), response)
  # print(resp_msg.text)
 
  user_msg_col.insert_one(user_msg.get_document())
  gpt_msg_col.insert_one(resp_msg.get_document())
  return resp_msg.get_document()

if __name__ == "__main__":
  main_query()