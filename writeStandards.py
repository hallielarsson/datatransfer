from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
import csv
import re
import urllib2


from baxterSlate import Skill, Competency
import json


levelLut = {
  "EN" : 1,
  "PR" : 2,
  "GB" : 3,
  "AD" : 4,
  "EX" : 5 ,
  "" : -1
}


legacyLevelLut = {
  "EN" : 9,
  "PR" : 10,
  "GB" : 11,
  "AD" : 12,
  "EX" : 13,
  "BA" : 1,  
  "" : -1
}
config = None
with open('config.json') as configFile:
  config = json.load(configFile)

def IsCompetency(data):
  return data["Type"] == "Competency Statement"


def Main():

  url = URL("mysql", username = config['dbUsername'], password = config['dbPassword'],  host = config['dbHost'],
    port = config['dbPort'], database = config['database'])
  engine = create_engine(url, echo=False)
  Base = declarative_base()
  Session = sessionmaker(bind=engine, autoflush=False, autocommit = False)

  conn= engine.connect()  
  session = Session()
  compIndex = {}
  skillIndex = {}
  compsByCode = {}
  skillsByCode = {}

  try:
    oldCompetencies = session.query(Competency)
    for comp in oldCompetencies:
      compIndex[str(comp.id)] = comp
      compsByCode[comp.code] = comp
    oldSkills = session.query(Competency)
    for skill in oldSkills:
        skillIndex[str(skill.id)] = skill
        skillsByCode[skill.code] = skill
    importer = SkillImporter(compIndex, skillIndex, compsByCode, skillsByCode, session)
    importer.loadUrls()
  except RuntimeError as e:
    print e
    session.rollback()
    session.flush()



  session.rollback()
  session.flush()
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

  def readCsv(self, reader, domainId):
    index = 0
    lastGrade = 1
    competencyCode = ""
    currentComp = None
    for skillData in reader:
      if IsCompetency(skillData): 
        id = str(skillData["ID"])
        if(id in self.compIndex.keys()):
          comp = self.compIndex[id]
        else:
          code = skillData["Code"]
          if(code in self.compsByCode.keys()): 
            comp = self.compsByCode[code]
          else:
            comp = Competency()
            comp.creatorID = 1

        comp.readDict(skillData)
        if comp.contentAreaID == None:
          comp.contentAreaID = domainId
        else:
          print (comp.contentAreaID)
        self.competencies.append(comp)
        currentComp = comp
        self.session.add(comp)
        self.session.flush()
        index = 1
        lastGrade = 1

      else:
        skill = Skill()
        skill.creatorID = 1
        skill.readDict(skillData)
        self.skills.append(skillData)
        if skill.gradeLevel.isdigit():
          gradeInt = int(skill.gradeLevel)
        else:
          gradeInt = levelLut[skill.gradeLevel]
        if gradeInt > lastGrade:
          lastGrade = gradeInt
          index = 1

        oldCode = skill.code
        skill.code = '.'.join([currentComp.getCodeRoot(),str(gradeInt),str(index)])
        index += 1
        skill.competency = currentComp
        skill.competencyID = currentComp.id
        print(skill)
        print(skill.competencyID)

Main()
