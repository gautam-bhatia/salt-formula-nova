# -*- coding: utf-8 -*-
from __future__ import absolute_import, with_statement
from pprint import pprint

# Import python libs
import logging

# Get logging started
log = logging.getLogger(__name__)

# Function alias to not shadow built-ins
__func_alias__ = {
    'list_': 'list'
}

# Define the module's virtual name
__virtualname__ = 'novang'


def __virtual__():
    '''
    Only load this module if nova
    is installed on this minion.
    '''
    if check_nova():
        return __virtualname__
    return (False, 'The nova execution module failed to load: '
            'only available if nova is installed.')


__opts__ = {}


def _authng(profile=None, tenant_name=None):
    '''
    Set up nova credentials
    '''
    if profile:
        credentials = __salt__['config.option'](profile)
        user = credentials['keystone.user']
        password = credentials['keystone.password']
        if tenant_name:
            tenant = tenant_name
        else:
            tenant = credentials['keystone.tenant']
        auth_url = credentials['keystone.auth_url']
        region_name = credentials.get('keystone.region_name', None)
        api_key = credentials.get('keystone.api_key', None)
        os_auth_system = credentials.get('keystone.os_auth_system', None)
        use_keystoneauth = credentials.get('keystone.use_keystoneauth', False)
        verify = credentials.get('keystone.verify', True)
    else:
        user = __salt__['config.option']('keystone.user')
        password = __salt__['config.option']('keystone.password')
        tenant = __salt__['config.option']('keystone.tenant')
        auth_url = __salt__['config.option']('keystone.auth_url')
        region_name = __salt__['config.option']('keystone.region_name')
        api_key = __salt__['config.option']('keystone.api_key')
        os_auth_system = __salt__['config.option']('keystone.os_auth_system')
        use_keystoneauth = __salt__['config.option']('keystone.use_keystoneauth', False)
        verify = __salt__['config.option']('keystone.verify', True)

    kwargs = {
        'username': user,
        'password': password,
        'api_key': api_key,
        'project_id': tenant,
        'auth_url': auth_url,
        'region_name': region_name,
        'os_auth_plugin': os_auth_system,
        'use_keystoneauth': use_keystoneauth,
        'verify': verify,
        'profile': profile
    }
    return SaltNova(**kwargs)


def server_list(profile=None, tenant_name=None):
    '''
    Return list of active servers
    CLI Example:
    .. code-block:: bash
        salt '*' nova.server_list
    '''
    conn = _authng(profile, tenant_name)
    return conn.server_list()


def server_get(name, tenant_name=None, profile=None):
    '''
    Return information about a server
    '''
    items = server_list(profile, tenant_name)
    instance_id = None
    for key, value in items.iteritems():
        if key == name:
            instance_id = value['id']
    return instance_id


def get_connection_args(profile=None):
    '''
    Set up profile credentials
    '''
    if profile:
        credentials = __salt__['config.option'](profile)
        user = credentials['keystone.user']
        password = credentials['keystone.password']
        tenant = credentials['keystone.tenant']
        auth_url = credentials['keystone.auth_url']

    kwargs = {
        'username': user,
        'password': password,
        'tenant': tenant,
        'auth_url': auth_url
    }
    return kwargs


def quota_list(tenant_name, profile=None):
    '''
    list quotas of a tenant
    '''
    connection_args = get_connection_args(profile)
    tenant = __salt__['keystone.tenant_get'](name=tenant_name, profile=profile, **connection_args)
    tenant_id = tenant[tenant_name]['id']
    conn = _authng(profile)
    nt_ks = conn.compute_conn
    item = nt_ks.quotas.get(tenant_id).__dict__
    return item


def quota_get(name, tenant_name, profile=None, quota_value=None):
    '''
    get specific quota value of a tenant
    '''
    item = quota_list(tenant_name, profile)
    quota_value = item[name]
    return quota_value


def quota_update(tenant_name, profile=None, **quota_argument):
    '''
    update quota of specified tenant
    '''
    connection_args = get_connection_args(profile)
    tenant = __salt__['keystone.tenant_get'](name=tenant_name, profile=profile, **connection_args)
    tenant_id = tenant[tenant_name]['id']
    conn = _authng(profile)
    nt_ks = conn.compute_conn
    item = nt_ks.quotas.update(tenant_id, **quota_argument)
    return item


def server_list(profile=None, tenant_name=None):
    '''
    Return list of active servers
    CLI Example:
    .. code-block:: bash
        salt '*' nova.server_list
    '''
    conn = _authng(profile, tenant_name)
    return conn.server_list()


def secgroup_list(profile=None, tenant_name=None):
    '''
    Return a list of available security groups (nova items-list)
    CLI Example:
    .. code-block:: bash
        salt '*' nova.secgroup_list
    '''
    conn = _authng(profile, tenant_name)
    return conn.secgroup_list()


def boot(name, flavor_id=0, image_id=0, profile=None, tenant_name=None, timeout=300, **kwargs):
    '''
    Boot (create) a new instance
    name
        Name of the new instance (must be first)
    flavor_id
        Unique integer ID for the flavor
    image_id
        Unique integer ID for the image
    timeout
        How long to wait, after creating the instance, for the provider to
        return information about it (default 300 seconds).
        .. versionadded:: 2014.1.0
    CLI Example:
    .. code-block:: bash
        salt '*' nova.boot myinstance flavor_id=4596 image_id=2
    The flavor_id and image_id are obtained from nova.flavor_list and
    nova.image_list
    .. code-block:: bash
        salt '*' nova.flavor_list
        salt '*' nova.image_list
    '''
    #kwargs = {'nics': nics}
    conn = _authng(profile, tenant_name)
    return conn.boot(name, flavor_id, image_id, timeout, **kwargs)


def network_show(name, profile=None):
    conn = _authng(profile)
    return conn.network_show(name)


def availability_zone_list(profile=None):
    '''
    list existing availability zones
    '''
    connection_args = get_connection_args(profile)
    conn = _authng(profile)
    nt_ks = conn.compute_conn
    ret = nt_ks.aggregates.list()
    return ret


def availability_zone_get(name, profile=None):
    '''
    list existing availability zones
    '''
    connection_args = get_connection_args(profile)
    conn = _authng(profile)
    nt_ks = conn.compute_conn
    zone_exists=False
    items = availability_zone_list(profile)
    for p in items:
        item = nt_ks.aggregates.get(p).__getattr__('name')
        if item == name:
            zone_exists = True
    return zone_exists


def availability_zone_create(name, availability_zone, profile=None):
    '''
    create availability zone
    '''
    connection_args = get_connection_args(profile)
    conn = _authng(profile)
    nt_ks = conn.compute_conn
    item = nt_ks.aggregates.create(name, availability_zone)
    ret = {
        'Id': item.__getattr__('id'),
        'Aggregate Name': item.__getattr__('name'),
        'Availability Zone': item.__getattr__('availability_zone'),
    }
    return ret

def aggregate_list(profile=None):
    '''
    list existing aggregates
    '''
    connection_args = get_connection_args(profile)
    conn = _authng(profile)
    nt_ks = conn.compute_conn
    ret = nt_ks.aggregates.list()
    return ret


def aggregate_get(name, profile=None):
    '''
    list existing aggregates
    '''
    connection_args = get_connection_args(profile)
    conn = _authng(profile)
    nt_ks = conn.compute_conn
    aggregate_exists=False
    items = aggregate_list(profile)
    for p in items:
        item = nt_ks.aggregates.get(p).__getattr__('name')
        if item == name:
            aggregate_exists = True
    return aggregate_exists


def aggregate_create(name, aggregate, profile=None):
    '''
    create aggregate
    '''
    connection_args = get_connection_args(profile)
    conn = _authng(profile)
    nt_ks = conn.compute_conn
    item = nt_ks.aggregates.create(name, aggregate)
    ret = {
        'Id': item.__getattr__('id'),
        'Aggregate Name': item.__getattr__('name'),
    }
    return ret

#
# Moved from salt.utils.openstack.nova until this works in upstream
#

'''
Nova class
'''

# Import Python libs
import inspect
import time

from distutils.version import LooseVersion as _LooseVersion

# Import third party libs
import salt.ext.six as six
HAS_NOVA = False
# pylint: disable=import-error
try:
    import novaclient
    from novaclient import client
    from novaclient.shell import OpenStackComputeShell
    import novaclient.utils
    import novaclient.exceptions
    import novaclient.extension
    import novaclient.base
    HAS_NOVA = True
except ImportError:
    pass

OCATA = True
try:
    import novaclient.auth_plugin
    OCATA = False
except ImportError:
    pass

HAS_KEYSTONEAUTH = False
try:
    import keystoneauth1.loading
    import keystoneauth1.session
    HAS_KEYSTONEAUTH = True
except ImportError:
    pass
# pylint: enable=import-error

# Import salt libs
import salt.utils
from salt.exceptions import SaltCloudSystemExit

# Version added to novaclient.client.Client function
NOVACLIENT_MINVER = '2.6.1'

# dict for block_device_mapping_v2
CLIENT_BDM2_KEYS = {
    'id': 'uuid',
    'source': 'source_type',
    'dest': 'destination_type',
    'bus': 'disk_bus',
    'device': 'device_name',
    'size': 'volume_size',
    'format': 'guest_format',
    'bootindex': 'boot_index',
    'type': 'device_type',
    'shutdown': 'delete_on_termination',
}


def check_nova():
    if HAS_NOVA:
        novaclient_ver = _LooseVersion(novaclient.__version__)
        min_ver = _LooseVersion(NOVACLIENT_MINVER)
        if novaclient_ver >= min_ver:
            return HAS_NOVA
        log.debug('Newer novaclient version required.  Minimum: {0}'.format(NOVACLIENT_MINVER))
    return False


# kwargs has to be an object instead of a dictionary for the __post_parse_arg__
class KwargsStruct(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)


def _parse_block_device_mapping_v2(block_device=None, boot_volume=None, snapshot=None, ephemeral=None, swap=None):
    bdm = []
    if block_device is None:
        block_device = []
    if ephemeral is None:
        ephemeral = []

    if boot_volume is not None:
        bdm_dict = {'uuid': boot_volume, 'source_type': 'volume',
                    'destination_type': 'volume', 'boot_index': 0,
                    'delete_on_termination': False}
        bdm.append(bdm_dict)

    if snapshot is not None:
        bdm_dict = {'uuid': snapshot, 'source_type': 'snapshot',
                    'destination_type': 'volume', 'boot_index': 0,
                    'delete_on_termination': False}
        bdm.append(bdm_dict)

    for device_spec in block_device:
        bdm_dict = {}

        for key, value in six.iteritems(device_spec):
            bdm_dict[CLIENT_BDM2_KEYS[key]] = value

        # Convert the delete_on_termination to a boolean or set it to true by
        # default for local block devices when not specified.
        if 'delete_on_termination' in bdm_dict:
            action = bdm_dict['delete_on_termination']
            bdm_dict['delete_on_termination'] = (action == 'remove')
        elif bdm_dict.get('destination_type') == 'local':
            bdm_dict['delete_on_termination'] = True

        bdm.append(bdm_dict)

    for ephemeral_spec in ephemeral:
        bdm_dict = {'source_type': 'blank', 'destination_type': 'local',
                    'boot_index': -1, 'delete_on_termination': True}
        if 'size' in ephemeral_spec:
            bdm_dict['volume_size'] = ephemeral_spec['size']
        if 'format' in ephemeral_spec:
            bdm_dict['guest_format'] = ephemeral_spec['format']

        bdm.append(bdm_dict)

    if swap is not None:
        bdm_dict = {'source_type': 'blank', 'destination_type': 'local',
                    'boot_index': -1, 'delete_on_termination': True,
                    'guest_format': 'swap', 'volume_size': swap}
        bdm.append(bdm_dict)

    return bdm


class NovaServer(object):
    def __init__(self, name, server, password=None):
        '''
        Make output look like libcloud output for consistency
        '''
        self.name = name
        self.id = server['id']
        self.image = server.get('image', {}).get('id', 'Boot From Volume')
        self.size = server['flavor']['id']
        self.state = server['state']
        self._uuid = None
        self.extra = {
            'metadata': server['metadata'],
            'access_ip': server['accessIPv4']
        }

        self.addresses = server.get('addresses', {})
        self.public_ips, self.private_ips = [], []
        for network in self.addresses.values():
            for addr in network:
                if salt.utils.cloud.is_public_ip(addr['addr']):
                    self.public_ips.append(addr['addr'])
                else:
                    self.private_ips.append(addr['addr'])

        if password:
            self.extra['password'] = password

    def __str__(self):
        return self.__dict__


def get_entry(dict_, key, value, raise_error=True):
    for entry in dict_:
        if entry[key] == value:
            return entry
    if raise_error is True:
        raise SaltCloudSystemExit('Unable to find {0} in {1}.'.format(key, dict_))
    return {}


def get_entry_multi(dict_, pairs, raise_error=True):
    for entry in dict_:
        if all([entry[key] == value for key, value in pairs]):
            return entry
    if raise_error is True:
        raise SaltCloudSystemExit('Unable to find {0} in {1}.'.format(pairs, dict_))
    return {}


def sanatize_novaclient(kwargs):
    variables = (
        'username', 'api_key', 'project_id', 'auth_url', 'insecure',
        'timeout', 'proxy_tenant_id', 'proxy_token', 'region_name',
        'endpoint_type', 'extensions', 'service_type', 'service_name',
        'volume_service_name', 'timings', 'bypass_url', 'os_cache',
        'no_cache', 'http_log_debug', 'auth_system', 'auth_plugin',
        'auth_token', 'cacert', 'tenant_id'
    )
    ret = {}
    for var in kwargs:
        if var in variables:
            ret[var] = kwargs[var]

    return ret


def _format_v2_endpoints(endpoints_v2, services):
    catalog = []
    for endpoint_v2 in endpoints_v2:
        endpoints = []
        endpoint = endpoint_v2.copy()
        if 'internalurl' in endpoint:
            internalurl = endpoint.pop('internalurl')
            endpoint['internalURL'] = internalurl

        if 'adminurl' in endpoint:
            adminurl = endpoint.pop('adminurl')
            endpoint['adminURL'] = adminurl

        if 'publicurl' in endpoint:
            publicurl = endpoint.pop('publicurl')
            endpoint['publicURL'] = publicurl
 
        etype = endpoint.pop('type', '')
        ename = endpoint.pop('name', '')
        if endpoint.get('service_id', None) and not etype and not ename:
            service = [s for s in services if s.get('id', '') == endpoint.get('service_id')]
            etype = service[0].get('type', '')
            ename = service[0].get('name', '')

        entry = {
            'type': etype,
            'name': ename,
            'id': endpoint.pop('id'),
            'region': endpoint.get('region'),
            'endpoints': [endpoint]
        }
        catalog.append(entry)
 
    return catalog


# Function alias to not shadow built-ins
class SaltNova(object):
    '''
    Class for all novaclient functions
    '''
    extensions = []

    def __init__(
        self,
        username,
        project_id,
        auth_url,
        region_name=None,
        password=None,
        os_auth_plugin=None,
        use_keystoneauth=False,
        verify=True,
        profile=None,
        **kwargs
    ):
        '''
        Set up nova credentials
        '''

        self._keystoneng_init(profile=profile, **kwargs)

    def _keystoneng_init(self, profile, **kwargs):
        kstone = __salt__['keystoneng.auth'](profile, **kwargs)
        self.session = kstone.session
        self.version = str(kwargs.get('version', 2))
        self.compute_conn = client.Client(version=self.version, session=self.session)
        self.volume_conn = client.Client(version=self.version, session=self.session)

    def expand_extensions(self):
        for connection in (self.compute_conn, self.volume_conn):
            if connection is None:
                continue
            for extension in self.extensions:
                for attr in extension.module.__dict__:
                    if not inspect.isclass(getattr(extension.module, attr)):
                        continue
                    for key, value in six.iteritems(connection.__dict__):
                        if not isinstance(value, novaclient.base.Manager):
                            continue
                        if value.__class__.__name__ == attr:
                            setattr(connection, key, extension.manager_class(connection))

    def get_catalog(self):
        '''
        Return service catalog
        '''
        return self.catalog

    def server_show_libcloud(self, uuid):
        '''
        Make output look like libcloud output for consistency
        '''
        server_info = self.server_show(uuid)
        server = next(six.itervalues(server_info))
        server_name = next(six.iterkeys(server_info))
        if not hasattr(self, 'password'):
            self.password = None
        ret = NovaServer(server_name, server, self.password)

        return ret

    def boot(self, name, flavor_id=0, image_id=0, timeout=300, **kwargs):
        '''
        Boot a cloud server.
        '''
        nt_ks = self.compute_conn
        kwargs['name'] = name
        kwargs['flavor'] = flavor_id
        kwargs['image'] = image_id or None
        ephemeral = kwargs.pop('ephemeral', [])
        block_device = kwargs.pop('block_device', [])
        boot_volume = kwargs.pop('boot_volume', None)
        snapshot = kwargs.pop('snapshot', None)
        swap = kwargs.pop('swap', None)
        kwargs['block_device_mapping_v2'] = _parse_block_device_mapping_v2(
            block_device=block_device, boot_volume=boot_volume, snapshot=snapshot,
            ephemeral=ephemeral, swap=swap
        )
        response = nt_ks.servers.create(**kwargs)
        self.uuid = response.id
        self.password = getattr(response, 'adminPass', None)

        start = time.time()
        trycount = 0
        while True:
            trycount += 1
            try:
                return self.server_show_libcloud(self.uuid)
            except Exception as exc:
                log.debug(
                    'Server information not yet available: {0}'.format(exc)
                )
                time.sleep(1)
                if time.time() - start > timeout:
                    log.error('Timed out after {0} seconds '
                              'while waiting for data'.format(timeout))
                    return False

                log.debug(
                    'Retrying server_show() (try {0})'.format(trycount)
                )

    def show_instance(self, name):
        '''
        Find a server by its name (libcloud)
        '''
        return self.server_by_name(name)

    def root_password(self, server_id, password):
        '''
        Change server(uuid's) root password
        '''
        nt_ks = self.compute_conn
        nt_ks.servers.change_password(server_id, password)

    def server_by_name(self, name):
        '''
        Find a server by its name
        '''
        return self.server_show_libcloud(
            self.server_list().get(name, {}).get('id', '')
        )

    def _volume_get(self, volume_id):
        '''
        Organize information about a volume from the volume_id
        '''
        if self.volume_conn is None:
            raise SaltCloudSystemExit('No cinder endpoint available')
        nt_ks = self.volume_conn
        volume = nt_ks.volumes.get(volume_id)
        response = {'name': volume.display_name,
                    'size': volume.size,
                    'id': volume.id,
                    'description': volume.display_description,
                    'attachments': volume.attachments,
                    'status': volume.status
                    }
        return response

    def volume_list(self, search_opts=None):
        '''
        List all block volumes
        '''
        if self.volume_conn is None:
            raise SaltCloudSystemExit('No cinder endpoint available')
        nt_ks = self.volume_conn
        volumes = nt_ks.volumes.list(search_opts=search_opts)
        response = {}
        for volume in volumes:
            response[volume.display_name] = {
                'name': volume.display_name,
                'size': volume.size,
                'id': volume.id,
                'description': volume.display_description,
                'attachments': volume.attachments,
                'status': volume.status
            }
        return response

    def volume_show(self, name):
        '''
        Show one volume
        '''
        if self.volume_conn is None:
            raise SaltCloudSystemExit('No cinder endpoint available')
        nt_ks = self.volume_conn
        volumes = self.volume_list(
            search_opts={'display_name': name},
        )
        volume = volumes[name]
#        except Exception as esc:
#            # volume doesn't exist
#            log.error(esc.strerror)
#            return {'name': name, 'status': 'deleted'}

        return volume

    def volume_create(self, name, size=100, snapshot=None, voltype=None,
                      availability_zone=None):
        '''
        Create a block device
        '''
        if self.volume_conn is None:
            raise SaltCloudSystemExit('No cinder endpoint available')
        nt_ks = self.volume_conn
        response = nt_ks.volumes.create(
            size=size,
            display_name=name,
            volume_type=voltype,
            snapshot_id=snapshot,
            availability_zone=availability_zone
        )

        return self._volume_get(response.id)

    def volume_delete(self, name):
        '''
        Delete a block device
        '''
        if self.volume_conn is None:
            raise SaltCloudSystemExit('No cinder endpoint available')
        nt_ks = self.volume_conn
        try:
            volume = self.volume_show(name)
        except KeyError as exc:
            raise SaltCloudSystemExit('Unable to find {0} volume: {1}'.format(name, exc))
        if volume['status'] == 'deleted':
            return volume
        response = nt_ks.volumes.delete(volume['id'])
        return volume

    def volume_detach(self,
                      name,
                      timeout=300):
        '''
        Detach a block device
        '''
        try:
            volume = self.volume_show(name)
        except KeyError as exc:
            raise SaltCloudSystemExit('Unable to find {0} volume: {1}'.format(name, exc))
        if not volume['attachments']:
            return True
        response = self.compute_conn.volumes.delete_server_volume(
            volume['attachments'][0]['server_id'],
            volume['attachments'][0]['id']
        )
        trycount = 0
        start = time.time()
        while True:
            trycount += 1
            try:
                response = self._volume_get(volume['id'])
                if response['status'] == 'available':
                    return response
            except Exception as exc:
                log.debug('Volume is detaching: {0}'.format(name))
                time.sleep(1)
                if time.time() - start > timeout:
                    log.error('Timed out after {0} seconds '
                              'while waiting for data'.format(timeout))
                    return False

                log.debug(
                    'Retrying volume_show() (try {0})'.format(trycount)
                )

    def volume_attach(self,
                      name,
                      server_name,
                      device='/dev/xvdb',
                      timeout=300):
        '''
        Attach a block device
        '''
        try:
            volume = self.volume_show(name)
        except KeyError as exc:
            raise SaltCloudSystemExit('Unable to find {0} volume: {1}'.format(name, exc))
        server = self.server_by_name(server_name)
        response = self.compute_conn.volumes.create_server_volume(
            server.id,
            volume['id'],
            device=device
        )
        trycount = 0
        start = time.time()
        while True:
            trycount += 1
            try:
                response = self._volume_get(volume['id'])
                if response['status'] == 'in-use':
                    return response
            except Exception as exc:
                log.debug('Volume is attaching: {0}'.format(name))
                time.sleep(1)
                if time.time() - start > timeout:
                    log.error('Timed out after {0} seconds '
                              'while waiting for data'.format(timeout))
                    return False

                log.debug(
                    'Retrying volume_show() (try {0})'.format(trycount)
                )

    def suspend(self, instance_id):
        '''
        Suspend a server
        '''
        nt_ks = self.compute_conn
        response = nt_ks.servers.suspend(instance_id)
        return True

    def resume(self, instance_id):
        '''
        Resume a server
        '''
        nt_ks = self.compute_conn
        response = nt_ks.servers.resume(instance_id)
        return True

    def lock(self, instance_id):
        '''
        Lock an instance
        '''
        nt_ks = self.compute_conn
        response = nt_ks.servers.lock(instance_id)
        return True

    def delete(self, instance_id):
        '''
        Delete a server
        '''
        nt_ks = self.compute_conn
        response = nt_ks.servers.delete(instance_id)
        return True

    def flavor_list(self):
        '''
        Return a list of available flavors (nova flavor-list)
        '''
        nt_ks = self.compute_conn
        ret = {}
        for flavor in nt_ks.flavors.list():
            links = {}
            for link in flavor.links:
                links[link['rel']] = link['href']
            ret[flavor.name] = {
                'disk': flavor.disk,
                'id': flavor.id,
                'name': flavor.name,
                'ram': flavor.ram,
                'swap': flavor.swap,
                'vcpus': flavor.vcpus,
                'links': links,
            }
            if hasattr(flavor, 'rxtx_factor'):
                ret[flavor.name]['rxtx_factor'] = flavor.rxtx_factor
        return ret

    list_sizes = flavor_list

    def flavor_create(self,
                      name,             # pylint: disable=C0103
                      flavor_id=0,      # pylint: disable=C0103
                      ram=0,
                      disk=0,
                      vcpus=1):
        '''
        Create a flavor
        '''
        nt_ks = self.compute_conn
        nt_ks.flavors.create(
            name=name, flavorid=flavor_id, ram=ram, disk=disk, vcpus=vcpus
        )
        return {'name': name,
                'id': flavor_id,
                'ram': ram,
                'disk': disk,
                'vcpus': vcpus}

    def flavor_delete(self, flavor_id):  # pylint: disable=C0103
        '''
        Delete a flavor
        '''
        nt_ks = self.compute_conn
        nt_ks.flavors.delete(flavor_id)
        return 'Flavor deleted: {0}'.format(flavor_id)

    def keypair_list(self):
        '''
        List keypairs
        '''
        nt_ks = self.compute_conn
        ret = {}
        for keypair in nt_ks.keypairs.list():
            ret[keypair.name] = {
                'name': keypair.name,
                'fingerprint': keypair.fingerprint,
                'public_key': keypair.public_key,
            }
        return ret

    def keypair_add(self, name, pubfile=None, pubkey=None):
        '''
        Add a keypair
        '''
        nt_ks = self.compute_conn
        if pubfile:
            with salt.utils.fopen(pubfile, 'r') as fp_:
                pubkey = fp_.read()
        if not pubkey:
            return False
        nt_ks.keypairs.create(name, public_key=pubkey)
        ret = {'name': name, 'pubkey': pubkey}
        return ret

    def keypair_delete(self, name):
        '''
        Delete a keypair
        '''
        nt_ks = self.compute_conn
        nt_ks.keypairs.delete(name)
        return 'Keypair deleted: {0}'.format(name)

    def image_show(self, image_id):
        '''
        Show image details and metadata
        '''
        nt_ks = self.compute_conn
        image = nt_ks.images.get(image_id)
        links = {}
        for link in image.links:
            links[link['rel']] = link['href']
        ret = {
            'name': image.name,
            'id': image.id,
            'status': image.status,
            'progress': image.progress,
            'created': image.created,
            'updated': image.updated,
            'metadata': image.metadata,
            'links': links,
        }
        if hasattr(image, 'minDisk'):
            ret['minDisk'] = image.minDisk
        if hasattr(image, 'minRam'):
            ret['minRam'] = image.minRam

        return ret

    def image_list(self, name=None):
        '''
        List server images
        '''
        nt_ks = self.compute_conn
        ret = {}
        for image in nt_ks.images.list():
            links = {}
            for link in image.links:
                links[link['rel']] = link['href']
            ret[image.name] = {
                'name': image.name,
                'id': image.id,
                'status': image.status,
                'progress': image.progress,
                'created': image.created,
                'updated': image.updated,
                'metadata': image.metadata,
                'links': links,
            }
            if hasattr(image, 'minDisk'):
                ret[image.name]['minDisk'] = image.minDisk
            if hasattr(image, 'minRam'):
                ret[image.name]['minRam'] = image.minRam
        if name:
            return {name: ret[name]}
        return ret

    list_images = image_list

    def image_meta_set(self,
                       image_id=None,
                       name=None,
                       **kwargs):  # pylint: disable=C0103
        '''
        Set image metadata
        '''
        nt_ks = self.compute_conn
        if name:
            for image in nt_ks.images.list():
                if image.name == name:
                    image_id = image.id  # pylint: disable=C0103
        if not image_id:
            return {'Error': 'A valid image name or id was not specified'}
        nt_ks.images.set_meta(image_id, kwargs)
        return {image_id: kwargs}

    def image_meta_delete(self,
                          image_id=None,     # pylint: disable=C0103
                          name=None,
                          keys=None):
        '''
        Delete image metadata
        '''
        nt_ks = self.compute_conn
        if name:
            for image in nt_ks.images.list():
                if image.name == name:
                    image_id = image.id  # pylint: disable=C0103
        pairs = keys.split(',')
        if not image_id:
            return {'Error': 'A valid image name or id was not specified'}
        nt_ks.images.delete_meta(image_id, pairs)
        return {image_id: 'Deleted: {0}'.format(pairs)}

    def server_list(self):
        '''
        List servers
        '''
        nt_ks = self.compute_conn
        ret = {}
        for item in nt_ks.servers.list():
            try:
                ret[item.name] = {
                    'id': item.id,
                    'name': item.name,
                    'state': item.status,
                    'accessIPv4': item.accessIPv4,
                    'accessIPv6': item.accessIPv6,
                    'flavor': {'id': item.flavor['id'],
                               'links': item.flavor['links']},
                    'image': {'id': item.image['id'] if item.image else 'Boot From Volume',
                              'links': item.image['links'] if item.image else ''},
                    }
            except TypeError:
                pass
        return ret

    def server_list_min(self):
        '''
        List minimal information about servers
        '''
        nt_ks = self.compute_conn
        ret = {}
        for item in nt_ks.servers.list(detailed=False):
            try:
                ret[item.name] = {
                    'id': item.id,
                    'status': 'Running'
                }
            except TypeError:
                pass
        return ret

    def server_list_detailed(self):
        '''
        Detailed list of servers
        '''
        nt_ks = self.compute_conn
        ret = {}
        for item in nt_ks.servers.list():
            try:
                ret[item.name] = {
                    'OS-EXT-SRV-ATTR': {},
                    'OS-EXT-STS': {},
                    'accessIPv4': item.accessIPv4,
                    'accessIPv6': item.accessIPv6,
                    'addresses': item.addresses,
                    'created': item.created,
                    'flavor': {'id': item.flavor['id'],
                               'links': item.flavor['links']},
                    'hostId': item.hostId,
                    'id': item.id,
                    'image': {'id': item.image['id'] if item.image else 'Boot From Volume',
                              'links': item.image['links'] if item.image else ''},
                    'key_name': item.key_name,
                    'links': item.links,
                    'metadata': item.metadata,
                    'name': item.name,
                    'state': item.status,
                    'tenant_id': item.tenant_id,
                    'updated': item.updated,
                    'user_id': item.user_id,
                }
            except TypeError:
                continue

            ret[item.name]['progress'] = getattr(item, 'progress', '0')

            if hasattr(item.__dict__, 'OS-DCF:diskConfig'):
                ret[item.name]['OS-DCF'] = {
                    'diskConfig': item.__dict__['OS-DCF:diskConfig']
                }
            if hasattr(item.__dict__, 'OS-EXT-SRV-ATTR:host'):
                ret[item.name]['OS-EXT-SRV-ATTR']['host'] = \
                    item.__dict__['OS-EXT-SRV-ATTR:host']
            if hasattr(item.__dict__, 'OS-EXT-SRV-ATTR:hypervisor_hostname'):
                ret[item.name]['OS-EXT-SRV-ATTR']['hypervisor_hostname'] = \
                    item.__dict__['OS-EXT-SRV-ATTR:hypervisor_hostname']
            if hasattr(item.__dict__, 'OS-EXT-SRV-ATTR:instance_name'):
                ret[item.name]['OS-EXT-SRV-ATTR']['instance_name'] = \
                    item.__dict__['OS-EXT-SRV-ATTR:instance_name']
            if hasattr(item.__dict__, 'OS-EXT-STS:power_state'):
                ret[item.name]['OS-EXT-STS']['power_state'] = \
                    item.__dict__['OS-EXT-STS:power_state']
            if hasattr(item.__dict__, 'OS-EXT-STS:task_state'):
                ret[item.name]['OS-EXT-STS']['task_state'] = \
                    item.__dict__['OS-EXT-STS:task_state']
            if hasattr(item.__dict__, 'OS-EXT-STS:vm_state'):
                ret[item.name]['OS-EXT-STS']['vm_state'] = \
                    item.__dict__['OS-EXT-STS:vm_state']
            if hasattr(item.__dict__, 'security_groups'):
                ret[item.name]['security_groups'] = \
                    item.__dict__['security_groups']
        return ret

    def server_show(self, server_id):
        '''
        Show details of one server
        '''
        ret = {}
        try:
            servers = self.server_list_detailed()
        except AttributeError:
            raise SaltCloudSystemExit('Corrupt server in server_list_detailed. Remove corrupt servers.')
        for server_name, server in six.iteritems(servers):
            if str(server['id']) == server_id:
                ret[server_name] = server
        return ret

    def secgroup_create(self, name, description):
        '''
        Create a security group
        '''
        nt_ks = self.compute_conn
        nt_ks.security_groups.create(name, description)
        ret = {'name': name, 'description': description}
        return ret

    def secgroup_delete(self, name):
        '''
        Delete a security group
        '''
        nt_ks = self.compute_conn
        for item in nt_ks.security_groups.list():
            if item.name == name:
                nt_ks.security_groups.delete(item.id)
                return {name: 'Deleted security group: {0}'.format(name)}
        return 'Security group not found: {0}'.format(name)

    def secgroup_list(self):
        '''
        List security groups
        '''
        nt_ks = self.compute_conn
        ret = {}
        for item in nt_ks.security_groups.list():
            ret[item.name] = {
                'name': item.name,
                'description': item.description,
                'id': item.id,
                'tenant_id': item.tenant_id,
                'rules': item.rules,
            }
        return ret

    def _item_list(self):
        '''
        List items
        '''
        nt_ks = self.compute_conn
        ret = []
        for item in nt_ks.items.list():
            ret.append(item.__dict__)
        return ret

    def _network_show(self, name, network_lst):
        '''
        Parse the returned network list
        '''
        for net in network_lst:
            if net.label == name:
                return net.__dict__
        return {}

    def network_show(self, name):
        '''
        Show network information
        '''
        nt_ks = self.compute_conn
        net_list = nt_ks.networks.list()
        return self._network_show(name, net_list)

    def network_list(self):
        '''
        List extra private networks
        '''
        nt_ks = self.compute_conn
        return [network.__dict__ for network in nt_ks.networks.list()]

    def _sanatize_network_params(self, kwargs):
        '''
        Sanatize novaclient network parameters
        '''
        params = [
            'label', 'bridge', 'bridge_interface', 'cidr', 'cidr_v6', 'dns1',
            'dns2', 'fixed_cidr', 'gateway', 'gateway_v6', 'multi_host',
            'priority', 'project_id', 'vlan_start', 'vpn_start'
        ]

        for variable in six.iterkeys(kwargs):  # iterate over a copy, we might delete some
            if variable not in params:
                del kwargs[variable]
        return kwargs

    def network_create(self, name, **kwargs):
        '''
        Create extra private network
        '''
        nt_ks = self.compute_conn
        kwargs['label'] = name
        kwargs = self._sanatize_network_params(kwargs)
        net = nt_ks.networks.create(**kwargs)
        return net.__dict__

    def _server_uuid_from_name(self, name):
        '''
        Get server uuid from name
        '''
        return self.server_list().get(name, {}).get('id', '')

    def virtual_interface_list(self, name):
        '''
        Get virtual interfaces on slice
        '''
        nt_ks = self.compute_conn
        nets = nt_ks.virtual_interfaces.list(self._server_uuid_from_name(name))
        return [network.__dict__ for network in nets]

    def virtual_interface_create(self, name, net_name):
        '''
        Add an interfaces to a slice
        '''
        nt_ks = self.compute_conn
        serverid = self._server_uuid_from_name(name)
        networkid = self.network_show(net_name).get('id', None)
        if networkid is None:
            return {net_name: False}
        nets = nt_ks.virtual_interfaces.create(networkid, serverid)
        return nets

    def floating_ip_pool_list(self):
        '''
        List all floating IP pools
        .. versionadded:: 2016.3.0
        '''
        nt_ks = self.compute_conn
        pools = nt_ks.floating_ip_pools.list()
        response = {}
        for pool in pools:
            response[pool.name] = {
                'name': pool.name,
            }
        return response

    def floating_ip_list(self):
        '''
        List floating IPs
        .. versionadded:: 2016.3.0
        '''
        nt_ks = self.compute_conn
        floating_ips = nt_ks.floating_ips.list()
        response = {}
        for floating_ip in floating_ips:
            response[floating_ip.ip] = {
                'ip': floating_ip.ip,
                'fixed_ip': floating_ip.fixed_ip,
                'id': floating_ip.id,
                'instance_id': floating_ip.instance_id,
                'pool': floating_ip.pool
            }
        return response

    def floating_ip_show(self, ip):
        '''
        Show info on specific floating IP
        .. versionadded:: 2016.3.0
        '''
        nt_ks = self.compute_conn
        floating_ips = nt_ks.floating_ips.list()
        for floating_ip in floating_ips:
            if floating_ip.ip == ip:
                return floating_ip
        return {}

    def floating_ip_create(self, pool=None):
        '''
        Allocate a floating IP
        .. versionadded:: 2016.3.0
        '''
        nt_ks = self.compute_conn
        floating_ip = nt_ks.floating_ips.create(pool)
        response = {
            'ip': floating_ip.ip,
            'fixed_ip': floating_ip.fixed_ip,
            'id': floating_ip.id,
            'instance_id': floating_ip.instance_id,
            'pool': floating_ip.pool
        }
        return response

    def floating_ip_delete(self, floating_ip):
        '''
        De-allocate a floating IP
        .. versionadded:: 2016.3.0
        '''
        ip = self.floating_ip_show(floating_ip)
        nt_ks = self.compute_conn
        return nt_ks.floating_ips.delete(ip)

    def floating_ip_associate(self, server_name, floating_ip):
        '''
        Associate floating IP address to server
        .. versionadded:: 2016.3.0
        '''
        nt_ks = self.compute_conn
        server_ = self.server_by_name(server_name)
        server = nt_ks.servers.get(server_.__dict__['id'])
        server.add_floating_ip(floating_ip)
        return self.floating_ip_list()[floating_ip]

    def floating_ip_disassociate(self, server_name, floating_ip):
        '''
        Disassociate a floating IP from server
        .. versionadded:: 2016.3.0
        '''
        nt_ks = self.compute_conn
        server_ = self.server_by_name(server_name)
        server = nt_ks.servers.get(server_.__dict__['id'])
        server.remove_floating_ip(floating_ip)
        return self.floating_ip_list()[floating_ip]

#
# Moved from salt.modules.nova until this works in upstream
#

def _auth(profile=None):
    '''
    Set up nova credentials
    '''
    if profile:
        credentials = __salt__['config.option'](profile)
        user = credentials['keystone.user']
        password = credentials['keystone.password']
        tenant = credentials['keystone.tenant']
        auth_url = credentials['keystone.auth_url']
        region_name = credentials.get('keystone.region_name', None)
        api_key = credentials.get('keystone.api_key', None)
        os_auth_system = credentials.get('keystone.os_auth_system', None)
        use_keystoneauth = credentials.get('keystone.use_keystoneauth', False)
        verify = credentials.get('keystone.verify', False)
    else:
        user = __salt__['config.option']('keystone.user')
        password = __salt__['config.option']('keystone.password')
        tenant = __salt__['config.option']('keystone.tenant')
        auth_url = __salt__['config.option']('keystone.auth_url')
        region_name = __salt__['config.option']('keystone.region_name')
        api_key = __salt__['config.option']('keystone.api_key')
        os_auth_system = __salt__['config.option']('keystone.os_auth_system')
        use_keystoneauth = __salt__['config.option']('keystone.use_keystoneauth', False)
        verify = __salt__['config.option']('keystone.verify', True)

    kwargs = {
        'username': user,
        'password': password,
        'api_key': api_key,
        'project_id': tenant,
        'auth_url': auth_url,
        'region_name': region_name,
        'os_auth_plugin': os_auth_system,
        'use_keystoneauth': use_keystoneauth,
        'verify': verify,
        'profile': profile
    }

    return SaltNova(**kwargs)


#def boot(name, flavor_id=0, image_id=0, profile=None, timeout=300):
#    '''
#    Boot (create) a new instance
#    name
#        Name of the new instance (must be first)
#    flavor_id
#        Unique integer ID for the flavor
#    image_id
#        Unique integer ID for the image
#    timeout
#        How long to wait, after creating the instance, for the provider to
#        return information about it (default 300 seconds).
#        .. versionadded:: 2014.1.0
#    CLI Example:
#    .. code-block:: bash
#        salt '*' nova.boot myinstance flavor_id=4596 image_id=2
#    The flavor_id and image_id are obtained from nova.flavor_list and
#    nova.image_list
#    .. code-block:: bash
#        salt '*' nova.flavor_list
#        salt '*' nova.image_list
#    '''
#    conn = _auth(profile)
#    return conn.boot(name, flavor_id, image_id, timeout)


def volume_list(search_opts=None, profile=None):
    '''
    List storage volumes
    search_opts
        Dictionary of search options
    profile
        Profile to use
    CLI Example:
    .. code-block:: bash
        salt '*' nova.volume_list \
                search_opts='{"display_name": "myblock"}' \
                profile=openstack
    '''
    conn = _auth(profile)
    return conn.volume_list(search_opts=search_opts)


def volume_show(name, profile=None):
    '''
    Create a block storage volume
    name
        Name of the volume
    profile
        Profile to use
    CLI Example:
    .. code-block:: bash
        salt '*' nova.volume_show myblock profile=openstack
    '''
    conn = _auth(profile)
    return conn.volume_show(name)


def volume_create(name, size=100, snapshot=None, voltype=None,
                  profile=None):
    '''
    Create a block storage volume
    name
        Name of the new volume (must be first)
    size
        Volume size
    snapshot
        Block storage snapshot id
    voltype
        Type of storage
    profile
        Profile to build on
    CLI Example:
    .. code-block:: bash
        salt '*' nova.volume_create myblock size=300 profile=openstack
    '''
    conn = _auth(profile)
    return conn.volume_create(
        name,
        size,
        snapshot,
        voltype
    )


def volume_delete(name, profile=None):
    '''
    Destroy the volume
    name
        Name of the volume
    profile
        Profile to build on
    CLI Example:
    .. code-block:: bash
        salt '*' nova.volume_delete myblock profile=openstack
    '''
    conn = _auth(profile)
    return conn.volume_delete(name)


def volume_detach(name,
                  profile=None,
                  timeout=300):
    '''
    Attach a block storage volume
    name
        Name of the new volume to attach
    server_name
        Name of the server to detach from
    profile
        Profile to build on
    CLI Example:
    .. code-block:: bash
        salt '*' nova.volume_detach myblock profile=openstack
    '''
    conn = _auth(profile)
    return conn.volume_detach(
        name,
        timeout
    )


def volume_attach(name,
                  server_name,
                  device='/dev/xvdb',
                  profile=None,
                  timeout=300):
    '''
    Attach a block storage volume
    name
        Name of the new volume to attach
    server_name
        Name of the server to attach to
    device
        Name of the device on the server
    profile
        Profile to build on
    CLI Example:
    .. code-block:: bash
        salt '*' nova.volume_attach myblock slice.example.com profile=openstack
        salt '*' nova.volume_attach myblock server.example.com \
                device='/dev/xvdb' profile=openstack
    '''
    conn = _auth(profile)
    return conn.volume_attach(
        name,
        server_name,
        device,
        timeout
    )


def suspend(instance_id, profile=None):
    '''
    Suspend an instance
    instance_id
        ID of the instance to be suspended
    CLI Example:
    .. code-block:: bash
        salt '*' nova.suspend 1138
    '''
    conn = _auth(profile)
    return conn.suspend(instance_id)


def resume(instance_id, profile=None):
    '''
    Resume an instance
    instance_id
        ID of the instance to be resumed
    CLI Example:
    .. code-block:: bash
        salt '*' nova.resume 1138
    '''
    conn = _auth(profile)
    return conn.resume(instance_id)


def lock(instance_id, profile=None):
    '''
    Lock an instance
    instance_id
        ID of the instance to be locked
    CLI Example:
    .. code-block:: bash
        salt '*' nova.lock 1138
    '''
    conn = _auth(profile)
    return conn.lock(instance_id)


def delete(instance_id, profile=None):
    '''
    Delete an instance
    instance_id
        ID of the instance to be deleted
    CLI Example:
    .. code-block:: bash
        salt '*' nova.delete 1138
    '''
    conn = _auth(profile)
    return conn.delete(instance_id)


def flavor_list(profile=None):
    '''
    Return a list of available flavors (nova flavor-list)
    CLI Example:
    .. code-block:: bash
        salt '*' nova.flavor_list
    '''
    conn = _auth(profile)
    return conn.flavor_list()


def flavor_create(name,      # pylint: disable=C0103
                  flavor_id=0,      # pylint: disable=C0103
                  ram=0,
                  disk=0,
                  vcpus=1,
                  profile=None):
    '''
    Add a flavor to nova (nova flavor-create). The following parameters are
    required:
    name
        Name of the new flavor (must be first)
    flavor_id
        Unique integer ID for the new flavor
    ram
        Memory size in MB
    disk
        Disk size in GB
    vcpus
        Number of vcpus
    CLI Example:
    .. code-block:: bash
        salt '*' nova.flavor_create myflavor flavor_id=6 \
                ram=4096 disk=10 vcpus=1
    '''
    conn = _auth(profile)
    return conn.flavor_create(
        name,
        flavor_id,
        ram,
        disk,
        vcpus
    )


def flavor_delete(flavor_id, profile=None):  # pylint: disable=C0103
    '''
    Delete a flavor from nova by id (nova flavor-delete)
    CLI Example:
    .. code-block:: bash
        salt '*' nova.flavor_delete 7
    '''
    conn = _auth(profile)
    return conn.flavor_delete(flavor_id)


def keypair_list(profile=None):
    '''
    Return a list of available keypairs (nova keypair-list)
    CLI Example:
    .. code-block:: bash
        salt '*' nova.keypair_list
    '''
    conn = _auth(profile)
    return conn.keypair_list()


def keypair_add(name, pubfile=None, pubkey=None, profile=None):
    '''
    Add a keypair to nova (nova keypair-add)
    CLI Examples:
    .. code-block:: bash
        salt '*' nova.keypair_add mykey pubfile='/home/myuser/.ssh/id_rsa.pub'
        salt '*' nova.keypair_add mykey pubkey='ssh-rsa <key> myuser@mybox'
    '''
    conn = _auth(profile)
    return conn.keypair_add(
        name,
        pubfile,
        pubkey
    )


def keypair_delete(name, profile=None):
    '''
    Add a keypair to nova (nova keypair-delete)
    CLI Example:
    .. code-block:: bash
        salt '*' nova.keypair_delete mykey'
    '''
    conn = _auth(profile)
    return conn.keypair_delete(name)


def image_list(name=None, profile=None):
    '''
    Return a list of available images (nova images-list + nova image-show)
    If a name is provided, only that image will be displayed.
    CLI Examples:
    .. code-block:: bash
        salt '*' nova.image_list
        salt '*' nova.image_list myimage
    '''
    conn = _auth(profile)
    return conn.image_list(name)


def image_meta_set(image_id=None,
                   name=None,
                   profile=None,
                   **kwargs):  # pylint: disable=C0103
    '''
    Sets a key=value pair in the metadata for an image (nova image-meta set)
    CLI Examples:
    .. code-block:: bash
        salt '*' nova.image_meta_set 6f52b2ff-0b31-4d84-8fd1-af45b84824f6 \
                cheese=gruyere
        salt '*' nova.image_meta_set name=myimage salad=pasta beans=baked
    '''
    conn = _auth(profile)
    return conn.image_meta_set(
        image_id,
        name,
        **kwargs
    )


def image_meta_delete(image_id=None,     # pylint: disable=C0103
                      name=None,
                      keys=None,
                      profile=None):
    '''
    Delete a key=value pair from the metadata for an image
    (nova image-meta set)
    CLI Examples:
    .. code-block:: bash
        salt '*' nova.image_meta_delete \
                6f52b2ff-0b31-4d84-8fd1-af45b84824f6 keys=cheese
        salt '*' nova.image_meta_delete name=myimage keys=salad,beans
    '''
    conn = _auth(profile)
    return conn.image_meta_delete(
        image_id,
        name,
        keys
    )


def list_(profile=None):
    '''
    To maintain the feel of the nova command line, this function simply calls
    the server_list function.
    CLI Example:
    .. code-block:: bash
        salt '*' nova.list
    '''
    return server_list(profile=profile)


#def server_list(profile=None):
#    '''
#    Return list of active servers
#    CLI Example:
#    .. code-block:: bash
#        salt '*' nova.server_list
#    '''
#    conn = _auth(profile)
#    return conn.server_list()


def show(server_id, profile=None):
    '''
    To maintain the feel of the nova command line, this function simply calls
    the server_show function.
    CLI Example:
    .. code-block:: bash
        salt '*' nova.show
    '''
    return server_show(server_id, profile)


def server_list_detailed(profile=None):
    '''
    Return detailed list of active servers
    CLI Example:
    .. code-block:: bash
        salt '*' nova.server_list_detailed
    '''
    conn = _auth(profile)
    return conn.server_list_detailed()


def server_show(server_id, profile=None):
    '''
    Return detailed information for an active server
    CLI Example:
    .. code-block:: bash
        salt '*' nova.server_show <server_id>
    '''
    conn = _auth(profile)
    return conn.server_show(server_id)


#def secgroup_create(name, description, profile=None):
#    '''
#    Add a secgroup to nova (nova secgroup-create)
#    CLI Example:
#    .. code-block:: bash
#        salt '*' nova.secgroup_create mygroup 'This is my security group'
#    '''
#    conn = _auth(profile)
#    return conn.secgroup_create(name, description)
#
#
#def secgroup_delete(name, profile=None):
#    '''
#    Delete a secgroup to nova (nova secgroup-delete)
#    CLI Example:
#    .. code-block:: bash
#        salt '*' nova.secgroup_delete mygroup
#    '''
#    conn = _auth(profile)
#    return conn.secgroup_delete(name)
#
#
#def secgroup_list(profile=None):
#    '''
#    Return a list of available security groups (nova items-list)
#    CLI Example:
#    .. code-block:: bash
#        salt '*' nova.secgroup_list
#    '''
#    conn = _auth(profile)
#    return conn.secgroup_list()


def server_by_name(name, profile=None):
    '''
    Return information about a server
    name
        Server Name
    CLI Example:
    .. code-block:: bash
        salt '*' nova.server_by_name myserver profile=openstack
    '''
    conn = _auth(profile)
    return conn.server_by_name(name)

