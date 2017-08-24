from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
import re

Base = declarative_base()

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

def IsCompetency(data):
  return data["Type"] == "Competency Statement"


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

  def getCodeRoot(self):
    competencySearch = re.search('([A-Z]+\.[0-9]+)\.', self.code)
    if competencySearch:
      return competencySearch.group(1)
    else:
      return "?"


  def readDict(self, dict):
    self.code = dict['Code']
    self.descriptor = dict['Descriptor']
    self.statement = dict['Statement']
    self._class = 'Slate\CBL\Competency'

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
    self._class = 'Slate\CBL\Skill'
    self.code = data['Code']
    self.creatorID = 1
    self.descriptor = data['Descriptor']
    self.statement = data['Statement']
    self.demonstrationsRequired = data['ER']
    self.gradeLevel = data['Grade Level'].upper()
    self.validateDescriptor()

  def validateDescriptor(self):
    if not re.match('^(EN)|(PR)|(GB)|(AD)|(EX):.*', self.descriptor):
      self.descriptor = self.gradeLevel + ": " + self.descriptor

