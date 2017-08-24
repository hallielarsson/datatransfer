from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
import csv
import re
import urllib2

import json


config = None
with open('config.json') as configFile:
  config = json.load(configFile)

url = URL("mysql", username = config['dbUsername'], password = config['dbPassword'],  host = config['dbHost'],
  port = config['dbPort'], database = config['database'])
engine = create_engine(url, echo=False)
Base = declarative_base()

Session = sessionmaker(bind=engine)

def Main():

  conn= engine.connect()  
  session = Session()
  compIndex = {}
  skillIndex = {}

  oldCompetencies = session.query(Competency)
  for comp in oldCompetencies:
    compIndex[str(comp.id)] = comp
  oldSkills = session.query(Competency)
  for skill in oldSkills:
      skillIndex[str(skill.id)] = skill
  importer = SkillImporter(compIndex, skillIndex)
  importer.loadUrls()

  print(compIndex)


levelLut = {
  "EN" : 1,
  "PR" : 2,
  "GB" : 3,
  "AD" : 4,
  "EX" : 5 ,
  "" : -1
}

def IsCompetency(data):
  return data["Type"] == "Competency Statement"

class SkillImporter:
  config = config
  competencies = []
  skills = []
  def __init__(self, compIndex, skillIndex):
      self.compIndex = compIndex
      self.skillIndex = skillIndex

  def loadFiles(self):
    targets = self.config["standardFiles"]
    for target in targets:
      with open(target, 'rb') as file:
        reader = csv.DictReader(file)
        self.readCsv (reader)
  def loadUrls(self):
    targets = self.config["standardsSheets"]
    baseUrl = self.config["standardsUrl"]
    for baseId in targets:
      url = baseUrl + "&gid=" + str(baseId)
      response = urllib2.urlopen(url)
      reader = csv.DictReader(response)
      self.readCsv (reader)

  def readCsv(self, reader):
    index = 0
    lastGrade = 1
    competencyCode = ""
    for skillData in reader:
      if IsCompetency(skillData): 
        if("ID" in skillData.keys()):
          id = str(skillData["ID"])
          if(id in self.compIndex.keys()):
            comp = self.compIndex[id]
          else:
            comp = Competency()
        else:
          comp = Competency()

        comp.readDict(skillData)
        self.competencies.append(comp)
        currentComp = comp
        index = 1
        lastGrade = 1
        competencySearch = re.search('([A-Z]+\.[0-9]+)\.', comp.code)
        if competencySearch:
          competencyCode = competencySearch.group(1)
        else:
          competencyCode = "?"
        if comp.id:
          print comp.id

      else:
        skill = Skill()
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
        skill.code = ".".join([competencyCode,str(gradeInt),str(index)])
        index += 1
        skill.competency = currentComp


class StudentCompetency(Base):
  __tablename__ = "cbl_student_competencies"
  id = Column(Integer, primary_key=True)
  _class = Column('class', String)
  created = Column(DateTime)
  creatorID = Column(Integer)
  studentID = Column(Integer)
  level = Column(Integer)
  enteredVia = Column(String)

class Student(Base):
  __tablename__ = "people"
  id = Column(Integer, primary_key=True)
  _class = Column('class', String)
  created = Column(DateTime)
  creatorID = Column(Integer)
  modified = Column(DateTime)
  modifierID = Column(Integer)
  firstName = Column(String)
  lastName = Column(String)
  middleName = Column(String)
  preferredName = Column(String)
  gender = Column(String)
  birthdate = Column(DateTime)
  username = Column(String)
  password = Column(String)
  accountLevel = Column(String)
  temporaryPassword = Column(String)
  studentNumber = Column(Integer)
  graduationYear = Column(Integer)

class Competency(Base):
  __tablename__ = "cbl_competencies"
  id = Column(Integer, primary_key=True)
  _class = Column('class', String)
  created = Column(DateTime)
  creatorID = Column(Integer)
  modified = Column(DateTime)
  modifierID = Column(Integer)
  contentAreaID = Column(Integer)
  code = Column(String)
  descriptor = Column(String)
  statement = Column(String)

  def __repr__(self):
    return self.code + ": " + self.descriptor

  def readDict(self, dict):
    self.code = dict['Code']
    self.descriptor = dict['Descriptor']
    self.statement = dict['Statement']
    self._class = "Slate\CBL\StudentCompetency"

class Skill(Base):
  __tablename__ = "cbl_skills"
  id = Column(Integer, primary_key=True)
  _class = Column('class', String)
  created = Column(DateTime)
  creatorID = Column(Integer)
  modified = Column(DateTime)
  modifierID = Column(Integer)
  competencyID = Column(Integer)
  code = Column(String)
  descriptor = Column(String)
  statement = Column(String)
  demonstrationsRequired = Column(String)

  def __repr__(self):
    return self.code + ": " + self.descriptor

  def readDict(self, data):
    self._class = "Slate\CBL\Skill"
    self.code = data['Code']
    self.descriptor = data['Descriptor']
    self.statement = data['Statement']
    self.demonstrationsRequired = data['ER']
    self.gradeLevel = data['Grade Level'].upper()
    self.validateDescriptor()

  def validateDescriptor(self):
    if not re.match('^(EN)|(PR)|(GB)|(AD)|(EX):.*', self.descriptor):
      self.descriptor = self.gradeLevel + ": " + self.descriptor

Main()
