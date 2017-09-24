from baxterSlate import Student, DemonstrationSkill, Demonstration, Skill
import datetime, csv, re

termMonthLut = {
  "T1" : "08",
  "T2" : "12",
  "T3" : "04"

}
class DemoImporter:
  def __init__(self, compsByBaxterName, session):  

    self.compsByBaxterName = compsByBaxterName
    self.session = session

    self.unfound = {}

    self.demoSkills = self.GetDemoSkillsByDemo(session.query(DemonstrationSkill).all())
    self.skillsByID, self.skillsByCompID = self.GetSkillIndices(session.query(Skill).all())
    self.studentsByNumber, self.studentsByID = self.GetStudentIndicies(session.query(Student).all())
    self.demosByHash = self.GetDemosByHash(self.session.query(Demonstration).all())

    
  def readDemos(self, targets):
    unfound = self.unfound
    entries = []
    for targetInfo in targets:
      filename = "data/" + targetInfo['file']
      year = int(targetInfo['year'])
      with open(filename, 'rb') as file:
        reader = csv.DictReader(file)
        for entry in reader:
          if(entry['Date'] != ''):
            entries.append(entry)
          else:
            term = entry['Term Name']
            month = termMonthLut[term]
            renderYear = year
            if (int(month) < 8):
              renderYear = renderYear + 1

            dateString = month + "/" + "01" + "/" + str(renderYear)
            entry['Date'] = dateString
            print "DATE INFO BAD Set to" +  dateString + "for data: " + ','.join(entry.values())


    for data in unfound:
      print "NOT FOUND: " + ",".join(unfound[data])

    sortedEntries = sorted(entries, key=lambda k: datetime.datetime.strptime(k['Date'], '%m/%d/%Y')) 

    for entry in sortedEntries:
      self.readDemo(entry)



  def readDemo(self, info):
    stateID = info['State ID']
    if not stateID in self.studentsByNumber.keys():
      print stateID + " : " + info["Last Name"] + ", " + info["First Name"] + " NOT FOUND"
      return

    student = self.studentsByNumber[stateID]

    compName = info['Task']
    if not compName in self.compsByBaxterName.keys():
      print compName + " NOT FOUND"
      return
    comp = self.compsByBaxterName[compName]
    print comp.descriptor + ", " + str(comp.id)
    compSkills = self.skillsByCompID[comp.id]

    demo = self.getDemo(info, student)
    if demo.id != None:
      demoSkills = self.demoSkills[demo.id]
      newSkills = self.getMissingSkillsInDemo(compSkills, demoSkills)
    



  def getDemo(self, info, student):

    myDate = info['Date']
    courseName = info['Course Name']
    demoHash = str(myDate) + str(student.studentNumber) + courseName

    if demoHash in self.demosByHash.keys():
      return self.demosByHash[demoHash]
    else:
      newDemo = Demonstration()
      newDemo.readDict(info, student.id)
      return newDemo

  def GetSkillIndices(self, skills):
    skillsByCompID = {}
    skillsByID = {}
    for skill in skills:
      skillsByID[skill.id] = skill
      compID = skill.competencyID
      skillSet = []
      if compID in skillsByCompID.keys():
        skillSet = skillsByCompID[compID]
      if skill not in skillSet:
        skillSet.append(skill)
      skillsByCompID[compID] = skillSet

    return skillsByID, skillsByCompID

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

  def GetDemoSkillsByDemo(self, demoSkills):
    demoSkillsByDemoID = {}
    for demoSkill in demoSkills:
      demoID = demoSkill.demonstrationID
      if demoID in demoSkillsByDemoID.keys():
        dsList = demoSkillsByDemoID[demoID]
        dsList.append(demoID)
      else:
        dsList = [demoSkill]
        demoSkillsByDemoID[demoID] = dsList

    return demoSkillsByDemoID