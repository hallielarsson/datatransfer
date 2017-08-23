from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
import csv
import re

import json
engine = create_engine('sqlite:///memory:', echo=True)
Base = declarative_base()

config = None
with open('config.json') as configFile:
  config = json.load(configFile)

competencies = []
skills = []

levelLut = {
  "EN" : 1,
  "PR" : 2,
  "GB" : 3,
  "AD" : 4,
  "EX" : 5 
}

def IsCompetency(data):
  return data["Type"] == "Competency Statement"

class SkillImporter:
  config = config
  competencies = competencies
  def main(self):
    targets = self.config["standardFiles"]
    for target in targets:
      currentComp = None
      with open(target, 'rb') as file:
        reader = csv.DictReader(file)
        index = 0
        lastGrade = 1
        competencyCode = ""
        for skillData in reader:
          if IsCompetency(skillData):
            comp = Competency()
            comp.ReadDict(skillData)
            competencies.append(comp)
            currentComp = comp
            index = 1
            lastGrade = 1
            competencyCode = re.search('([A-Z]+\.[0-9]+)\.', comp.code).group(1)
   
          else:
            skill = Skill()
            skill.ReadDict(skillData)
            skills.append(skillData)
            gradeInt = levelLut[skill.gradeLevel]
            if gradeInt > lastGrade:
              lastGrade = gradeInt
              print('reset' + str(lastGrade) + skill.gradeLevel)
              index = 1

            oldCode = skill.code
            skill.code = ".".join([competencyCode,str(levelLut[skill.gradeLevel]),str(index)])
            index += 1
            print(skill.code + " " + oldCode)
            skill.competency = currentComp

print competencies

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
  __tablename__ = "cbl_users"
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

  def ReadDict(self, dict):
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
  evidenceRequirement = Column(String)

  def ReadDict(self, data):
    self._class = "Slate\CBL\Skill"
    self.code = data['Code']
    self.descriptor = data['Descriptor']
    self.statement = data['Statement']
    self.evidenceRequirement = data['ER']
    self.gradeLevel = data['Grade Level']

importer = SkillImporter()
importer.main()
