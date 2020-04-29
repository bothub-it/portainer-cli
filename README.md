# Portainer CLI

Powered by [Ilhasoft's Web Team](http://www.ilhasoft.com.br/en/).

Portainer CLI is a Python software to use in command line. Use this command line interface to easy communicate with your [Portainer](https://portainer.io/) application, like in a continuous integration and continuous deployment environments.

## Install

```
pip install [--user] portainer-cli
```

## Usage

### Global flags

| Flag | Description |
|--|--|
| `-l` or `--local` | Save and load configuration file (`.portainer-cli.json`) in current directory. |
| `-d` or `--debug` | Enable DEBUG messages in stdout |

### configure command

Configure Portainer HTTP service base url.

```bash
portainer-cli configure base_url
```

**E.g:**

```bash
portainer-cli configure http://10.0.0.1:9000/
```

### login command

Identify yourself and take action.

```bash
portainer-cli login username password
```

**E.g:**

```bash
portainer-cli login douglas d1234
```

### create_stack command

Create a stack.

```bash
portainer-cli create_stack -n stack_name -e endpoint_id -sf stack_file
```

**E.g:**

```bash
portainer-cli create_stack -n stack_name -e 1 stack-test -sf docker-compose.yml
```

#### Flags

| Flag | Description |
|--|--|
| `-n` or `-stack-name` | Stack name |
| `-e` or `-endpoint-id` | Endpoint id (required) |
| `-sf` or `-stack-file` |Stack file |
| `-ef` or `-env-file` | Pass env file path, usually `.env` |

### update_stack command

Update a stack.

```bash
portainer-cli update_stack -s stack_id -e endpoint_id -sf stack_file
```

**E.g:**

```bash
portainer-cli update_stack -s 18 -e 1 -sf docker-compose.yml
```

#### Environment variables arguments

```bash
portainer-cli update_stack id -s stack_id -e endpoint_id -sf stack_file --env.var=value
```

Where `var` is the environment variable name and `value` is the environment variable value.

#### Flags

| Flag | Description |
|--|--|
| `-s` or `-stack-id` | Stack id |
| `-e` or `-endpoint-id` | Endpoint id (required) |
| `-sf` or `-stack-file` |Stack file |
| `-ef` or `-env-file` | Pass env file path, usually `.env` |
| `-p` or `--prune` | Prune services |
| `-c` or `--clear-env` | Clear all environment variables |

### create_or_update_stack command

Create or update a stack based on it's name.

```bash
portainer-cli create_or_update_stack -n stack_name -e endpoint_id -sf stack_file
```

**E.g:**

```bash
portainer-cli update_stack -s 18 -e 1 -sf docker-compose.yml
```

#### Environment variables arguments

```bash
portainer-cli create_or_update_stack -n stack_name -e endpoint_id -sf stack_file --env.var=value
```

Where `var` is the environment variable name and `value` is the environment variable value.

#### Flags

| Flag | Description |
|--|--|
| `-n` or `-stack-name` | Stack name |
| `-e` or `-endpoint-id` | Endpoint id (required) |
| `-sf` or `-stack-file` |Stack file |
| `-ef` or `-env-file` | Pass env file path, usually `.env` |
| `-p` or `--prune` | Prune services |
| `-c` or `--clear-env` | Clear all environment variables |

### update_stack_acl command

Update acl associated to a stack

```bash
portainer-cli update_stack_acl -s stack_id -e endpoint_id -o ownership_type
```

Remark : you can either update by stack_id or stack_name (`-s` or `-n`)

**E.g:**

```bash
portainer-cli update_stack_acl -n stack-test -e 1 -o restricted -u user1,user2 -t team1,team2
```

#### Flags

| Flag | Description |
|--|--|
| `-s` or `-stack-id` | Stack id |
| `-n` or `-stack-name` | Stack name |
| `-e` or `-endpoint-id` | Endpoint id (required) |
| `-o` or `-ownership-type` | Ownership type (`admin`|`restricted`,`public`) (required) |
| `-u` or `-users` | Comma separated list of user names (when `restricted`) |
| `-t` or `-teams` | Comma separated list of team names (when `restricted`) |
| `-c` or `-clear` | Clear users and teams before updateing them (when `restricted`) |

### get_stack_id command

Get stack id by it's name. return -1 if the stack does not exist

```bash
portainer-cli get_stack_id -n stack_name -e endpoint_id
```

**E.g:**

```bash
portainer-cli get_stack_id -n stack-test -e 1
```

#### Flags

| Flag | Description |
|--|--|
| `-n` or `-stack-name` | Stack name |
| `-e` or `-endpoint-id` | Endpoint id (required) |

### update_registry command

Update registry.

```bash
portainer-cli update_registry id [-name] [-url]
```

**E.g:**

```bash
portainer-cli update_registry 1 -name="Some registry" -url="some.url.com/r"
```

#### Authentication

You can use authentication passing `-a` or `--authentication` flag, but you must pass the `-username` and `-password` options.

```bash
portainer-cli update_registry 1 -a -username=douglas -password=d1234
```

### request command

Make a request.

```bash
portainer-cli request path [method=GET] [data]
```

**E.g:**

```bash
portainer-cli request status
```

#### Flags

| Flag | Description |
|--|--|
| `-p` or `--printc` | Print response content in stdout. |

## Development

This project use [Pipenv](https://pipenv.readthedocs.io/en/latest/) to manager Python packages.

With Pipenv installed, run `make install` to install all development packages dependencies.

Run `make lint` to run [flake8](http://flake8.pycqa.org/en/latest/) following PEP8 rules.

Run `make` or `make sdist` to create/update `dist` directory.
