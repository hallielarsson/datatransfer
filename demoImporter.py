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

    self.studentsByNumber, self.studentsByID = self.GetStudentIndicies(session.query(Student).all())
    self.demoSkillsByID = self.GetDemoSkills(session.query(DemonstrationSkill).all())
    self.skillsByID, self.skillsByCompID = self.GetSkillIndices(session.query(Skill).all())
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

    sl = sortedEntries[0:100]

    changedDemos = []
    for entry in sl:
      print ",".join(entry.values())
      demo, newDemo = self.readDemo(entry)
      #self.session.commit()
      if newDemo:
          changedDemos.append(demo)

    self.session.commit()

    print ("CHANGED DEMOS")
    for demo in changedDemos:
        print demo.id

  def readDemo(self, info):
    stateID = info['State ID']
    if not stateID in self.studentsByNumber.keys():
      print stateID + " : " + info["Last Name"] + ", " + info["First Name"] + " NOT FOUND"
      return None, False

    student = self.studentsByNumber[stateID]
    demo, newDemo = self.getDemo(info, student)
    if newDemo:
        self.session.add(demo)
    return demo, newDemo

    compName = info['Task']
    if not compName in self.compsByBaxterName.keys():
      print compName + " NOT FOUND"
      return

    comp = self.compsByBaxterName[compName]

    if not comp.id in self.skillsByCompID.keys():
      print comp.descriptor + ", " + str(comp.id) + " has no SLATE defined skills"
      return

    compSkills = self.skillsByCompID[comp.id]
    print "adding demo " + demo.context
    demo.addSkills(compSkills)

  def getMissingSkillsInDemo(self, compSkills, demoSkills):
    out = []
    for skill in compSkills:
      if skill not in demoSkills:
        out.append(skill)
    return out

  def getDemo(self, info, student):
    myDate = info['Date']
    courseName = info['Course Name']
    demoHash = str(myDate) + str(student.studentNumber) + courseName
    print demoHash
    if demoHash in self.demosByHash.keys():
      return self.demosByHash[demoHash], False
    else:
      demo = Demonstration()
      demo.readDict(info, student.id)
      self.demosByHash[demoHash] = demo
      return demo, True

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
      demoHash = self.GetDemoHash(demo, student)
      demosByHash[demoHash] = demo
    return demosByHash

  def GetDemoHash(self, demo, student):
    return (demo.demonstrated.strftime("%m/%d/%Y")) + str(student.studentNumber) + demo.context

  def GetDemoSkills(self, demoSkills):
    demoSkillsByDemoID = {}
    demoSkillsByHash = {}
    for demoSkill in demoSkills:
      demoID = demoSkill.demonstrationID
      if demoID in demoSkillsByDemoID.keys():
        dsList = demoSkillsByDemoID[demoID]
        dsList.append(demoID)
      else:
        dsList = [demoSkill]
        demoSkillsByDemoID[demoID] = dsList

    return demoSkillsByDemoID
