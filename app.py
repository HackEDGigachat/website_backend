from flask import Flask, jsonify, request, send_file
from client import send_query
from storage import get_user_col , get_gpt_msg_col,get_msg_col
import pdb
import json
from query_chatgpt import main_query, start_chatgpt,create_new_conv
import config
app = Flask(__name__)
gpt_count = 0


def updateDictionary(user,collection_msg):
  for message in collection_msg:
    message["from"] = user
    del message['_id']
  return collection_msg
@app.route('/api/create_user', methods=['POST'])
def create_user():
  print(request)

  if request.method == 'POST':
    print("goes here")
    data = request.get_json()
    name = data["name"]
    username = data["username"]
    password = data["password"]
    query = {
      "username" : username,
    }
    collection = get_user_col()
    doc = collection.find(query)
    if(len(list(doc) )==0):
      collection.insert_one({
        "name": name,
        "username" : username,
        "password" : password,
      })
      return jsonify({"valid":True})
    else:
      return jsonify({"valid":False})

@app.route('/api/get_history', methods=['POST'])
def get_history():
  print(request)

  if request.method == 'POST':
    print("goes here")
    data = request.get_json()
    username = data["username"]
    query = {
      "username" : username,
    }
    user_msg_col = list(get_msg_col().find(query))
    gpt_msg_col = list(get_gpt_msg_col().find(query))
    user_msg_col = updateDictionary(0,user_msg_col) #0 = user , 1 = chat
    gpt_msg_col = updateDictionary(1,gpt_msg_col)
    combined_msgs = gpt_msg_col+user_msg_col
    sorted_msgs = sorted(combined_msgs,key=lambda d:d['timestamp'])
    convo_id_added ={}
    group_sort_msg = []
    for x in range(len(sorted_msgs)):
      if(sorted_msgs[x]['conversation_id'] not in convo_id_added):
        group_sort_msg.append([sorted_msgs[x]['conversation_id'],[sorted_msgs[x]]])
        convo_id_added[sorted_msgs[x]['conversation_id']]  = len(group_sort_msg)-1

      else:
        index = convo_id_added[sorted_msgs[x]['conversation_id']]
        group_sort_msg[index][1].append(sorted_msgs[x])
    



    if(len(sorted_msgs) == 0):
      conversation_id = create_new_conv(config.chatbot)
      group_sort_msg =[[conversation_id,[[]]]]
    print(group_sort_msg)
    return jsonify({"sorted_msgs":group_sort_msg})
    
@app.route('/api/check_user', methods=['POST'])
def check_cred():
  print(request)

  if request.method == 'POST':
    print("goes here")
    data = request.get_json()
    query = {
      "username" : data["username"],
      "password" : data["password"]
    }
    collection = get_user_col()
    doc = collection.find(query)
    if(len(list(doc)) == 1):
      return jsonify({"valid":True})
    else:
      return jsonify({"valid":False})

@app.route('/api/new_conversation', methods=['POST'])
def new_conversation():
  if request.method == 'POST':
    print("creating a new ConvoId!")
    conversation_id = create_new_conv(chatbot=config.chatbot)
    print("conversation_id")
    return jsonify({'conversation_id':conversation_id})


@app.route('/api/reply', methods=['POST', 'GET'])
def reply():
  if request.method == 'POST':
    data = request.get_json()
    print(data)
    query=data["message"]
    username = data["username"] 
    doc ={
      "username" :username,
      "text" : query
    }
    answer = main_query(doc=doc,chatbot=config.chatbot,conversation_id=data["conversation_id"])
    print(answer['text'])
    return jsonify({'reply': answer['text']}), 200
    


@app.route('/api/data', methods=['POST', 'GET'])
def get_data():
  if request.method == 'POST':
    data = request.get_json()
    print(data)
    return jsonify({'received_data': data}), 200
  elif request.method == 'GET':
    return jsonify({'received_data': 'Hello from the backend!'}), 200

@app.route('/video')
def send_video():
    return send_file('resources/login_video.mp4', mimetype='video/mp4')




if __name__ == "__main__":
  config.chatbot = start_chatgpt()

  app.run(debug=True, host='0.0.0.0') #putting debug to false will make stuff run once