from baxterSlate import Student, DemonstrationSkill, Demonstration, Skill
import datetime
import csv

class DemoImporter:
  def __init__(self, compsByBaxterName, session):  

    self.compsByBaxterName = compsByBaxterName
    self.session = session

    self.unfound = {}

    self.demoSkills = session.query(DemonstrationSkill).all()
    self.skillsByCompID = self.GetSkillsByCompID(session.query(Skill).all())
    self.studentsByNumber, self.studentsByID = self.GetStudentIndicies(session.query(Student).all())
    self.demosByHash = self.GetDemosByHash(self.session.query(Demonstration).all())

    
  def readDemos(self, targets):
    unfound = self.unfound
    entries = []
    for targetInfo in targets:
      filename = "data/" + targetInfo['file']
      year = targetInfo['year']
      with open(filename, 'rb') as file:
        reader = csv.DictReader(file)
        for entry in reader:
          if(entry['Date'] != ''):
            entries.append(entry)
          else:
            print "DATE INFO BAD" + ','.join(entry.values())
    for data in unfound:
      print "NOT FOUND: " + ",".join(unfound[data])

    sortedEntries = sorted(entries, key=lambda k: datetime.datetime.strptime(k['Date'], '%m/%d/%Y')) 

    for entry in sortedEntries:
      self.readDemo(entry)



  def readDemo(self, info):
    unfound = self.unfound
    compsByBaxterName = self.compsByBaxterName
    stateID = info['State ID']
    if stateID in self.studentsByNumber.keys():
      student = self.studentsByNumber[info['State ID']]
      demo = self.getDemo(info, student)
      self.session.add(demo)
      self.session.flush()

      demoSkills = self.getDemoSkills(demo, student, info)

      compName = info['Task']
      if not compName in compsByBaxterName.keys():
        print compName

    else:
      print stateID + " : " + info["Last Name"] + ", " + info["First Name"] + " NOT FOUND"

  def getDemo(self, info, student):
    myDate = info['Date']
    courseName = info['Course Name']
    demoHash = str(myDate) + str(student.studentNumber) + courseName

    if demoHash in self.demosByHash.keys():
      return self.demosByHash[demoHash]
    else:
      newDemo = Demonstration()
      newDemo.readDict(info, student.studentID)
      return newDemo

  def GetSkillsByCompID(self, skills):
    skillsByCompID = {}
    for skill in skills:
      compID = skill.competencyID
      skillSet = []
      if compID in skillsByCompID.keys():
        skillSet = skillsByCompID[compID]
      if skill not in skillSet:
        skillSet.append(skill)

    return skillsByCompID

  def GetStudentIndicies(self, students):
    studentsByNumber = {}
    studentsByID = {}
    for student in students:
      studentsByNumber[student.studentNumber] = student
      studentsByID[student.id] = student

    return studentsByNumber, studentsByID

  def GetDemosByHash(self, demos):
    demosByHash = {}
    for demo in demos:
      student = self.studentsByID[demo.studentID]
      demoHash = (demo.demonstrated.strftime("%m/%d/%Y")) + str(student.studentNumber) + demo.context
      demosByHash[demoHash] = demo

    return demosByHash