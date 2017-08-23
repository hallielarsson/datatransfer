from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker

import json
engine = create_engine('sqlite:///memory:', echo=True)
Base = declarative_base()

from csvkey import CsvKey

config = None
with open('config.json') as configFile:
  config = json.load(configFile)

  config = config
  competencies = []

class SkillImporter:
  config = config
  competencies = competencies
  def Main(self):
    targets = self.config.standardFiles
    for target in targets:
      currentComp = None
      with open(target, 'rb') as file:
        reader = csv.DictReader(file)
        for skill in reader:
          if Competency.IsInstance(skill):
            comp = Competency()
            comp.ReadDict(skill)
            competencies.append(comp)
            currentComp = comp
          else:
            skill = Skill()
            skill.ReadDict(skill)
            skills.append(skill)
            skill.competency = currentComp

class StudentCompetency(Base):
  id = Column(Integer, primary_key=True)
  _class = Column('class', String)
  created = Column(DateTime)
  creatorID = Column(Integer)
  studentID = Column(Integer)
  level = Column(Integer)
  enteredVia = Column(String)

class Student(Base):
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
  studentNumer = Column(Integer)
  graduationYear = Column(Integer)

class Competency(Base):
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

  def IsInstance(dict):
    return data["Type"] == "Competency"

  def ReadDict(self, dict):
    self.code = dict['Code']
    self.descriptor = dict['Descriptor']
    self.statement = dict['Statement']
    self._class = "Slate\CBL\StudentCompetency"

class Skill(Base):
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
  evidenceRequirement = Column(String)

  def ReadDict(self, dict):
    self.code = dict['Code']
    self.descriptor = dict['Descriptior']
    self.statement = dict['Statement']
    self.evidenceRequirement = dict['ER']
    self._class = "Slate\CBL\Skill"
    self.gradeLevel = dict['Grade Level']



Main()


