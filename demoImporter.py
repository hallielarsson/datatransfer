from baxterSlate import Student, DemonstrationSkill, Demonstration, Skill, Competency, StudentCompetency
import datetime, csv, re

MAX_RECORDS = 100
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

    self.competenciesByID = {}
    comps = self.session.query(Competency).all()
    for comp in comps:
      print comp.id
      self.competenciesByID[comp.id] = comp
    self.studentsByNumber, self.studentsByID = self.GetStudentIndicies(session.query(Student).all())
    self.demoSkillsByID = self.GetDemoSkills(session.query(DemonstrationSkill).all())
    self.skillsByID, self.skillsByCompID = self.GetSkillIndices(session.query(Skill).all())
    self.demosByHash = self.GetDemosByHash(self.session.query(Demonstration).all())
    self.studentCompetencies = self.session.query(StudentCompetency).all()

  def readDemos(self, targets):
    unfound = self.unfound
    entries = []
    for targetInfo in targets:
      filename = "data/" + targetInfo['file']
      year = int(targetInfo['year'])
      with open(filename, 'rb') as file:
        reader = csv.DictReader(file)
        for entry in reader:
            self.validateDate(entry, year)
            if not entry["Score"] == "":
              entries.append(entry)

    sortedEntries = sorted(entries, key=lambda k: datetime.datetime.strptime(k['Date'], '%m/%d/%Y'))

    changedDemos = []
    sl = sortedEntries[0:MAX_RECORDS]
    for entry in sl:
      print ",".join(entry.keys())
      print ",".join(entry.values())
      demo, newDemo = self.readDemo(entry)
      if demo:
        changedDemos.append(demo)

    self.session.commit()

    fixedIds = []
    print ("CHANGED DEMOS")
    for demo in changedDemos:
        id = demo.id
        if not id in fixedIds:
            print str(demo.id)
            fixedIds.append(id)
            self.addDemoSkills(demo, self.session)

    self.session.commit()

  def addDemoSkills(self, demo, session):
    demosWithSkills = self.demoSkillsByID.keys()
    if demo.id in demosWithSkills:
      demoSkills = self.demoSkillsByID[demo.id]
    else:
      demoSkills = []

    recordedIDs = []
    for demoSkill in demoSkills:
      print "DS" + str(demoSkill)
      recordedIDs.append(demoSkill.skillID)

    skillDatas = demo.skillDatas
    for skillData in skillDatas:
      for skill in skillData["skills"]:
        self.checkCompetency(demo, skill)
        if skill.id not in recordedIDs:
          demoSkill = self.makeNewDemoSkill(demo, skill, skillData)
          session.add(demoSkill)

  def makeNewDemoSkill(self, demo, skill, skillData):
    demoSkill = DemonstrationSkill()
    demoSkill.init()
    demoSkill.targetLevel = skillData["level"]
    demoSkill.demonstratedLevel = skillData["level"]
    demoSkill.skillID = skill.id
    demoSkill.demonstrationID = demo.id
    print demo.context + " " + skill.descriptor
    return demoSkill

  def checkCompetency(self, demo, skill):
    student = self.studentsByID[demo.studentID]
    competency = self.competenciesByID[skill.competencyID]
    competencyRecords = [sc for sc in self.studentCompetencies if sc.studentID == student.id and sc.competencyID == competency.id]
    if len(competencyRecords) < 1:
      print "STUDENT NOT ENROLLED: " + student.firstName + " " + student.lastName + " " + competency.descriptor
    else:
      print  "STUDENT ENROLLED!: " + student.firstName + " " + student.lastName + " " + competency.descriptor + " " + str(competencyRecords[0].level)


  def readDemo(self, info):
    stateID = info['State ID']
    if not stateID in self.studentsByNumber.keys():
      print stateID + " : " + info["Last Name"] + ", " + info["First Name"] + " NOT FOUND"
      return None, False

    student = self.studentsByNumber[stateID]
    demo, newDemo = self.getDemo(info, student)
    if newDemo:
        self.session.add(demo)

    compName = info['Task']
    if not compName in self.compsByBaxterName.keys():
      print compName + " NOT FOUND"
      return None, False

    comp = self.compsByBaxterName[compName]

    if not comp.id in self.skillsByCompID.keys():
      print comp.descriptor + ", " + str(comp.id) + " has no SLATE defined skills"
      return None, False

    compSkills = self.skillsByCompID[comp.id]
    print "adding demo " + demo.context + " " + info['Score']
    demo.addSkillDatas(compSkills, info['Score'])
    return demo, newDemo

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
        dsList.append(demoSkill)
      else:
        dsList = [demoSkill]
        demoSkillsByDemoID[demoID] = dsList

    return demoSkillsByDemoID

  def validateDate(self, entry, year):
      if(entry['Date'] != ''):
        return entry
      else:
        term = entry['Term Name']
        month = termMonthLut[term]
        renderYear = year
        if (int(month) < 8):
          renderYear = renderYear + 1
        dateString = month + "/" + "01" + "/" + str(renderYear)
        entry['Date'] = dateString

      return entry
