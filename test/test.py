import pymongo
def get_url():
  url = "mongodb+srv://zxlim:Mongo1234@cluster0.1p0y0.mongodb.net/?retryWrites=true&w=majority"
  return url
client = pymongo.MongoClient(get_url())
print(list(client["gigachat"]["users"].find({})))