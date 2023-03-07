#!/usr/bin/python
#
# eric o meehan
# 2023-066
#
# example application using ApiE

from ApiE import ApiE, DataModel
from flask import Flask

class ExampleData(DataModel):
	dataPath = "/tmp/test/" 
	identifier = 'example'
	defaultFields = {'test': True}
	requiredFields = ['exampleId']
	optionalFields = ['one', 'two', 'three']
	def __init__(self, id = None, data = None):
		self.purge = False
		super().__init__(id = id, data = data)
	
	def filter(self, filters):
		return True

	def validate(self, data):
		super().validate(data)
		return True

app = Flask(__name__)
app.register_blueprint(ApiE(ExampleData).blueprint)

if __name__ == "__main__":
	app.run(debug = True, host="::1", port=8080)
