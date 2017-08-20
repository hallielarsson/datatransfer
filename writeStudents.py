import sqlalchemy
import csv
import re

from csvKey import CsvKey

targets = ["firststudents.csv", "students.csv"]
output = "studentsRev.csv"
delimeter = ","
students = {}

FIRST_NAME_INDEX = 2
LAST_NAME_INDEX = 3
MIDDLE_NAME_INDEX = 4

usedNames = []

class Student:
	def __init__(self, studentCsv):
		self.params = [
			CsvKey('Student ID', 'Student Number', 'State ID'),
			CsvKey('Username'),
			CsvKey('First Name'),
			CsvKey('Last Name'),
			CsvKey('Middle Name'),
			CsvKey('Gender'),
			CsvKey('Birthdate'),
			CsvKey('Cell Phone'),
			CsvKey('Email'),
			CsvKey('Address Line 1'),
			CsvKey('City'),
			CsvKey('State'),
			CsvKey('Zip'),
			CsvKey('Graduation Year', 'Cohort Year', 'Cohort Year NGA')
		]

		self.data = studentCsv
		for param in self.params:
			param.read(self.data)

	def getDict(self):
		output = {}

		for param in self.params:
			output[param.writeKey] = param.value

		#output['Username'] = self.getUserName()
		output['Email'] = self.getEmail()
		return output

	def getUserName(self):
		name = ""
		i = 1
		print len(name)
		while name == "" or name in usedNames:
			fname = self.params[FIRST_NAME_INDEX].value
			lname = self.params[LAST_NAME_INDEX].value
			uname = fname[:i] + lname
			uname = re.sub('\W','',uname)
			i = i + 1
			name = uname.lower()
			print (uname)
			print name
		usedNames.append(name)
		return name


	def getEmail(self):
		fname = self.params[FIRST_NAME_INDEX].value
		lname = self.params[LAST_NAME_INDEX].value
		uname = fname + "." + lname
		uname = re.sub('\W','',uname)
		uname += "@baxter-academy.org"
		return uname.lower()

	def getId(self):
		return self.params[0].value

	def getKeys(self):
		out = []
		for param in self.params:
			out.append(param.writeKey)
		return out

	#assumes same key structure on target
	def merge(self, target):
		targetParams = target.params
		params = self.params
		targetSize = len(targetParams)
		assert(targetSize == len(params))
		for i in range(targetSize):
			param = params[i]
			targetParam = targetParams[i]
			if param.value == "" and targetParam.value != "":
				param.value = targetParam.value

def validate(student):
	out = {}
	return out

keys = []
noKeys = True
for target in targets:
	with open(target, 'rb') as file:
		studentReader = csv.DictReader(file)
		for student in studentReader:
			validStudent = Student(student)
			studentId = validStudent.getId()
			if studentId in students.keys():
				students[validStudent.getId()].merge(validStudent)
			else:
				students[validStudent.getId()] = validStudent
	
			if (noKeys):
				keys = validStudent.getKeys()
				keys.append('Email')
				noKeys = False


with open(output, 'w') as file:
	studentWriter = csv.DictWriter(file, keys)
	studentWriter.writeheader()
	for student in students.values():
		print(student.getUserName())
		studentData = student.getDict()
		studentWriter.writerow(studentData)
		
