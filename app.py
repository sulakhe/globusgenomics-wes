from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from bioblend import galaxy
import json
import weshandler


app = Flask(__name__)

#db = SQLAlchemy(app)



@app.route('/service-info', methods=['GET'])
def get_service_info():
    return weshandler.__service_info()

# This is the resource to return all the workflows available on the service
@app.route('/workflows', methods=['GET'])
def get_workflows():
 	return weshandler.__get_workflows()

# This is the resource to submit a workflow
# Takes a JSON Paylod with parameters and return the ID for the run.
@app.route('/workflows', methods=['POST'])
def submit_workflow():

    parameters = request.get_json(silent=False)

    if(request.headers['Authorization']):
        api_key = __get_galaxy_user(request.headers['Authorization'])
    else:
        print ("Inside Else")
        return Response('Globus Auth token required..', 401, {'WWW-Authenticate': 'Basic realm="Tokens Required"'})

    runid = weshandler.__submit_workflow(parameters, api_key)
    return runid

## This resource provides detailed info on a workflow run
@app.route('/workflows/<workflow_id>', methods=['GET'])
def get_workflow_run_details(workflow_id=None):
	return ""

## This resource provides detailed info on a workflow run
@app.route('/workflows/<workflow_id>', methods=['DELETE'])
def delete_workflow(workflow_id=None):
	return weshandler.__delete_workflow(workflow_id)

## This resource provides status of a workflow run
@app.route('/workflows/<workflow_id>/status')
def workflow_status(workflow_id=None):
    return "RUNNING"

def __get_galaxy_user(auth):
    globus_user = __get_globus_user(auth)
    
    # Map the globus username to Galaxy username

    # if (galaxy user doesn't exist):
    #	__create_galaxy_user(globus_user)
    # 	api_key = __create_API_key(user)
    return globus_user


def __get_globus_user(auth):
	# Using Auth token, get the globus username and return the username
    return "sulakhe"







if __name__ == '__main__':
    app.run(threaded=True)
