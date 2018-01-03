# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

"""HTTP Listener handler for sensor phone application readings"""
import sys
from aiohttp import web
import asyncio
from foglamp.common import logger
from foglamp.common.web import middleware
from foglamp.services.south.ingest import Ingest
from datetime import datetime, timezone
import uuid

__author__ = "Mark Riddoch"
__copyright__ = "Copyright (c) 2017 OSIsoft, LLC"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_LOGGER = logger.setup(__name__, level=20)

_CONFIG_CATEGORY_NAME = 'SensorPhon'
_CONFIG_CATEGORY_DESCRIPTION = 'South Plugin Sensor Phone app - based on SAP IOT Cloud platform'
_DEFAULT_CONFIG = {
    'plugin': {
         'description': 'Sensor Phone',
         'type': 'string',
         'default': 'sensor_phone'
    },
    'port': {
        'description': 'Port to listen on',
        'type': 'integer',
        'default': '8080',
    },
    'host': {
        'description': 'Address to accept data on',
        'type': 'string',
        'default': '0.0.0.0',
    }
}


def plugin_info():
    return {'name': 'sensor_phone', 'version': '1.0', 'mode': 'async', 'type': 'device',
            'interface': '1.0', 'config': _DEFAULT_CONFIG}


def plugin_init(config):
    """Registers HTTP Listener handler to accept sensor readings"""

    _LOGGER.info("Retrieve Sensor Phone Configuration %s", config)

    host = config['host']['value']
    port = config['port']['value']

    return {'host': host, 'port': port}


def plugin_start(data):
    try:
        host = data['host']
        port = data['port']

        loop = asyncio.get_event_loop()

        app = web.Application(middlewares=[middleware.error_middleware])
        app.router.add_route('POST', '/', SensorPhoneIngest.render_post)
        handler = app.make_handler()
        coro = loop.create_server(handler, host, port)
        server = asyncio.ensure_future(coro)

        data['app'] = app
        data['handler'] = handler
        data['server'] = server
    except Exception as e:
        _LOGGER.exception(str(e))
        sys.exit(1)


def plugin_reconfigure(config):
    pass


def plugin_shutdown(data):
    try:
        app = data['app']
        handler = data['handler']
        server = data['server']

        server.close()
        asyncio.ensure_future(server.wait_closed())
        asyncio.ensure_future(app.shutdown())
        asyncio.ensure_future(handler.shutdown(60.0))
        asyncio.ensure_future(app.cleanup())
    except Exception as e:
        _LOGGER.exception(str(e))
        raise


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

        increment_discarded_counter = False

        # TODO: Decide upon the correct format of message
        message = {'result': 'success'}
        code = web.HTTPOk.status_code

        try:
            if not Ingest.is_available():
                increment_discarded_counter = True
                message = {'busy': True}
            else:
                payload = await request.json()

                asset = 'SensorPhone'
                timestamp = str(datetime.now(tz=timezone.utc))
                messages = payload.get('messages')

                if not isinstance(messages, list):
                        raise ValueError('messages must be a list')

                for readings in messages:
                    key = str(uuid.uuid4())
                    await Ingest.add_readings(asset=asset, timestamp=timestamp, key=key, readings=readings)

        except (ValueError, TypeError) as e:
            increment_discarded_counter = True
            code = web.HTTPBadRequest.status_code
            message = {'error': str(e)}
            _LOGGER.exception(str(e))
        except Exception as e:
            increment_discarded_counter = True
            code = web.HTTPInternalServerError.status_code
            message = {'error': str(e)}
            _LOGGER.exception(str(e))

        if increment_discarded_counter:
            Ingest.increment_discarded_readings()

        # expect keys in response:
        # (code = 2xx) result Or busy
        # (code = 4xx, 5xx) error
        message['status'] = code

        return web.json_response(message)
