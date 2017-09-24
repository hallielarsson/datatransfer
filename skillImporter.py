from baxterSlate import Student, DemonstrationSkill, Demonstration
import datetime
import csv
import re
import urllib2

def IsCompetency(data):
  return data["Type"] == "Competency Statement"

class SkillImporter:
  competencies = []
  skills = []
  def __init__(self, compIndex, skillIndex, compsByCode, skillsByCode, session, config):
      self.compIndex = compIndex
      self.skillIndex = skillIndex
      self.session = session
      self.compsByCode = compsByCode
      self.skillsByCode = skillsByCode
      self.compsByBaxterName = {}
      self.config = config

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

  def getComp(self, data):
    id = str(data["ID"])
    code = data["Code"].upper()
    if id in self.compIndex.keys():
      return self.compIndex[id]
    elif code in self.compsByCode.keys(): 
      return self.compsByCode[code]
    else:
      comp = Competency()
      comp.creatorID = 1
      return comp

  def getSkill(self, data):
    id = str(data["ID"])
    code = data["Code"].upper()
    if id in self.skillIndex.keys():
      return self.skillIndex[id]
    elif code in self.skillsByCode.keys(): 
      return self.skillsByCode[code]
    else:
      skill = Skill()
      skill.creatorID = 1
      return skill

  def readCsv(self, reader, domainId):
    index = 0
    lastGrade = 1
    competencyCode = ""
    currentComp = None
    for skillData in reader:
      if IsCompetency(skillData): 
        comp = self.getComp(skillData)
        comp.readDict(skillData)
        for key in comp.icName.split(','):
          self.compsByBaxterName[key.strip()] = comp
        if comp.contentAreaID == None:
          comp.contentAreaID = domainId
        currentComp = comp
        self.session.add(comp)
        self.session.flush()
        index = 1
        lastGrade = 1

      else:
        skill = self.getSkill(skillData)
        skill.readDict(skillData)
        index += 1
        skill.competency = currentComp
        skill.competencyID = currentComp.id
        self.session.add(skill)