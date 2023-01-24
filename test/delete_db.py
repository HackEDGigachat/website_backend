import pymongo

import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import storage

user_msg_col = storage.get_msg_col()
gpt_msg_col = storage.get_gpt_msg_col()
user_msg_col.delete_many({})
gpt_msg_col.delete_many({})