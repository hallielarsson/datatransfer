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


class Student:
	def __init__(self, studentCsv):
		self.paramByKey = {}
		self.params = [
			CsvKey('Student ID', 'Student Number', 'State ID'),
			CsvKey('Username'),
			CsvKey('First Name'),
			CsvKey('Last Name'),
			CsvKey('Middle Name'),
			CsvKey('Gender'),
			CsvKey('Birthdate'),
			CsvKey('Phone','Cell Phone'),
			CsvKey('Email'),
			CsvKey('Postal Address'),
			CsvKey('Address Line 1'),
			CsvKey('City'),
			CsvKey('State'),
			CsvKey('Zip'),
			CsvKey('Graduation Year', 'Cohort Year', 'Cohort Year NGA')
		]

		self.data = studentCsv
		for param in self.params:
			param.read(self.data)
			self.paramByKey[param.writeKey] = param
		self.computeParams()

	def computeParams(self):
		self.setAddress()
		self.setUserName()
		self.setEmail()

	def setAddress(self):
		pbk = self.paramByKey
		postalAddress = pbk['Postal Address'].value
		if len(postalAddress) == 0:
			city = pbk['City'].value
			state = pbk['State'].value
			zipCode = pbk['Zip'].value
			address1 = pbk['Address Line 1'].value
			fullAdd = address1 + ", " + city + ", " + state + " " + zipCode
			fullAdd = re.sub('(\s)\s+', ' ', fullAdd)
			if(city != ""):
				pbk['Postal Address'].setIfEmpty(fullAdd)
	
	def setUserName(self):
		global usedNames
		name = ""
		i = 1
		lastName = ""
		while name == "" or name in usedNames:
			fname = self.params[FIRST_NAME_INDEX].value.lower()
			lname = self.params[LAST_NAME_INDEX].value.lower()
			uname = fname[:i] + lname
			uname = re.sub('\W','',uname)
			i = i + 1
			name = uname.lower()
			if(name == lastName):
				name += str(i)
			lastName = name
		self.paramByKey['Username'].value = name

	def getUsername(self):
		return self.paramByKey['Username'].value

	def setEmail(self):
		fname = self.params[FIRST_NAME_INDEX].value
		lname = self.params[LAST_NAME_INDEX].value
		uname = re.sub('\W','',fname) + "." + re.sub('\W','',lname)
		uname += "@baxter-academy.org"
		self.paramByKey['Email'].value = uname.lower()

	def getId(self):
		return self.params[0].value

	def getKeys(self):
		return self.paramByKey.keys()

	def getDict(self):
		output = {}

		for param in self.params:
			output[param.writeKey] = param.value

		#output['Username'] = self.getUserName()
		return output

	#assumes same key structure on target
	def merge(self, target):
		targetParams = target.params
		params = self.params
		targetSize = len(targetParams)
		assert(targetSize == len(params))
		for i in range(targetSize):
			param = params[i]
			targetParam = targetParams[i]
			print param.writeKey + " : " + param.value + " : " + targetParam.value
			if param.value == "" and targetParam.value != "":
				print targetParam.value
				param.value = targetParam.value

def validate(student):
	out = {}
	return out
		
usedNames = []

keys = ['Student ID','First Name','Last Name','Middle Name','Gender','Birthdate','Graduation Year','Username','Email','Phone','Postal Address']
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
				usedNames.append(validStudent.getUsername())

	#keys = validStudent.getKeys()

with open(output, 'w') as file:
	studentWriter = csv.DictWriter(file, keys, extrasaction='ignore')
	studentWriter.writeheader()
	for student in students.values():
		studentData = student.getDict()
		print(studentData)
		studentWriter.writerow(studentData)
