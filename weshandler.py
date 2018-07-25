import time

def __service_info():
	return """
	{
		"workflow_type_versions": {		
		},
		"supported_wes_versions": [
			"1.0"
		],
		"workflow_engine_versions": {
			"Globus Genomics": "5.0.0"
		}
	}
	"""

def __get_workflows(gi):
    workflows = gi.workflows.get_workflows()
    invocations = []
    for wf in workflows:
        if 'cwl_tools' in wf['name']:
            for invoke in gi.workflows.get_invocations(wf['id']):
                invocations.append( { "workflow_id" : invoke['id'], "state" : invoke['state'] })
    return { "workflows": invocations }

def __get_workflow_status(gi, invocation_id):
    invocation = gi.workflows.get_invocations(invocation_id)
    return invocation['state']

def __get_workflow_details(gi, invocation_id):
    invocation = gi.workflows.get_invocations(invocation_id)
    details = gi.workflows.show_invocation(invocation['workflow_id'], invocation_id)
    return details

def __delete_workflow(gi, invocation_id):
	## Delete the workflow with exception handling:
    invocation = gi.workflows.get_invocations(invocation_id)
    del_inv = gi.workflows.cancel_invocation(invocation['workflow_id'], invocation_id)
    return del_inv

def __submit_workflow(json_param=None, gi_handle=None, workflow=None):
    # format for CWL_runner_workflow is always the following:
    # params={}
		
    # create a history
    history_name = "topmed_history_cwl_runner_%s" % time.strftime("%a_%b_%d_%Y_%-I:%M:%S_%p",time.localtime(time.time()))
    history = gi_handle.histories.create_history(name=history_name)
    wf_data = {}
    wf_data['workflow_id'] = workflow['id']
    wf_data['ds_map'] = {}
    parameters = {}
    parameters['0'] = {'inputs' : json_param}
    wf_data['parameters'] = parameters
    res = gi_handle.workflows.invoke_workflow(wf_data['workflow_id'], wf_data['ds_map'], params=wf_data['parameters'], history_id=history['id'], import_inputs_to_history=False)
    return res['id']
