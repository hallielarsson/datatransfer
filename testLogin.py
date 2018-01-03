import requests, json, csv, re

config = {}
with open('config.json') as configFile:
  config = json.load(configFile)

def getBaseParams():
   return {'_LOGIN[username]' : config['username'],
    '_LOGIN[password]': config['password'], '_LOGIN[returnMethod]' : 'POST',
    '_LOGIN[format]' : 'application/json'}

headers={ 'Content-Type':'application/json' }

def tryRequest(path):
  req = requests.post(config['url'] + path + "?format=json", params = getBaseParams(), headers = headers)
  print req.text
  return req

relationships = tryRequest("/relationships").json()['data']
people = tryRequest("/people").json()['data']
contactPoints = tryRequest("/contact-points").json()['data']

peopleById = {}
peopleByEmail = {}
studentsByNumber = {}
peopleByUsername = {}

def getUsername(firstname, lastname):
  baseName = str.lower(firstname + lastname)
  return re.sub("\W","", baseName)

for person in people:
  peopleById[person['ID']] = person
  if 'Username' in person.keys() and person['Username'] != None:
    peopleByUsername[person['Username']] = person
  if 'StudentNumber' in person.keys() and person['StudentNumber'] != None:
    studentsByNumber[person['StudentNumber']] = person

for k in peopleByUsername.keys():
  print k
for cp in contactPoints:
  person = peopleById[cp['PersonID']]
  peopleByEmail[cp['Data']] = person


def relationshipExists(idA, idB):
  for rel in relationships:
    if (idA == rel['PersonID'] and idB == rel['RelatedPersonID']) or (idB == rel['PersonID'] and idA == rel['RelatedPersonID']):
      return True
  return False

for (email, person) in peopleByEmail.iteritems():
  print(email, person['FirstName'])

saveParents = []

def createEmailEntry(personId, email, makePrimary=True):
  try:
    newContact = {
      "Label" : "Imported Email",
      "Data" : email,
      "PersonID" : personId,
      "Class" : "Emergence\People\ContactPoint\Email"
    }
    req = requests.post(
      config['url'] + "/contact-points/save?format=json",
      params=getBaseParams(),
      headers=headers,
      data=json.dumps({ 'data' : [newContact] })
    )
    print(req.text)
    emailID = req.json()['data'][0]['ID']
    print(req.json())
    if makePrimary:
      req = requests.post(
        config['url'] + "/people/save?format=json",
        params=getBaseParams(),
        headers=headers,
        data=json.dumps({ 'data' : [{
          "PrimaryEmailID" :emailID,
          "ID" : personId,
        }]})
      )
      print(req.json())
  except NameError as e:
    print(e)
  except IndexError as e:
    print(e)


with open("data/parentwrite.csv", 'r') as parentData:
  parentReader = csv.DictReader(parentData)
  for parent in parentReader:
    parentUsername = getUsername(parent['First Name'], parent['Last Name'])
    email = parent['Email']
    parentId = None
    try:
      studentId = studentsByNumber[parent['Student ID']]['ID']
    except KeyError as e:
      print ("!!!" , e)
    if email == None:
      continue
    if email in peopleByEmail.keys():
      person = peopleByEmail[email]
      print(email, person)
      parentId = person['ID']
    elif parentUsername in peopleByUsername.keys():
      person = peopleByUsername[parentUsername]
      parentId = person['ID']
      if person['PrimaryEmailID'] == None:
        createEmailEntry(parentId, email)
    else:
      saveParent = {
        'FirstName' : parent['First Name'],
        'LastName' : parent['Last Name'],
        'AccountLevel' : 'User',
        'Username' : parentUsername,
        'About' : 'Parent'

      }
      req = requests.post(
        config['url'] + "/people/save?format=json",
        params=getBaseParams(),
        headers=headers,
        data=json.dumps({ 'data' : [saveParent] })
      )
      print req.json()
      parentId = req.json()['data'][0]['ID']
      createEmailEntry(parentId, email)
      #saveParents.append(saveParent)

    if not relationshipExists(parentId, studentId):
      rel = {
        'Class' : 'Emergence\People\Relationship',
        'PersonID': parentId,
        'Label':'child',
        'RelatedPersonID' : studentId,
        'InverseRelationship' : {
          'Class' : 'Emergence\People\GuardianRelationship',
          'PersonID': studentId,
          'Label':'guardian',
          'RelatedPersonID' : parentId,
        }
      }
      req = requests.post(
        config['url'] + "/relationships/save?format=json",
        params=getBaseParams(),
        headers=headers,
        data=json.dumps({ 'data' : [rel] })
      )



def saveData(data):
  sendData = []
  for p in data:
    print(p)
    p["MiddleName"] = "Steve"
    sendData.append(p)
    #newdata.append(p)

  req = requests.post(config['url'] + "/people/save?include=MiddleName",
    params= getBaseParams(),
    data=json.dumps({ "data" : sendData } ),
    headers=headers,
    )

  print(req.text)

#saveData(people["data"])

#print json.dumps(newdata)
