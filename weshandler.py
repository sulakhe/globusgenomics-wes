import time
import json

def get_filepath(UUID):
    GALAXY_DATABASE_CONN = "postgresql://galaxy:globus_genomics_pass@rds.ops.globusgenomics.org:5432/galaxy_nihcommons"
    galaxy_db_conn = sa.create_engine(GALAXY_DATABASE_CONN).connect()
    galaxy_db_meta = sa.MetaData(bind=galaxy_db_conn)

    dataset_table = sa.Table("dataset", galaxy_db_meta, autoload=True)

    dataset_id = galaxy_db_conn.execute(sa.sql.select([dataset_table.c.id]).where(dataset_table.c.uuid == UUID)).fetchone()[0]
    dir_num =  get_dir_num(dataset_id)
    file_path = "/scratch/galaxy/files/{0}/dataset_{1}.dat".format(get_dir_num(dataset_id), dataset_id)
    return file_path

def get_dir_num(dataset_id):
  if dataset_id < 1000:
    return "000"
  tmp = str(dataset_id)[:-3]
  if len(tmp) == 1:
    return "00{0}".format(tmp)
  else:
    return "0{0}".format(tmp)

def __get_file_json(file_path):
    with open(file_path) as f:
        data = json.load(f)
    return data

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

    outputs = {}
    if history_state == 'ok':
        for content in gi.histories.show_history(invocation['history_id'], contents=True):
            if "Minid for history" in content['name'] and content['deleted'] is False:
                id = content['id']
                dataset_info = gi.datasets.show_dataset(id)
                UUID = dataset_info['uuid'].replace("-", "")
                file_path = get_filepath(UUID)
                outputs = __get_file_json(file_path)

    workflow_log = { "name": "string", "cmd": [ "string" ], "start_time": invocation["update_time"], "end_time": "string", "stdout": "string", "stderr": "string", "exit_code": 0 }
    return { "outputs" : outputs, "workflow_id" : invocation_id, "state" : history_state, "task_logs": invocation['steps'], "workflow_log" : workflow_log}

def __delete_workflow(gi, invocation_id):
	## Delete the workflow with exception handling:
    (wf_id, inv_id) = invocation_id.split("-")
    invocation = gi.workflows.show_invocation(wf_id, inv_id)
    del_inv = gi.workflows.cancel_invocation(invocation['workflow_id'], inv_id)
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
