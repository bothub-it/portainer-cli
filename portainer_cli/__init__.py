#!/usr/bin/env python
import os
import re
import logging
import json
import plac
import validators
from requests import Request, Session


try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

__version__ = '0.3.0'

logger = logging.getLogger('portainer-cli')

env_arg_regex = r'--env\.(.+)=(.+)'


def env_arg_to_dict(s):
    split = re.split(env_arg_regex, s)
    return (split[1], split[2],)


class PortainerCLI(object):
    COMMAND_CONFIGURE = 'configure'
    COMMAND_LOGIN = 'login'
    COMMAND_REQUEST = 'request'
    COMMAND_CREATE_STACK = 'create_stack'
    COMMAND_UPDATE_STACK = 'update_stack'
    COMMAND_UPDATE_STACK_ACL = 'update_stack_acl'
    COMMAND_CREATE_OR_UPDATE_STACK = 'create_or_update_stack'
    COMMAND_GET_STACK_ID = 'get_stack_id'
    COMMAND_UPDATE_REGISTRY = 'update_registry'
    COMMANDS = [
        COMMAND_CONFIGURE,
        COMMAND_LOGIN,
        COMMAND_REQUEST,
        COMMAND_CREATE_STACK,
        COMMAND_UPDATE_STACK,
        COMMAND_UPDATE_STACK_ACL,
        COMMAND_CREATE_OR_UPDATE_STACK,
        COMMAND_GET_STACK_ID,
        COMMAND_UPDATE_REGISTRY
    ]

    METHOD_GET = 'GET'
    METHOD_POST = 'POST'
    METHOD_PUT = 'PUT'
    METHOD_DELETE = 'DELETE'

    local = False
    _base_url = 'http://localhost:9000/'
    _jwt = None
    _proxies = {}
    _swarm_id = None

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, value):
        if not validators.url(value):
            raise Exception('Insert a valid base URL')
        self._base_url = value if value.endswith('/') else '{}/'.format(value)
        self.persist()

    @property
    def jwt(self):
        return self._jwt

    @jwt.setter
    def jwt(self, value):
        self._jwt = value
        self.persist()

    @property
    def proxies(self):
        return self._proxies

    @proxies.setter
    def proxies(self, value):
        try:
            self._proxies['http'] = os.environ['HTTP_PROXY']
        except KeyError:
            self._proxies['http'] = ''
        try:
            self._proxies['https'] = os.environ['HTTPS_PROXY']
        except KeyError:
            self._proxies['https'] = ''
        if self._proxies['http'] == '' and self._proxies['https'] == '':
            self._proxies = {}

    @property
    def swarm_id(self):
        return self._swarm_id

    @swarm_id.setter
    def swarm_id(self, value):
        self._swarm_id = value
        self.persist()

    @property
    def data_path(self):
        if self.local:
            logger.debug('using local configuration file')
            return '.portainer-cli.json'
        logger.debug('using user configuration file')
        return os.path.join(
            os.path.expanduser('~'),
            '.portainer-cli.json',
        )

    def persist(self):
        data = {
            'base_url': self.base_url,
            'jwt': self.jwt,
        }
        logger.info('persisting configuration: {}'.format(data))
        data_file = open(self.data_path, 'w+')
        data_file.write(json.dumps(data))
        logger.info('configuration persisted in: {}'.format(self.data_path))

    def load(self):
        try:
            data_file = open(self.data_path)
        except FileNotFoundError:
            return
        data = json.loads(data_file.read())
        logger.info('configuration loaded: {}'.format(data))
        self._base_url = data.get('base_url')
        self._jwt = data.get('jwt')

    def configure(self, base_url):
        self.base_url = base_url

    def login(self, username, password):
        response = self.request(
            'auth',
            self.METHOD_POST,
            {
                'username': username,
                'password': password,
            }
        )
        r = response.json()
        jwt = r.get('jwt')
        logger.info('logged with jwt: {}'.format(jwt))
        self.jwt = jwt

    def get_users(self):
        users_url = 'users'
        return self.request(users_url, self.METHOD_GET).json()
    
    # retrieve users by their names
    def get_users_by_name(self, names):
        all_users = self.get_users()
        if not all_users:
            logger.debug('No users found')
            return []
        users=[]
        for name in names:
            # searching for user
            user = next(u for u in all_users if u['Username'] == name)
            if not user:
                logger.warn('User with name \'{}\' not found'.format(name))
            else:
                logger.debug('User with name \'{}\' found'.format(name))
                users.append(user)
        return users
    
    # retrieve users by their names
    def get_users_by_name(self, names):
        all_users = self.get_users()
        all_users_by_name = dict(map(
            lambda u: (u['Username'], u),
            all_users,
        ))
        users = []
        for name in names:
            user = all_users_by_name.get(name)
            if not user:
                logger.warn('User with name \'{}\' not found'.format(name))
            else:
                logger.debug('User with name \'{}\' found'.format(name))
                users.append(user)
        return users
    
    def get_teams(self):
        teams_url = 'teams'
        return self.request(teams_url, self.METHOD_GET).json()

    # retrieve teams by their names
    def get_teams_by_name(self, names):
        all_teams = self.get_teams()
        all_teams_by_name = dict(map(
            lambda u: (u['Name'], u),
            all_teams,
        ))
        teams = []
        for name in names:
            team = all_teams_by_name.get(name)
            if not team:
                logger.warn('Team with name \'{}\' not found'.format(name))
            else:
                logger.debug('Team with name \'{}\' found'.format(name))
                teams.append(team)
        return teams

    def get_stacks(self):
        stack_url = 'stacks'
        return self.request(stack_url, self.METHOD_GET).json()

    def get_stack_by_id(self, stack_id, endpoint_id):
        stack_url = 'stacks/{}?endpointId={}'.format(
            stack_id,
            endpoint_id,
        )
        stack = self.request(stack_url).json()
        if not stack:
            raise Exception('Stack with id={} does not exist'.format(stack_id))
        return stack
    
    def get_stack_by_name(self, stack_name, endpoint_id, mandatory=False):
        result = self.get_stacks()
        if result:
            for stack in result:
                if stack['Name'] == stack_name and stack['EndpointId'] == endpoint_id:
                    return stack
        if mandatory:
            raise Exception('Stack with name={} and endpoint_id={} does not exist'.format(stack_name, endpoint_id))
        else:
            return None

    # Retrieve the stack if. -1 if the stack does not exist
    @plac.annotations(
        stack_name=('Stack name', 'option', 'n'),
        endpoint_id=('Endpoint id', 'option', 'e', int)
    )
    def get_stack_id(self, stack_name, endpoint_id):
        stack = self.get_stack_by_name(stack_name, endpoint_id)
        if not stack:
            logger.debug('Stack with name={} does not exist'.format(stack_name))
            return -1
        logger.debug('Stack with name={} -> id={}'.format(stack_name, stack['Id']))
        return stack['Id']

    def extract_env(self, env_file='', *args):
        if env_file:
            env = {}
            for env_line in open(env_file).readlines():
                env_line = env_line.strip()
                if not env_line or env_line.startswith('#') or '=' not in env_line:
                    continue
                k, v = env_line.split('=', 1)
                k, v = k.strip(), v.strip()
                env[k] = v
        else:
            env_args = filter(
                lambda x: re.match(env_arg_regex, x),
                args,
            )
        env = dict(map(
            lambda x: env_arg_to_dict(x),
            env_args,
        ))
        return env

    @plac.annotations(
            stack_name=('Stack name', 'option', 'n', str),
            endpoint_id=('Endpoint id', 'option', 'e', int),
            stack_file=('Stack file', 'option', 'sf'),
            env_file=('Environment Variable file', 'option', 'ef'),
            prune=('Prune services', 'flag', 'p'),
            clear_env=('Clear all env vars', 'flag', 'c'),
        )
    def create_or_update_stack(self, stack_name, endpoint_id, stack_file='', env_file='', prune=False, clear_env=False, *args):
        logger.debug('create_or_update_stack')
        stack_id = self.get_stack_id(stack_name, endpoint_id)
        if stack_id == -1:
            self.create_stack(stack_name, endpoint_id, stack_file, env_file, *args)
        else:
           self.update_stack(stack_id, endpoint_id, stack_file, env_file, prune, clear_env, *args)

    @plac.annotations(
        stack_name=('Stack name', 'option', 'n'),
        endpoint_id=('Endpoint id', 'option', 'e', int),
        stack_file=('Environment Variable file', 'option', 'sf'),
        env_file=('Environment Variable file', 'option', 'ef')
    )
    def create_stack(self, stack_name, endpoint_id, stack_file='', env_file='', *args):
        logger.info('Creating stack name={}'.format(stack_name))
        stack_url = 'stacks?type=1&method=string&endpointId={}'.format(
            endpoint_id
        )
        swarm_url = 'endpoints/{}/docker/swarm'.format(endpoint_id)
        swarm_id = self.request(swarm_url, self.METHOD_GET).json().get('ID')
        self.swarm_id = swarm_id
        stack_file_content = open(stack_file).read()

        env = self.extract_env(env_file, *args)
        final_env = list(
            map(
                lambda x: {'name': x[0], 'value': x[1]},
                env.items()
            ),
        )
        data = {
            'StackFileContent': stack_file_content,
            'SwarmID': self.swarm_id,
            'Name': stack_name,
            'Env': final_env if len(final_env) > 0 else []
        }
        logger.debug('create stack data: {}'.format(data))
        self.request(
            stack_url,
            self.METHOD_POST,
            data,
        )
    
    def create_or_update_resource_control(self, stack, public, users, teams):
        resource_control = stack['ResourceControl']
        if resource_control and resource_control['Id'] != 0:
            resource_path = 'resource_controls/{}'.format(resource_control['Id'])
            data = {
                    'Public': public,
                    'Users': users,
                    'Teams': teams
                }
            logger.debug('Updating stack acl {} for stack {}: {}'.format(resource_control['Id'], stack['Id'], data))
            self.request(resource_path, self.METHOD_PUT, data)
        else:
            resource_path = 'resource_controls'
            data = {
                    'Type': 'stack',
                    'ResourceID': stack['Name'],
                    'Public': public,
                    'Users': users,
                    'Teams': teams
                }
            logger.debug('Creating stack acl for stack {}: {}'.format(stack['Id'], data))
            self.request(resource_path, self.METHOD_POST, data)


    @plac.annotations(
        stack_id=('Stack id', 'option', 's', int),
        stack_name=('Stack name', 'option', 'n', str),
        endpoint_id=('Endpoint id', 'option', 'e', int),
        ownership_type=('Ownership type', 'option', 'o', str, ['admin', 'restricted', 'public']),
        users=('Allowed usernames (comma separated - restricted ownership_type only)', 'option', 'u'),
        teams=('Allowed teams (comma separated - restricted ownership_type only)', 'option', 't'),
        clear=('Clear acl (restricted ownership_type only)', 'flag', 'c')
    )
    def update_stack_acl(self, stack_id, stack_name, endpoint_id, ownership_type, users, teams, clear=False):
        stack = None
        if stack_id:
            stack = self.get_stack_by_id(stack_id, endpoint_id)
        elif stack_name:
            stack = self.get_stack_by_name(stack_name, endpoint_id, True)
        else:
            raise Exception('Please provide either stack_name or stack_id')

        logger.info('Updating acl of stack name={} - type={}'.format(stack['Name'], ownership_type))

        resource_control = stack['ResourceControl']

        if ownership_type == 'admin':
            if resource_control and resource_control['Id'] != 0:
                logger.debug('Deleting resource control with id {}'.format(resource_control['Id']))
                resource_path = 'resource_controls/{}'.format(resource_control['Id'])
                logger.debug('resource_path : {}'.format(resource_path))
                self.request(resource_path, self.METHOD_DELETE)
            else:
                logger.debug('Nothing to do')
        elif ownership_type == 'public':
            self.create_or_update_resource_control(stack, True, [], [])
        elif ownership_type == 'restricted':
            users = map(lambda u: u['Id'], self.get_users_by_name(users.split(',')))
            teams = map(lambda t: t['Id'], self.get_teams_by_name(teams.split(',')))

            if (not clear) and resource_control:
                logger.debug('Merging existing users / teams')
                users = list(set().union(users, map(lambda u: u['UserId'], resource_control['UserAccesses'])))
                teams = list(set().union(teams, map(lambda t: t['TeamId'], resource_control['TeamAccesses'])))

            self.create_or_update_resource_control(stack, False, users, teams)

    @plac.annotations(
        stack_id=('Stack id', 'option', 's', int),
        endpoint_id=('Endpoint id', 'option', 'e', int),
        stack_file=('Stack file', 'option', 'sf'),
        env_file=('Environment Variable file', 'option', 'ef'),
        prune=('Prune services', 'flag', 'p'),
        clear_env=('Clear all env vars', 'flag', 'c'),
    )
    def update_stack(self, stack_id, endpoint_id, stack_file='', env_file='',
                     prune=False, clear_env=False, *args):
        logger.info('Updating stack id={}'.format(stack_id))
        stack_url = 'stacks/{}?endpointId={}'.format(
            stack_id,
            endpoint_id,
        )
        current = self.get_stack_by_id(stack_id, endpoint_id)
        stack_file_content = ''
        if stack_file:
            stack_file_content = open(stack_file).read()
        else:
            stack_file_content = self.request(
                'stacks/{}/file?endpointId={}'.format(
                    stack_id,
                    endpoint_id,
                )
            ).json().get('StackFileContent')

        env = self.extract_env(env_file, *args)

        if not clear_env:
            current_env = dict(
                map(
                    lambda x: (x.get('name'), x.get('value'),),
                    current.get('Env'),
                ),
            )
            current_env.update(env)
            env = current_env
        final_env = list(
            map(
                lambda x: {'name': x[0], 'value': x[1]},
                env.items()
            ),
        )
        data = {
            'Id': stack_id,
            'StackFileContent': stack_file_content,
            'Prune': prune,
            'Env': final_env if len(final_env) > 0 else current.get('Env'),
        }
        logger.debug('update stack data: {}'.format(data))
        self.request(
            stack_url,
            self.METHOD_PUT,
            data,
        )

    @plac.annotations(
        name=('Name', 'option'),
        url=('URL', 'option'),
        authentication=('Use authentication', 'flag', 'a'),
        username=('Username', 'option'),
        password=('Password', 'option'),
    )
    def update_registry(self, id, name='', url='', authentication=False,
                        username='', password=''):
        assert not authentication or (authentication and username and password)
        registry_url = 'registries/{}'.format(id)
        current = self.request(registry_url).json()
        data = {
            'Name': name or current.get('Name'),
            'URL': url or current.get('URL'),
            'Authentication': authentication,
            'Username': username or current.get('Username'),
            'Password': password,
        }
        self.request(
            registry_url,
            self.METHOD_PUT,
            data,
        )

    @plac.annotations(
        printc=('Print response content', 'flag', 'p'),
    )
    def request(self, path, method=METHOD_GET, data='', printc=False):
        url = '{}api/{}'.format(
            self.base_url,
            path,
        )
        session = Session()
        request = Request(method, url)
        prepped = request.prepare()
        if data:
            prepped.headers['Content-Type'] = 'application/json'
            try:
                json.loads(data)
                prepped.body = data
            except Exception:
                prepped.body = json.dumps(data)
            prepped.headers['Content-Length'] = len(prepped.body)
        if self.jwt:
            prepped.headers['Authorization'] = 'Bearer {}'.format(self.jwt)
        response = session.send(prepped, proxies=self.proxies, verify=False)
        logger.debug('request response: {}'.format(response.content))
        response.raise_for_status()
        if printc:
            print(response.content.decode())
        return response

    @plac.annotations(
        command=(
            'Command',
            'positional',
            None,
            str,
            COMMANDS,
        ),
        debug=('Enable debug mode', 'flag', 'd'),
        local=('Use local/dir configuration', 'flag', 'l'),
    )
    def main(self, command, debug=False, local=local, *args):
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        self.local = local
        self.load()
        self.proxies = {}
        if command == self.COMMAND_CONFIGURE:
            plac.call(self.configure, args)
        elif command == self.COMMAND_LOGIN:
            plac.call(self.login, args)
        elif command == self.COMMAND_CREATE_STACK:
            plac.call(self.create_stack, args)
        elif command == self.COMMAND_UPDATE_STACK:
            plac.call(self.update_stack, args)
        elif command == self.COMMAND_UPDATE_STACK_ACL:
            plac.call(self.update_stack_acl, args)
        elif command == self.COMMAND_CREATE_OR_UPDATE_STACK:
            plac.call(self.create_or_update_stack, args)
        elif command == self.COMMAND_GET_STACK_ID:
            plac.call(self.get_stack_id, args)
        elif command == self.COMMAND_UPDATE_REGISTRY:
            plac.call(self.update_registry, args)
        elif command == self.COMMAND_REQUEST:
            plac.call(self.request, args)
