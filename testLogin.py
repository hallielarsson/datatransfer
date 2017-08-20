import requests, json

config = {}
with open('config.json') as configFile:
  config = json.load(configFile)

params = {'_LOGIN[username]' : config['username'],
 '_LOGIN[password]': config['password'], '_LOGIN[returnMethod]' : 'POST',
 '_LOGIN[format]' : 'application/json'}
req = requests.post(config['url'] + "/login/json", data = params)


session = req.json()["data"]
print session
req = requests.post(config['url'] + "/people/json", data = params)
out = req.json()

for p in out["data"]:
  print p