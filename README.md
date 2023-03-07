# ApiE

eric o meehan

2023-066

blueprint of a python/flask api for json data

## usage
1. import DataModel and design a child class
2. create a basic flask application
3. import ApiE and create an instance parameterized with the DataModel child class
4. register the ApiE instance blueprint to the flask application
5. launch

## interface
### DataModel
* the DataModel object is an abstract class whose children represent the json objects being operated on by the api
* each child of the DataModel object is sourced from an underlying json file
* DataModel children must define the following:
	- static variables:
		* *dataPath*: the directory in which to store json files
		* *identifier*: human-readable prefix for data id fields
		* *defaultFields*: dictionary of default fields with default values
		* *requiredFields*: list of required fields
		* *optionalFields*: list of optional fields
	- member variables:
		* *purge*: boolean value signaling the deletion of underlying data files
	- methods:
		* *filter*: returns boolean values from arbitrary filters based on supplied parameters
		* *validate*: throws errors if supplied data does not match desired schema
			- call the super method to validate presence of fields and supply defaults

### ApiE
* the ApiE object maintains a list of active DataModel child objects and creates a blueprint of api for that DataModel child
* instantiate ApiE objects with DataModel child classes
#### api methods

**GET**:

	* retrieves json objects
	* filters may be parameterized

**POST**

	* creates new json objects from posted data
	* requires json data to be stored

**PUT**

	* replaces data in existing json objects with posted data
	* requires recordId and data to replace current version

**PATCH**

	* updates data in existing json objects from patched data
	* requires recordId and data to update current version

**DELETE**

	* removes a json object
	* requires recordId as the sole parameter

Note: *recordId* is derived from the *identifier* of the DataModel child class

	- if *identifier* = 'example' then *recordId* = 'example-xxxxxxxxxxxx' where x is a random, hexidecimal integer
