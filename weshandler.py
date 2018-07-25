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
                history_state = gi.histories.get_status(invoke['history_id'])['state']
                wf_wes_id = "%s-%s" % (wf['id'], invoke['id'])
                invocations.append( { "workflow_id" : wf_wes_id, "state" : history_state })
    return { "workflows": invocations }

def __get_workflow_status(gi, invocation_id):
    (wf_id, inv_id) = invocation_id.split("-")
    invocation = gi.workflows.show_invocation(wf_id, inv_id)
    history_state = gi.histories.get_status(invocation['history_id'])['state']
    return { "workflow_id" : invocation_id, "state" : history_state }

def __get_workflow_details(gi, invocation_id):
    (wf_id, inv_id) = invocation_id.split("-")
    invocation = gi.workflows.show_invocation(wf_id, inv_id)
    history_state = gi.histories.get_status(invocation['history_id'])['state']
    workflow_log = { "name": "string", "cmd": [ "string" ], "start_time": invocation["update_time"], "end_time": "string", "stdout": "string", "stderr": "string", "exit_code": 0 }
    return { "workflow_id" : invocation_id, "state" : history_state, "task_logs": invocation['steps'], "workflow_log" : workflow_log}

def __delete_workflow(gi, invocation_id):
	## Delete the workflow with exception handling:
    (wf_id, inv_id) = invocation_id.split("-")
    invocation = gi.workflows.show_invocation(wf_id, inv_id)
    del_inv = gi.workflows.cancel_invocation(invocation['workflow_id'], invocation_id)
    return { "workflow_id" : invocation_id }

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
    submit_wes_id = "%s-%s" % (workflow['id'], res['id'])
    return { "workflow_id" : submit_wes_id }
