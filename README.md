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

### update_stack command

Update stack.

```bash
portainer-cli update_stack id endpoint_id [stack_file] [-env-file]
```

**E.g:**

```bash
portainer-cli update_stack 2 1 docker-compose.yml
```

#### Environment variables arguments

```bash
portainer-cli update_stack id endpoint_id [stack_file] --env.var=value
```

Where `var` is the environment variable name and `value` is the environment variable value.

#### Flags

| Flag | Description |
|--|--|
| `-env-file` | Pass env file path, usually `.env` |
| `-p` or `--prune` | Prune services |
| `-c` or `--clear-env` | Clear all environment variables |

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
