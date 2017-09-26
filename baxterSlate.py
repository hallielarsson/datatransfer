from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
import datetime
import re

Base = declarative_base()

levelLut = {
  "NE" : 0,
  "EN" : 1,
  "PR" : 2,
  "GB" : 3,
  "AD" : 4,
  "EX" : 5 ,
  "BA" : 6 ,
  "" : -1
}


legacyLevelLut = {
  "EN" : 9,
  "PR" : 10,
  "GB" : 11,
  "AD" : 12,
  "EX" : 13,
  "BA" : 14,
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


  def readDict(self, data):
    self._class = 'Slate\CBL\StudentCompetency'
    self.creatorID = 1
    self.studentID = self.getId(data["StudentNumber"])
    self.competencyID = data["CompetencyID"]
    self.level = levelLut[int(data["level"])]
    self.enteredVia = "enrollment"


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

  demoInfos = []

  def addDemoInfo(self, demoInfo):
    self.demoInfos.append(demoInfo)
    print len(self.demoInfos)


  def __repr__(self):
    return self.code + ": " + self.lastName + ", " + self.firstName

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
    competencySearch = re.search('([A-Za-z]+\.[0-9]+)\.', self.code)
    if competencySearch:
      return competencySearch.group(1)
    else:
      return "BAD_CODE"

  def readDict(self, dict):
    self.code = dict['Code'].upper()
    self.descriptor = dict['Descriptor']
    self.statement = dict['Statement']
    self._class = 'Slate\CBL\Competency'
    self.icName = dict['Baxter Standard']

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
    self.code = data['Code'].upper()
    self.creatorID = 1
    self.descriptor = data['Descriptor']
    self.statement = data['Statement']
    self.demonstrationsRequired = 3 #"data['ER'].upper()
    #self.gradeLevel = data['Grade Level'].upper()

    #print(self.gradeLevel)
    self.demonstrationsRequired = '{"default" : "3" }'
    self.validateDescriptor()

  def validateDescriptor(self):
    if not re.match('^(EN)|(PR)|(GB)|(AD)|(EX):.*', self.descriptor):
      self.descriptor = self.descriptor

class Demonstration(Base):
  __tablename__ = "cbl_demonstrations"
  id = Column(Integer, primary_key=True)
  _class = Column('class', String)
  created = Column(DateTime)
  creatorID = Column(Integer)
  modified = Column(DateTime)
  modifierID = Column(Integer)
  studentID = Column(Integer)
  demonstrated = Column(DateTime)
  artifactURL = Column(String)
  comments = Column(String)
  experienceType = Column(String)
  context = Column(String)
  performanceType = Column(String)
  skillDatas = []


  def addSkillDatas(self, skills, level):
    print("-------------------------")
    print ("level " +str(level))
    self.skillDatas.append({ "skills" : skills, "level" : levelLut[level] })


  def readDict(self, data, studentID):
    self._class = 'Slate\CBL\Demonstrations\ExperienceDemonstration'
    self.creatorID = self.creatorID or 1
    self.modifierID = 1
    self.modified = datetime.datetime.now()
    self.demonstrated = datetime.datetime.strptime(data['Date'], "%m/%d/%Y")
    self.experienceType = "Baxter Course (Legacy)"
    self.context = data['Course Name']
    self.performanceType = 'Final Grade IC Import'
    self.comments = data['Teacher Display'] + " : " + data['Comments']
    self.studentID = studentID

class DemonstrationSkill(Base):
  __tablename__ = "cbl_demonstration_skills"
  _class = Column('class', String)
  id = Column(Integer, primary_key=True)
  created = Column(DateTime)
  creatorID = Column(Integer)
  demonstrationID = Column(Integer)
  skillID = Column(Integer)
  targetLevel = Column(Integer)
  demonstratedLevel = Column(Integer)

  def __repr__(self):
    return str(self.id) + " : " + str(self.targetLevel) + " : " + str(self.demonstratedLevel)

  def init(self):
    self._class = 'Slate\CBL\Demonstrations\DemonstrationSkill'
    self.creatorID = self.creatorID or 1
    self.modifierID = 1
    self.modified = datetime.datetime.now()

  def readDict(self, data):
    self.init()
    self.targetLevel = levelLut[data['targetLevel']]
    self.demonstratedLevel = levelLut[data['targetLevel']]
