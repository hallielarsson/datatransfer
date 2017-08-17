import sqlalchemy
import csv
import re

targets = ["students.csv"]
output = "studentsRev.csv"
delimeter = ","
students = {}

class CsvKey:
	writeKey = ""
	value = ""
	default= ""

	def __init__(self, *keys):
		assert len(keys) > 0
		self.writeKey = keys[0]
		self.readKeys = keys

	def getKey(self):
		return writeKey

	def tryGet(self, data):
		for key in self.readKeys:
			if key in data:
				return data[key]
		return default

	def read(self, sourceDict):
		self.value = self.tryGet(sourceDict)

class Student:
	def __init__(self, studentCsv):
		self.params = [
			CsvKey('Student ID', 'Student Number'),
			CsvKey('First Name'),
			CsvKey('Last Name'),
			CsvKey('Middle Name'),
		]

		self.data = studentCsv
		for param in self.params:
			param.read(self.data)

	def getDict(self):
		output = {}
		for param in self.params:
			output[param.writeKey] = value
			output['Username'] = self.getUserName()
			return output

	def getUserName(self):
		fname = self.params[1].value
		lname = self.params[3].value
		uname = fname + lname
		uname = re.sub('\W','',uname)
		return uname.lower()

	def getId(self):
		return self.params[0].value

	def getKeys(self):
		out = []
		for param in self.params:
			out.append(param.writeKey)
		return out

def validate(student):
	out = {}
	return out

keys = []
for target in targets:
	with open(target, 'rb') as file:
		studentReader = csv.DictReader(file)
		for student in studentReader:
			validStudent = Student(student)
			students[validStudent.getId()] = validStudent
			keys = validStudent.getKeys()
			print validStudent.getId()


with open(output, 'w') as file:
	studentWriter = csv.DictWriter(file, keys)
	studentWriter.writeheader()
	for student in students.values():
		print(student.getUserName())
		#studentData = student.getDict()
		#studentData["Username"] = student.getUserName()
		#writer.writerow(studentData)
		
