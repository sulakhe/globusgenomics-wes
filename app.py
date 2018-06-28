from flask import Flask, request
from bioblend import galaxy

app = Flask(__name__)


@app.route('/workflow')
def submit_workflow():

    if(request.headers['Authorization']):
        api_key = __get_galaxy_user(request.headers['Authorization'])
    else:
        return Response('Globus Auth token required..', 401, {'WWW-Authenticate': 'Basic realm="Tokens Required"'})

    runid = __submit_workflow()
    return runid


@app.route('/workflow/status/<runid>')
def workflow_status(runid=None):
    print(runid)
    return runid


def __get_galaxy_user(auth):
    globus_user = __get_globus_user(auth)
    print(auth)
    gi = galaxy.GalaxyInstance(url='https://nihcommons.globusgenomics.org', key='62b5adbe879627a4ff1c911f7d0ba657')
    user = gi.users.get_current_user()
    print(user)
    # Map the globus username to Galaxy username

    # if (galaxy user doesn't exist):
    #	__create_galaxy_user(globus_user)
    # 	api_key = __create_API_key(user)
    return user


def __get_globus_user(auth):
    return "sulakhe"


def __submit_workflow():
    return "1234"
