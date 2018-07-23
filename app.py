from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from bioblend.galaxy import GalaxyInstance
import json
import weshandler
import time
import os
import sys

app = Flask(__name__)
master_key = __config__("master_key")
url = __config__("url")
cwl_runner_galaxy_workflow_minid = "ark:/57799/b93q6h"
QUERY_BASE = "http://minid.bd2k.org/minid/landingpage/"

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

    gi = GalaxyInstance(url=url, key=api_key)
    wf = __import_galaxy_cwl_workflow(minid=cwl_runner_galaxy_workflow_minid, gi=gi)
    runid = weshandler.__submit_workflow(parameters=parameters, gi_handle=gi, workflow=wf)
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
    master_key = __config__("master_key")
    url = __config__("url")
    gi = GalaxyInstance(url=url, key=master_key)

    # Map the globus username to Galaxy username
    user_list = gi.users.get_users( f_name=globus_user )
    galaxy_user = None
    for user in user_list:
	if globus_user == user['username']:
	    galaxy_user = user
	    break
	
    if galaxy_user is None:
        # __create_galaxy_user(globus_user)
	galaxy_user = __create_galaxy_user(globus_user, gi)
   
    # __create_API_key(galaxy_user)
    api_key = gi.users.get_user_apikey(galaxy_user['id'])
    if api_key is None:
        api_key = gi.users.create_user_apikey(galaxy_user['id'])
    return api_key


def __get_globus_user(auth):
	# Using Auth token, get the globus username and return the username
    return "sulakhe"

def __create_galaxy_user(globus_user, gi):
    user_email = "%s@globusid.org" % globus_user
    user = gi.users.create_remote_user(user_email)
    return user

def __import_galaxy_cwl_workflow(minid=None, gi=None):
    tmp_path = tempfile.mkdtemp()
    wf_mine = None
    try:
        # A.
        BASE_DOWNLOAD_PATH = "/%s" % (tmp_path)
        query = "%s/%s" % (QUERY_BASE, wf_minid)
        #print( "Executing query: %s" % query)
        r = requests.get(query,  headers = {"Accept" : "application/json"})
        location = r.json()["locations"][0]['link']
        filename = location.split("/")[-1]
        path = "%s/%s" % (BASE_DOWNLOAD_PATH, filename)
        #print( "Downloading result: %s" % location)
        testfile = urllib.URLopener()
        testfile.retrieve(location, path)
        extract_path = ".".join(path.split(".")[0:-1])
        output_path = "%s/%s" %(extract_path, ".".join(filename.split(".")[0:-1]))
        #print( "Extracting bag and resolving fetch: %s" % output_path)
        bdbag_api.extract_bag(path, extract_path)
        time.sleep(5)
        bdbag_api.resolve_fetch(output_path, True)
        ga_file = glob.glob("%s/data/*.ga" % (output_path))[0]

        # B.
        ga_dict = None
        with open(ga_file) as handle:
            ga_dict = json.loads(handle.read())
        if ga_dict is not None:
            wf_mine = gi.workflows.import_workflow_dict(ga_dict)

    finally:
        shutil.rmtree(tmp_path)
	
    return wf_mine

if __name__ == '__main__':
    app.run(threaded=True)
