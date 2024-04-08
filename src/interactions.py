import requests
import os
from pathlib import Path
from json import dumps

def _read_config():
	config = {}
	try:
		with open(Path(os.path.expanduser('~/.salad/config')), 'r') as f:
			for line in f:
				key, value = line.strip().split('=', 1)
				config[key] = value
	except FileNotFoundError:
		print("Config file not found. Please run 'salad login' and 'salad setup'.")
		raise
	return config

def _get_headers():
	config = _read_config()
	return {
		"accept": "application/json", 
		"Salad-Api-Key": config['api_key']
	}

def _get_base_url():
	config = _read_config()
	return f"https://api.salad.com/api/public/organizations/{config['organization']}"

def _get_headers_and_base_url():
	return _get_headers(), _get_base_url()

# get quotas

def get_quotas():
	headers, base_url = _get_headers_and_base_url()

	quotas_url = f"{base_url}/quotas"
	response = requests.get(quotas_url, headers=headers)

	try: return response.json()
	except: return response.text

# list gpus

def list_gpus():
	headers, base_url = _get_headers_and_base_url()

	gpus_url = f"{base_url}/gpu-classes"
	response = requests.get(gpus_url, headers=headers)

	try: return response.json()['items']
	except: return response.text

# list container groups

def _get_cgroups_url():
	config = _read_config()
	base_url = _get_base_url()
	return f"{base_url}/projects/{config['project']}/containers"

def _get_headers_and_cgroups_url():
	return _get_headers(), _get_cgroups_url()

def list_cgroups():
	headers, containers_url = _get_headers_and_cgroups_url()

	response = requests.get(containers_url, headers=headers)
	try: return response.json()['items']
	except: return response.text

# create container group

from pydantic import BaseModel, Field, UUID4, validator, ValidationError
from typing import Literal

'''
COMMENTED OUT BECAUSE SALAD ALWAYS UPDATES THEIR API AND I DON'T WANT TO KEEP UP WITH IT

class TagsModel(BaseModel):
	name: str
	value: str

class DataDogLogModel(BaseModel):
	host: str
	api_key: str
	tags: list[TagsModel] | None = None

class NewRelicLogModel(BaseModel):
	host: str
	ingestion_key: str

class SplunkLogModel(BaseModel):
	host: str
	token: str

class TCPLogModel(BaseModel):
	host: str
	port: int

class HTTPLogModel(BaseModel):
	host: str
	port: int = Field(..., gt=0, le=65535)
	user: str | None = None
	password: str | None = None
	path: str | None = None
	format: Literal['json', 'json_lines']
	headers: list[TagsModel] | None = None
	compression: Literal['none', 'gzip']

class RegistryBasicAuthModel(BaseModel):
	username: str
	password: str

class RegistryGCPGCRModel(BaseModel):
	service_key: str

class RegistryAWSECRModel(BaseModel):
	access_key_id: str
	secret_access_key: str

class RegistryDockerHubModel(BaseModel):
	username: str
	personal_access_token: str

class CGroupResourcesModel(BaseModel):
	cpu: int = Field(..., gt=0, le=16)
	memory: int = Field(..., gt=0, le=30720)
	gpu_classes: list[UUID4] = Field(..., min_items=1)
	storage_amount: int | None = Field(None, gt=1, le=50)

	@validator('storage_amount')
	def convert_to_bytes(cls, v):
		if v is None: return v
		return v * 1024 * 1024 * 1024

class NetworkingModel(BaseModel):
	protocol: Literal['http']
	port: int = Field(..., gt=0, le=65535)
	auth: bool

class NetworkingUpdateModel(BaseModel):
	port: int | None = Field(None, gt=0, le=65535)

class HTTPProbeModel(BaseModel):
	path: str
	port: int = Field(..., gt=0, le=65535)

class TCPProbeModel(BaseModel):
	port: int = Field(..., gt=0, le=65535)

class GRPCProbeModel(BaseModel):
	service: str
	port: int = Field(..., gt=0, le=65535)

class ExecProbeModel(BaseModel):
	command: list[str]

class ProbeModel(BaseModel):
	http: HTTPProbeModel | None = None
	tcp: TCPProbeModel | None = None
	grpc: GRPCProbeModel | None = None
	exec: ExecProbeModel | None = None
	initial_delay_seconds: int = Field(..., ge=0)
	period_seconds: int = Field(..., gt=0)
	timeout_seconds: int = Field(..., gt=0)
	success_threshold: int = Field(..., gt=0)
	failure_threshold: int = Field(..., gt=0)

class QueueConnectionModel(BaseModel):
	path: str
	port: int = Field(..., gt=0, le=65535)
	queue_name: str

class ContainerCreateModel(BaseModel):
	image: str
	resources: CGroupResourcesModel
	command: list[str] | None = None
	environment_variables : dict[str, str] | None = None
	logging: dict[Literal['datadog', 'new_relic', 'splunk', 'tcp', 'http'], DataDogLogModel | NewRelicLogModel | SplunkLogModel | TCPLogModel | HTTPLogModel] | None = None
	registry_authentication: dict[Literal['basic', 'gcp_gcr', 'aws_ecr', 'docker_hub'], RegistryBasicAuthModel | RegistryGCPGCRModel | RegistryAWSECRModel | RegistryDockerHubModel] | None = None

class CGroupModel(BaseModel):
	name: str = Field(..., min_length=2, max_length=63, pattern=r'^[a-z][a-z0-9-]{0,61}[a-z0-9]$')
	display_name: str | None = Field(None, min_length=2, max_length=63, pattern=r'^[ ,-.0-9A-Za-z]+$')
	container: ContainerCreateModel
	autostart_policy: bool
	restart_policy: Literal['always', 'on_failure', 'never']
	replicas: int = Field(..., gt=0, le=250)
	country_codes: list[str] = ['af']
	networking: NetworkingModel | None = None
	liveness_probe: ProbeModel | None = None
	readiness_probe: ProbeModel | None = None
	startup_probe: ProbeModel | None = None
	queue_connection: QueueConnectionModel | None = None

class ContainerUpdateModel(BaseModel):
	image: str | None = None
	resources: CGroupResourcesModel | None = None
	command: list[str] | None = None
	environment_variables : dict[str, str] | None = None
	logging: dict[Literal['datadog', 'new_relic', 'splunk', 'tcp', 'http'], DataDogLogModel | NewRelicLogModel | SplunkLogModel | TCPLogModel | HTTPLogModel] | None = None
	registry_authentication: dict[Literal['basic', 'gcp_gcr', 'aws_ecr', 'docker_hub'], RegistryBasicAuthModel | RegistryGCPGCRModel | RegistryAWSECRModel | RegistryDockerHubModel] | None = None

class CGroupUpdateModel(BaseModel):
	display_name: str | None = Field(None, min_length=2, max_length=63, pattern=r'^[ ,-.0-9A-Za-z]+$')
	container: ContainerUpdateModel | None = None
	replicas: int | None = Field(None, gt=0, le=250)
	country_codes: list[str] | None = None
	networking: NetworkingUpdateModel | None = None
	liveness_probe: ProbeModel | None = None
	readiness_probe: ProbeModel | None = None
	startup_probe: ProbeModel | None = None'''

def create_cgroup(payload: dict):

	headers, containers_url = _get_headers_and_cgroups_url()
	response = requests.post(containers_url, headers=headers, json=payload)
	try: return response.json()
	except: return response.text

# get container group

def get_cgroup(container_group_name: str):
	headers, containers_url = _get_headers_and_cgroups_url()

	response = requests.get(f"{containers_url}/{container_group_name}", headers=headers)
	try: return response.json()
	except: return response.text

# update container group

def update_cgroup(container_group_name: str, payload: dict):

	headers, containers_url = _get_headers_and_cgroups_url()
	headers["accept"] = "application/merge-patch+json"
	headers["content-type"] = "application/merge-patch+json"

	response = requests.patch(
		f"{containers_url}/{container_group_name}", 
		headers=headers, 
		data=dumps(payload),
	)
	try: return response.json()
	except: return response.text

# delete container group

def delete_cgroup(container_group_name: str):
	headers, containers_url = _get_headers_and_cgroups_url()

	response = requests.delete(f"{containers_url}/{container_group_name}", headers=headers)
	return {'status': response.status_code}

# container group operations

def cgroup_operation(container_group_name: str, operation: Literal['start', 'restart', 'stop']):
	headers, containers_url = _get_headers_and_cgroups_url()

	response = requests.post(f"{containers_url}/{container_group_name}/{operation}", headers=headers)
	return {'status': response.status_code}

# list instances

def list_cinst(container_group_name: str):
	headers, containers_url = _get_headers_and_cgroups_url()

	response = requests.get(f"{containers_url}/{container_group_name}/instances", headers=headers)
	try: return response.json()['instances']
	except: return response.text

# container instance operations

def cinst_operation(container_group_name: str, machine_id: str, operation: Literal['reallocate', 'recreate', 'restart']):
	headers, containers_url = _get_headers_and_cgroups_url()

	response = requests.post(f"{containers_url}/{container_group_name}/instances/{machine_id}/{operation}", headers=headers)
	return {'status': response.status_code}

# get workload errors

def get_cgroup_workload_errors(container_group_name: str):
	headers, containers_url = _get_headers_and_cgroups_url()

	response = requests.get(f"{containers_url}/{container_group_name}/errors", headers=headers)
	try: return response.json()['items']
	except: return response.text