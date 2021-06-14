from pymongo import MongoClient
mgClient = MongoClient("mongodb+srv://minhhien37:minhhien37@sandbox.wfgv5.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = mgClient.get_database('dadnDB')
records = db.DoAnDaNganh

data = {
    'name': 'Hien',
    'age': 21,
    'school': 'HCMUT'
}

#records.insert_one(data)
#records.find()
#records.find_one(param)
#records.update_one(param)
#records.delete_one(param)
print(records.count_documents({}))