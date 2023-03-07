# apie
#
# eric o meehan
# 2023-065
#
# blueprint of a python/flask api for json data

from abc import ABC, abstractmethod
from flask import Blueprint, request
import json
import logging
import os
import uuid

########

class DataModel(ABC):
	def __init__(self, id = None, data = None):
		if id and not data:
			with open(self.dataPath + id + '.json', 'r') as file:
				self.data = json.loads(file.read())
		elif data and not id:
			if self.identifier + 'Id' in data:
				raise KeyError("cannot create data model object from data with id")
			data[self.identifier + 'Id'] = self.identifier + '-' + str(uuid.uuid4()).split('-')[4]
			self.validate(data)
			self.data = data
			self.save()
		else:
			raise TypeError("initialize data model objects with either id or data")
	
	def save(self):
		with open(self.dataPath + self.data[self.identifier + 'Id'] + '.json', 'w') as file:
			file.write(json.dumps(self.data))

	@abstractmethod
	def filter(self, filters):
		pass

	@abstractmethod
	def validate(self, data):
		for field in self.defaultFields:
			if field not in data:
				data[field] = self.defaultFields[field]
		for field in self.requiredFields:
			if field not in data:
				raise KeyError("missing " + field + " field")
		for field in data:
			if field not in self.defaultFields and field not in self.requiredFields and field not in self.optionalFields:
				raise KeyError(field + " is not a member of event")

	def __del__(self):
		if self.purge:
			try:
				os.remove(self.dataPath + self.data[self.identifier + 'Id'] + '.json')
			except Exception as error:
				logging.warning(str(error))

########

class BadRequest(Exception):
	pass


class InternalServerError(Exception):
	pass


class NotFound(Exception):
	pass

########

class DataStore():
	def __init__(self, dataModel):
		self.dataModel = dataModel
		self.records = {}
		for file in os.listdir(os.fsencode(self.dataModel.dataPath)):
			recordId = os.fsdecode(file).split('.')[0]
			self.records[recordId] = self.dataModel(recordId)
	
	def add(self, data):
		try:
			record = self.dataModel(data = json.loads(data))
			self.records[record.data[self.dataModel.identifier + 'Id']] = record
			return record.data
		except KeyError as error:
			raise BadRequest(str(error))
		except json.decoder.JSONDecodeError as error:
			raise BadRequest("malformed json " + str(error).lower())
		except PermissionError:
			raise InternalServerError("unable to write to " + self.dataModel.dataPath)
		except TypeError as error:
			raise InternalServerError("error initializing data model")
		except Exception as error:
			raise InternalServerError(str(error).lower())
	
	def query(self, filters):
		try:
			return [self.records[record].data for record in self.records if self.records[record].filter(filters)]
		except KeyError as error:
			raise BadRequest(str(error))
		except TypeError as error:
			raise BadRequest(str(error))
		except Exception as error:
			raise InternalServerError(str(error))
	
	def update(self, data, replace = False):
		try:
			data = json.loads(data)
			recordId = data[self.dataModel.identifier + 'Id']
			if recordId not in self.records:
				raise NotFound(recordId)
			temp = dict(self.records[recordId].data)
			if replace:
				temp = data
			else:
				for field in data:
					temp[field] = data[field]
			self.records[recordId].validate(temp)
			self.records[recordId].data = temp
			self.records[recordId].save()
			return self.records[recordId].data
		except json.decoder.JSONDecodeError as error:
			raise BadRequest("malformed json " + str(error).lower())
		except KeyError as error:
			raise BadRequest(str(error))
		except NotFound as error:
			raise NotFound(str(error))
		except Exception as error:
			raise InternalServerError(str(error))
	
	def remove(self, record):
		try:
			record = json.loads(record)
			recordId = record[self.dataModel.identifier + 'Id']
			if not recordId in self.records:
				raise NotFound(recordId)
			self.records.pop(recordId).purge = True
		except json.decoder.JSONDecodeError as error:
			raise BadRequest("malformed json " + str(error).lower())
		except KeyError as error:
			raise BadRequest(str(error))
		except NotFound as error:
			raise NotFound(str(error))
		except Exception as error:
			raise InternalServerError(str(error))

########

class ApiE():
	def __init__(self, dataModel):
		self.dataStore = DataStore(dataModel)
		self.blueprint = Blueprint(dataModel.identifier, __name__)

		@self.blueprint.post('/')
		def post():
			try:
				return json.dumps(self.dataStore.add(request.data))
			except BadRequest as error:
				return json.dumps(self.statusMessage("bad request", str(error))), 400
			except InternalServerError as error:
				logging.warning(str(error))
				return json.dumps(self.statusMessage("internal server error", "post failed")), 500

		@self.blueprint.get('/')
		def get():
			try:
				return json.dumps(self.dataStore.query(request.args))
			except BadRequest as error:
				return json.dumps(self.statusMessage("bad request", str(error))), 400
			except NotFound as error:
				return json.dumps(self.statusMessage("not found", str(error))), 404
			except InternalServerError as error:
				logging.warning(str(error))
				return json.dumps(self.statusMessage("internal server error", "get failed")), 500
		
		@self.blueprint.put('/')
		def put():
			try:
				return json.dumps(self.dataStore.update(request.data, replace = True))
			except BadRequest as error:
				return json.dumps(self.statusMessage("bad request", str(error))), 400
			except NotFound as error:
				return json.dumps(self.statusMessage("not found", str(error))), 404
			except InternalServerError as error:
				logging.warning(str(error))
				return json.dumps(self.statusMessage("internal server error", "put failed")), 500

		@self.blueprint.patch('/')
		def patch():
			try:
				return json.dumps(self.dataStore.update(request.data))
			except BadRequest as error:
				return json.dumps(self.statusMessage("bad request", str(error))), 400
			except NotFound as error:
				return json.dumps(self.statusMessage("not found", str(error))), 404
			except InternalServerError as error:
				logging.warning(str(error))
				return json.dumps(self.statusMessage("internal server error", "patch failed")), 500
		
		@self.blueprint.delete('/')
		def delete():
			try:
				self.dataStore.remove(request.data)
				return json.dumps(self.statusMessage("ok", "delete complete"))
			except BadRequest as error:
				return json.dumps(self.statusMessage("bad request", str(error))), 400
			except NotFound as error:
				return json.dumps(self.statusMessage("not found", str(error))), 404
			except InternalServerError as error:
				logging.warning(str(error))
				return json.dumps(self.statusMessage("internal server error", "delete failed")), 500
			
	def statusMessage(self, status, message):
		return {"status": status, "message": message}
