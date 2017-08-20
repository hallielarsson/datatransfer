import requests, json

config = {}
with open('config.json') as configFile:
  config = json.load(configFile)

params = {'_LOGIN[username]' : config['username'],
 '_LOGIN[password]': config['password'], '_LOGIN[returnMethod]' : 'POST',
 '_LOGIN[format]' : 'application/json'}
req = requests.post(config['url'] + "/people/json", data = params)
print req.content
out = req.json()


newdata = []
for p in out["data"]:
  if(p["LastName"] == "Larsson"):
    p["LastName"] = "Larson"
    print p