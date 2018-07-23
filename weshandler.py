

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

def __get_workflows():
	return """
    {
      "workflows": []
    }
	"""

def __delete_workflow(workflow_id):
	## Delete the workflow with exception handling:

	return """
    {
      "workflow_id": workflow_id
    }
    """

def __submit_workflow(json_param=None, gi_handle=None, workflow=None):
    # format for CWL_runner_workflow is always the following:
    # params={}
		
    # create a history
    history_name = "topmed_history_cwl_runner_%s" % time.strftime("%a_%b_%d_%Y_%-I:%M:%S_%p",time.localtime(time.time()))
    history = gi.histories.create_history(name=history_name)
    wf_data = {}
    wf_data['workflow_id'] = workflow['id']
    wf_data['ds_map'] = {}
    parameters = {}
    parameters['0'] = {'inputs' : json_param}
    wf_data['parameters'] = parameters
    res = gi.workflows.invoke_workflow(wf_data['workflow_id'], wf_data['ds_map'], params=wf_data['parameters'], history_id=history['id'], import_inputs_to_history=False)
    return res
