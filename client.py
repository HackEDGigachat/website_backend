import storage
import time
import sys
import pymongo

user = "rpi_user"
# check if it could run
def send_query(request_text):
  msg_col = storage.get_msg_col()
  epoch = int(time.time())
  user_msg = storage.Message(user, epoch, request_text)
  msg_doc = user_msg.get_document()
  msg_col.insert_one(msg_doc)
  gpt_col = storage.get_gpt_msg_col()
  timeout = False
  doc = gpt_col.find_one({"username": user, "timestamp": {"$gt": epoch}})
  # Need to check to see if the response exists
  # timeout for 2 mins
  while timeout == False and doc == None:
    if (int(time.time()) - epoch) >= (30):
      # print("Timed out")
      timeout = True
    doc = gpt_col.find_one({"username": user, "timestamp": {"$gt": epoch}})
  
  if doc == None: 
    # print("Timeout")
    return None
  else:
    return doc["text"]
  
 

if __name__ == "__main__":
  print(send_query("what is the weather"))