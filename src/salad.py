#!python

from interactions import (
	get_quotas, 
	list_gpus, 
	list_cgroups, 
	create_cgroup, 
	get_cgroup,
	update_cgroup,
	delete_cgroup,
	cgroup_operation,
	get_cgroup_workload_errors,
	list_cinst,
	cinst_operation
)
import argparse
import sys
from pathlib import Path
import os
import yaml
import json

def pretty_print(data):
	print(json.dumps(data, indent=4))

def setup_cli():
	parser = argparse.ArgumentParser(prog='salad')
	subparsers = parser.add_subparsers(dest='command')

	# Login command
	login_parser = subparsers.add_parser('login', help='Login with API key')

	# Setup command
	setup_parser = subparsers.add_parser('setup', help='Setup organization and project')

	# Get parser
	get_parser = subparsers.add_parser('get', help='Get resources')
	get_subparsers = get_parser.add_subparsers(dest='get_command')

	# List parser
	list_parser = subparsers.add_parser('list', help='List resources')
	list_subparsers = list_parser.add_subparsers(dest='list_command')

	# CGroup Parser
	cgroup_parser = subparsers.add_parser('cgroup', help='Manage container groups')
	cgroup_subparsers = cgroup_parser.add_subparsers(dest='cgroup_command')

	# CInst Parser
	cinst_parser = subparsers.add_parser('cinst', help='Manage container instances')
	cinst_subparsers = cinst_parser.add_subparsers(dest='cinst_command')

	# Get commands
	quotas_parser = get_subparsers.add_parser('quotas', help='Retrieve quotas')

	# List commands
	gpus_parser = list_subparsers.add_parser('gpus', help='List available GPUs')

	# CGroup commands
	cgroup_list_parser = cgroup_subparsers.add_parser('list', help='List container groups')

	cgroup_create_parser = cgroup_subparsers.add_parser('create', help='Create container group')
	cgroup_create_parser.add_argument('--file', '-f', help='YAML file containing container group configuration', required=True)

	cgroup_get_parser = cgroup_subparsers.add_parser('get', help='Get container group')
	cgroup_get_parser.add_argument('--name', '-n', help='Name of container group', required=True)

	cgroup_update_parser = cgroup_subparsers.add_parser('update', help='Update container group')
	cgroup_update_parser.add_argument('--name', '-n', help='Name of container group', required=True)
	cgroup_update_parser.add_argument('--file', '-f', help='YAML file containing container group configuration', required=True)

	cgroup_delete_parser = cgroup_subparsers.add_parser('delete', help='Delete container group')
	cgroup_delete_parser.add_argument('--name', '-n', help='Name of container group', required=True)

	cgroup_start_parser = cgroup_subparsers.add_parser('start', help='Start container group')
	cgroup_start_parser.add_argument('--name', '-n', help='Name of container group', required=True)

	cgroup_restart_parser = cgroup_subparsers.add_parser('restart', help='Restart container group')
	cgroup_restart_parser.add_argument('--name', '-n', help='Name of container group', required=True)

	cgroup_stop_parser = cgroup_subparsers.add_parser('stop', help='Stop container group')
	cgroup_stop_parser.add_argument('--name', '-n', help='Name of container group', required=True)

	cgroup_error_parser = cgroup_subparsers.add_parser('errors', help='Get container group workload errors')
	cgroup_error_parser.add_argument('--name', '-n', help='Name of container group', required=True)

	# CInst commands
	cinst_list_parser = cinst_subparsers.add_parser('list', help='List container instances')
	cinst_list_parser.add_argument('--name', '-n', help='Name of container group', required=True)

	cinst_reallocate_parser = cinst_subparsers.add_parser('reallocate', help='Reallocate container instance')
	cinst_reallocate_parser.add_argument('--name', '-n', help='Name of container group', required=True)
	cinst_reallocate_parser.add_argument('--machine_id', '-m', help='Machine ID of container instance', required=True)

	cinst_recreate_parser = cinst_subparsers.add_parser('recreate', help='Recreate container instance')
	cinst_recreate_parser.add_argument('--name', '-n', help='Name of container group', required=True)
	cinst_recreate_parser.add_argument('--machine_id', '-m', help='Machine ID of container instance', required=True)

	cinst_restart_parser = cinst_subparsers.add_parser('restart', help='Restart container instance')
	cinst_restart_parser.add_argument('--name', '-n', help='Name of container group', required=True)
	cinst_restart_parser.add_argument('--machine_id', '-m', help='Machine ID of container instance', required=True)

	return parser

def load_yaml_file(file_path):
	try:
		with open(file_path, 'r') as file:
			return yaml.safe_load(file)
	except Exception as e:
		print(f"Error reading YAML file: {e}")
		sys.exit(1)

def handle_login():
	api_key = input("Enter your API key: ")
	# Save API key to the current user's .salad folder
	salad_path = Path(os.path.expanduser('~/.salad'))
	salad_path.mkdir(exist_ok=True)
	with open(salad_path / 'config', 'w') as f:
		f.write(f"api_key={api_key}\n")

	handle_setup()

	print("Login successful!")

def handle_setup():
	organization = input("Enter your organization: ")
	project = input("Enter your project: ")
	# Save organization and project to the current user's .salad folder
	with open(Path(os.path.expanduser('~/.salad/config')), 'a') as f:
		f.write(f"organization={organization}\nproject={project}\n")

def main():
	try:
		parser = setup_cli()
		args = parser.parse_args()

		if args.command == 'login':
			handle_login()

		elif args.command == 'setup':
			handle_setup()

		elif args.command == 'get':

			if args.get_command == 'quotas':
				pretty_print(get_quotas())

			else:
				parser.print_help()

		elif args.command == 'list':
			if args.list_command == 'gpus':
				pretty_print(list_gpus())
			elif args.list_command == 'cgroups':
				pretty_print(list_cgroups())

		elif args.command == 'cgroup':
			if args.cgroup_command == 'list':
				pretty_print(list_cgroups())
			elif args.cgroup_command == 'create':
				config = load_yaml_file(args.file)
				if config['container']['resources'].get('storage_amount'):
					config['container']['resources']['storage_amount'] = config['container']['resources']['storage_amount'] * 1024 * 1024 * 1024
				pretty_print(create_cgroup(config))
			elif args.cgroup_command == 'get':
				pretty_print(get_cgroup(args.name))
			elif args.cgroup_command == 'update':
				config = load_yaml_file(args.file)
				if config.get('container', {}).get('resources', {}).get('storage_amount'):
					config['container']['resources']['storage_amount'] = config['container']['resources']['storage_amount'] * 1024 * 1024 * 1024
				pretty_print(update_cgroup(args.name, config))
			elif args.cgroup_command == 'delete':
				pretty_print(delete_cgroup(args.name))
			elif args.cgroup_command == 'start':
				pretty_print(cgroup_operation(args.name, 'start'))
			elif args.cgroup_command == 'restart':
				pretty_print(cgroup_operation(args.name, 'restart'))
			elif args.cgroup_command == 'stop':
				pretty_print(cgroup_operation(args.name, 'stop'))
			elif args.cgroup_command == 'errors':
				pretty_print(get_cgroup_workload_errors(args.name))
			
		elif args.command == 'cinst':
			if args.cinst_command == 'list':
				pretty_print(list_cinst(args.name))
			elif args.cinst_command == 'reallocate':
				pretty_print(cinst_operation(args.name, args.machine_id, 'reallocate'))
			elif args.cinst_command == 'recreate':
				pretty_print(cinst_operation(args.name, args.machine_id, 'recreate'))
			elif args.cinst_command == 'restart':
				pretty_print(cinst_operation(args.name, args.machine_id, 'restart'))

		else:
			parser.print_help()
	except KeyboardInterrupt:
		print("Exiting...")
		sys.exit(0)

if __name__ == "__main__":
	main()