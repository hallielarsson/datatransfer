from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from demoImporter import DemoImporter
from skillImporter import SkillImporter

import csv
import re
import urllib2
import datetime


from baxterSlate import Skill, Competency, DemonstrationSkill, Student, StudentCompetency, Demonstration
import json

levelLut = {
  "EN" : 1,
  "PR" : 2,
  "GB" : 3,
  "AD" : 4,
  "EX" : 5 ,
  "" : -1
}

levelConversion = {
  0 : 0,
  9 : 1,
  10 : 2,
  11: 3,
  12 : 4,
  13 : 5
}

config = None
with open('config.json') as configFile:
  config = json.load(configFile)

url = URL("mysql", username = config['dbUsername'], password = config['dbPassword'],  host = config['dbHost'],
  port = config['dbPort'], database = config['database'])

Session = sessionmaker()
engine = create_engine(url, echo=False)

def Main():
  conn= engine.connect()
  trans = conn.begin()
  session = Session(bind=conn,autoflush=False, autocommit = False)


  compsByBaxterName = SyncStandards(session)
  di = DemoImporter(compsByBaxterName, session)
  di.readDemos(config['studentCompetencyDemos'])

  #ShiftDemos(session)


def ShiftDemos(session):
  demoSkills = session.query(DemonstrationSkill)
  for demoSkill in demoSkills:
    if demoSkill.targetLevel >= 9:
      demoSkill.targetLevel -= 8
      demoSkill.demonstratedLevel -= 8

  session.commit()

  studentComps = session.query(StudentCompetency)
  for sc in studentComps:
    if sc.level >= 9:
      sc.level -= 8

  session.commit()

#Returns a dictionary mapping competencies to potential baxter names for correlations purposes
def SyncStandards(session):
  compIndex = {}
  skillIndex = {}
  compsByCode = {}
  skillsByCode = {}

  try:
    oldCompetencies = session.query(Competency)

    for comp in oldCompetencies:
      compIndex[str(comp.id)] = comp
      compsByCode[comp.code.upper()] = comp
      comp.code = comp.code.upper()
    oldSkills = session.query(Skill)
    for skill in oldSkills:
        skillIndex[str(skill.id)] = skill
        skillsByCode[skill.code.upper()] = skill
        skill.code = skill.code.upper()

    importer = SkillImporter(compIndex, skillIndex, compsByCode, skillsByCode, session, config)
    importer.loadUrls()
    return importer.compsByBaxterName
    #for skill in session.query(Skill):
      #print skill

  except RuntimeError as e:
    print "ERROR"
    print e
    session.rollback()

  session.rollback()
  session.close()

Main()
