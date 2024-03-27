# CLI for interactions with Salad. 

### Installation
This does NOT compile anything. Its just a raw python script that interacts with the API and uses argparse for ease of use.

To install with windows, clone this repo to `C:\ProgramData\`, and add `C:\ProgramData\SaladCLI\bin\` to your system PATH variable.
written on Python 3.11.5 with `pip install PyYAML==6.0.1 requests==2.31.0`. Not tested on any other version, but will probably work on many versions.

If you prefer to not install packages system-wide, use a virtual environment and modify `salad.bat` to `@path\to\python C:\ProgramData\SaladCLI\src\salad.py %*`

For linux, one would need to make a few modifications:

Clone to `/opt/SaladCLI`

Modify `salad.bat`:
`sudo nano /opt/SaladCLI/bin/salad.bat`

```
#!/bin/bash
python3 /opt/SaladCLI/src/salad.py "$@"
```

If you prefer to not install packages system-wide, use a virtual environment and modify `salad.bat` to use your python exe.

Rename `salad.bat` to `salad` and move it to a location in your PATH, such as `/usr/local/bin/`
`sudo mv /opt/SaladCLI/bin/salad.bat /usr/local/bin/salad`

Make the script executable:
`sudo chmod +x /usr/local/bin/salad`

### Usage
1. `salad login` to login to your account with an API key. It saves your credentials in `~/.salad/config`
2. `salad setup` to setup organization and project. It saves your credentials in `~/.salad/config`
3. `salad get quotas` to get organization quotas.
4. `salad list gpus` to get gpus and their IDs. required to creating container groups.
5. `salad cgroup -h` help on all of the container group operations.
```
usage: salad cgroup [-h] {list,create,get,update,delete,start,restart,stop,errors} ...

positional arguments:
  {list,create,get,update,delete,start,restart,stop,errors}
    list                List container groups
    create              Create container group
    get                 Get container group
    update              Update container group
    delete              Delete container group
    start               Start container group
    restart             Restart container group
    stop                Stop container group
    errors              Get container group workload errors
```
6. get, update, delete, start, restart, stop, and errors, use the container group name with `-n` or `--name`.
7. `salad cinst` to interact with container instances. Requires container group name and machine id with --name/-n --machine_id/-m
```
usage: salad cinst [-h] {list,reallocate,recreate,restart} ...

positional arguments:
  {list,reallocate,recreate,restart}
    list                List container instances
    reallocate          Reallocate container instance
    recreate            Recreate container instance
    restart             Restart container instance

options:
  -h, --help            show this help message and exit
```
8. `salad cgroup create` uses a .yaml file with keyword `--file/-f`
This .yaml file corresponds with the payload json required by `https://docs.salad.com/reference/create_container_group` EXCEPT the storage_amount, which we already multiply by 1073741824.

EXAMPLE FILE:
salad_config.yaml```
container:
  resources:
    cpu: 4
    memory: 2048
    gpu_classes:
    - f51baccc-dc95-40fb-a5d1-6d0ee0db31d2
    storage_amount: 5
  environment_variables:
    envkey: envvalue
  logging:
    new_relic:
      host: 1.2.3.4.5
      ingestion_key: '123123'
    http:
      format: json
      compression: gzip
      host: 1.2.3.4
      port: 1234
      user: test
      password: test
      headers:
      - name: logging_header
        value: val
  registry_authentication:
    docker_hub:
      username: usertest
      personal_access_token: accesstoken123
  image: user/image:tag
  command:
  - test_startup.py
  - test_readiness.py
autostart_policy: true
restart_policy: on_failure
networking:
  protocol: http
  auth: true
  port: 1234
liveness_probe:
  http:
    path: 1.2.3.4
    port: 1234
  initial_delay_seconds: 5
  period_seconds: 5
  timeout_seconds: 5
  success_threshold: 5
  failure_threshold: 5
startup_probe:
  http:
    path: '123'
name: containername
display_name: ContainerName
replicas: 4
```
