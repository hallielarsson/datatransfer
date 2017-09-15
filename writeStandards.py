from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
import csv
import re
import urllib2


from baxterSlate import Skill, Competency, DemonstrationSkill, Student, StudentCompetency
import json

levelLut = {
  "EN" : 1,
  "PR" : 2,
  "GB" : 3,
  "AD" : 4,
  "EX" : 5 ,
  "" : -1
}

levelConversion = {
  0 : 0,
  9 : 1,
  10 : 2,
  11: 3,
  12 : 4,
  13 : 5
}

config = None
with open('config.json') as configFile:
  config = json.load(configFile)

url = URL("mysql", username = config['dbUsername'], password = config['dbPassword'],  host = config['dbHost'],
  port = config['dbPort'], database = config['database'])

Session = sessionmaker()
engine = create_engine(url, echo=True)

def Main():
  conn= engine.connect()
  trans = conn.begin()
  session = Session(bind=conn,autoflush=False, autocommit = False)
  #SyncStandards(session)

  ShiftDemos(session)


def ShiftDemos(session):
  demoSkills = session.query(DemonstrationSkill)
  for demoSkill in demoSkills:
    if demoSkill.targetLevel >= 9:
      demoSkill.targetLevel -= 8
      demoSkill.demonstratedLevel -= 8
    print demoSkill
  session.commit()

def SyncStandards(session):

  compIndex = {}
  skillIndex = {}
  compsByCode = {}
  skillsByCode = {}

  try:
    oldCompetencies = session.query(Competency)
    print oldCompetencies

    for comp in oldCompetencies:
      compIndex[str(comp.id)] = comp
      compsByCode[comp.code.upper()] = comp
      comp.code = comp.code.upper()
    oldSkills = session.query(Skill)
    for skill in oldSkills:
        skillIndex[str(skill.id)] = skill
        skillsByCode[skill.code.upper()] = skill
        skill.code = skill.code.upper()
    importer = SkillImporter(compIndex, skillIndex, compsByCode, skillsByCode, session)
    importer.loadUrls()

    #for skill in session.query(Skill):
      #print skill

  except RuntimeError as e:
    print "ERROR"
    print e
    session.rollback()

  session.rollback()
  session.close()


class SkillImporter:
  config = config
  competencies = []
  skills = []
  def __init__(self, compIndex, skillIndex, compsByCode, skillsByCode, session):
      self.compIndex = compIndex
      self.skillIndex = skillIndex
      self.session = session
      self.compsByCode = compsByCode
      self.skillsByCode = skillsByCode

  def loadFiles(self):
    targets = self.config["standardFiles"]
    for target in targets:
      with open(target, 'rb') as file:
        reader = csv.DictReader(file)
        self.readCsv (reader)
  def loadUrls(self):
    targets = self.config["standardsSheets"]
    baseUrl = self.config["standardsUrl"]
    for data in targets:
      url = baseUrl + "&gid=" + str(data['sheet'])
      response = urllib2.urlopen(url)
      reader = csv.DictReader(response)
      self.readCsv (reader, data['domain'])

  def getComp(self, data):
    id = str(data["ID"])
    code = data["Code"].upper()
    if id in self.compIndex.keys():
      return self.compIndex[id]
    elif code in self.compsByCode.keys(): 
      return self.compsByCode[code]
    else:
      comp = Competency()
      comp.creatorID = 1
      return comp

  def getSkill(self, data):
    id = str(data["ID"])
    code = data["Code"].upper()
    print " ...[" + code +  "]..."
    print self.skillsByCode.keys()
    if id in self.skillIndex.keys():
      return self.skillIndex[id]
    elif code in self.skillsByCode.keys(): 
      return self.skillsByCode[code]
    else:
      skill = Skill()
      skill.creatorID = 1
      return skill

  def readCsv(self, reader, domainId):
    index = 0
    lastGrade = 1
    competencyCode = ""
    currentComp = None
    for skillData in reader:
      if IsCompetency(skillData): 
        comp = self.getComp(skillData)
        comp.readDict(skillData)
        if comp.contentAreaID == None:
          comp.contentAreaID = domainId
        currentComp = comp
        self.session.add(comp)
        self.session.flush()
        index = 1
        lastGrade = 1

      else:
        skill = self.getSkill(skillData)
        skill.readDict(skillData)
        index += 1
        skill.competency = currentComp
        skill.competencyID = currentComp.id
        print (skill.code)
        self.session.add(skill)

def IsCompetency(data):
  return data["Type"] == "Competency Statement"

class ImportStudentDemonstrations:
  def execute(self, targets, session):
    studentDemos = session.query(StudentDe)
    for target in targets:
      with open(target, 'rb') as file:
        reader = csv.DictReader(file)
        self.readCsv (reader)

  def readCsv(self, reader, session):
    competencies = session.query(Competency)
    students = session.query(Student)
    for data in reader:
      pass
Main()
