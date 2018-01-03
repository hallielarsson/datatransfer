import requests, json

config = {}
with open('config.json') as configFile:
  config = json.load(configFile)

params = {'_LOGIN[username]' : config['username'],
 '_LOGIN[password]': config['password'], '_LOGIN[returnMethod]' : 'POST',
 '_LOGIN[format]' : 'application/json'}

headers={ 'Content-Type':'application/json' }
req = requests.post(config['url'] + "/relationships?format=json", params = params, headers=headers)

newdata = []
i = 0

def saveData(data):
  for p in data:
    print(p)
    p["Notes"] = "test"
    p["Label"] = "comrade"
    send = {'data' : [p] }
    req = requests.post(config['url'] + "/relationships/save?include=Label",
      params= params,
      data=json.dumps(send),
      headers=headers,
      )
    print(req)
    #newdata.append(p)

saveData(req.json()["data"])

#print json.dumps(newdata)
