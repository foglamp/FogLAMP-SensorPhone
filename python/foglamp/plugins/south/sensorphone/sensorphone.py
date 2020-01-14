# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

"""HTTP Listener handler for sensor phone application readings"""
import asyncio
import logging
from threading import Thread
from aiohttp import web

from foglamp.common import logger
from foglamp.common.web import middleware
from foglamp.plugins.common import utils
import async_ingest


__author__ = "Mark Riddoch, Ashish Jabble"
__copyright__ = "Copyright (c) 2017 OSIsoft, LLC"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_LOGGER = logger.setup(__name__, level=logging.INFO)
c_callback = None
c_ingest_ref = None
loop = None
t = None

_CONFIG_CATEGORY_NAME = 'SensorApp'
_CONFIG_CATEGORY_DESCRIPTION = 'South Plugin Sensor Phone app - based on SAP IOT Cloud platform'
_DEFAULT_CONFIG = {
    'plugin': {
         'description': 'SensorPhone application on a iPhone',
         'type': 'string',
         'default': 'sensorphone',
         'readonly': 'true'
    },
    'host': {
        'description': 'Address to accept data on',
        'type': 'string',
        'default': '0.0.0.0',
        'order': '1',
        'displayName': 'Host'
    },
    'port': {
        'description': 'Port to listen on',
        'type': 'integer',
        'default': '8080',
        'order': '2',
        'displayName': 'Port'
    }
}


def plugin_info():
    return {
        'name': 'sensorphone',
        'version': '1.7.0',
        'mode': 'async',
        'type': 'south',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(config):
    """Registers HTTP Listener handler to accept sensor readings"""

    _LOGGER.info("Retrieve Sensor Phone Configuration %s", config)

    host = config['host']['value']
    port = config['port']['value']

    return {'host': host, 'port': port, 'plugin': {'value': 'sensorphone'}}


def plugin_start(data):
    global loop, t
    _LOGGER.info("plugin_start called")

    try:
        host = data['host']
        port = data['port']

        loop = asyncio.new_event_loop()
        app = web.Application(middlewares=[middleware.error_middleware], loop=loop)
        app.router.add_route('POST', '/', SensorPhoneIngest.render_post)
        handler = app._make_handler(loop=loop)
        server_coro = loop.create_server(handler, host, port)
        future = asyncio.ensure_future(server_coro, loop=loop)

        data['app'] = app
        data['handler'] = handler
        data['server'] = None

        def f_callback(f):
            data['server'] = f.result()

        future.add_done_callback(f_callback)

        def run():
            global loop
            loop.run_forever()

        t = Thread(target=run)
        t.start()
    except Exception as e:
        _LOGGER.exception(str(e))


def plugin_reconfigure(handle, new_config):
    """ Reconfigures the plugin

    it should be called when the configuration of the plugin is changed during the operation of the South service;
    The new configuration category should be passed.

    Args:
        handle: handle returned by the plugin initialisation call
        new_config: JSON object representing the new configuration category for the category
    Returns:
        new_handle: new handle to be used in the future calls
    Raises:
    """
    global loop
    _LOGGER.info("Old config for Sensor Phone south plugin {} \n new config {}".format(handle, new_config))

    # plugin_shutdown
    plugin_shutdown(handle)

    # plugin_init
    new_handle = plugin_init(new_config)

    # plugin_start
    plugin_start(new_handle)

    return new_handle


def plugin_shutdown(handle):
    _LOGGER.info('Sensor Phone plugin shut down.')
    global loop
    try:
        app = handle['app']
        handler = handle['handler']
        server = handle['server']

        if server:
            server.close()
            asyncio.ensure_future(server.wait_closed(), loop=loop)
            asyncio.ensure_future(app.shutdown(), loop=loop)
            asyncio.ensure_future(handler.shutdown(60.0), loop=loop)
            asyncio.ensure_future(app.cleanup(), loop=loop)
        loop.stop()
    except Exception as e:
        _LOGGER.exception(str(e))
        raise


def plugin_register_ingest(handle, callback, ingest_ref):
    """Required plugin interface component to communicate to South C server

    Args:
        handle: handle returned by the plugin initialisation call
        callback: C opaque object required to passed back to C->ingest method
        ingest_ref: C opaque object required to passed back to C->ingest method
    """
    global c_callback, c_ingest_ref
    c_callback = callback
    c_ingest_ref = ingest_ref


# TODO: Implement FOGL-701 (implement AuditLogger which logs to DB and can be used by all ) for this class


class SensorPhoneIngest(object):
    """Handles incoming sensor readings from Sensor Phone application"""

    @staticmethod
    async def render_post(request):
        """Store sensor readings from SensorPhone to FogLAMP

        Args:
            request:
                The payload decodes to JSON similar to the following:

                .. code-block:: python

                    {
                        "mode" : "sync",
                        "messages" : [
                             {
                                 "audio": 0.0005980864,
                                 "device": "iOS Device",
                                 "altitude": 30.71550178527832,
                                 "latitude": 51.55842144498452,
                                 "longitude": -0.8672407515484514,
                                 "timestamp": 1514597142,
                                 "gyroscopex": -0.005210537929087877,
                                 "gyroscopey": -0.02013654075562954,
                                 "gyroscopez": -0.005803442094475031,
                                 "accelerometerx": 0.0119628909160383,
                                 "accelerometery": -0.7869872764804313,
                                 "accelerometerz": -0.6097259288653731}
                        ]
                    }
        """
        # TODO: Decide upon the correct format of message
        message = {'result': 'success'}
        code = web.HTTPOk.status_code

        try:
            payload = await request.json()

            asset = 'SensorPhone'
            timestamp = utils.local_timestamp()
            messages = payload.get('messages')

            if not isinstance(messages, list):
                    raise ValueError('messages must be a list')

            for readings in messages:
                data = {
                    'asset': asset,
                    'timestamp': timestamp,
                    'readings': readings
                }
                async_ingest.ingest_callback(c_callback, c_ingest_ref, data)
        except (ValueError, TypeError) as e:
            code = web.HTTPBadRequest.status_code
            message = {'error': str(e)}
            _LOGGER.exception(str(e))
        except Exception as e:
            code = web.HTTPInternalServerError.status_code
            message = {'error': str(e)}
            _LOGGER.exception(str(e))

        # expect keys in response:
        # (code = 2xx) result Or busy
        # (code = 4xx, 5xx) error
        message['status'] = code

        return web.json_response(message)
