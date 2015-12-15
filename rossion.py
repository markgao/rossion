#!/usr/bin/env python
#
# Copyright 2013 Mark Gao
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Rossion is a fast and simple session module for tornado app.
"""

import os
import datetime
import base64
import cPickle as pickle

from collections import MutableMapping

__author__ = "Mark Gao"
__version__ = "0.1.0"


SESSION_ID_ALIAS = "SSID"

class SessionManager(MutableMapping):
    """The manager class for the session object.
    """
    def __init__(self, session_id, settings):
        self._session_id = session_id if session_id else \
                               self._generate_session_id(32)
        self.driver = mount_driver(self._session_id, settings)

    @property
    def session_id(self):
        return self._session_id

    def __repr__(self):
        return "<session id: %s>" % (self.session_id,)

    def __str__(self):
        return str(self.session_id)

    def __len__(self):
        return len(self.driver.data.keys())

    def __getitem__(self, key):
        if key in self.driver.data:
            return self.driver.data[key]
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError

    def __setitem__(self, key, value):
        self.driver.set(key, value)

    def __delitem__(self, key):
        self.driver.delete(key)

    def __iter__(self):
        return iter(self.driver.data)

    def keys(self):
        return self.driver.data.keys()

    def values(self):
        return self.driver.data.values()

    def has_key(self, key):
        return key in self.driver.data

    def _generate_session_id(self, n=32):
        return os.urandom(n).encode('hex') # 256 bits of entropy


class Driver(object):
    """Session driver base.
    """
    def __init__(self, session_id, storage, data=None, **kwargs):
        if data is None:
            data = {}
        self._session_id = session_id
        self._storage = storage
        self._data = data
        self._dirty = False

    @staticmethod
    def load(session_id, storage):
        """Load the stored session from storage backend or return None if the
        session was not found.
        """
        pass

    @property
    def data(self):
        return self._data

    def get(self, name, default=None):
        return self._data.get(name, default)

    def set(self, name, data):
        self._data[name] = data
        self._dirty = True
        self._save(self._data)

    def delete(self, name):
        del self._data[name]
        self._dirty = True
        self._save(self._data)

    def remove(self):
        """Remove all data representing the session from backend storage.
        """
        pass

    def _save(self, data):
        """Save all data.
        """
        pass

    @staticmethod
    def serialize(data):
        return base64.encodestring(pickle.dumps(data))

    @staticmethod
    def deserialize(serializedstring):
        return pickle.loads(base64.decodestring(serializedstring))


class MemoryDriver(Driver):
    """Memory stored sessions.
    """

    @staticmethod
    def load(session_id, dictionary, settings):
        value = dictionary.get(session_id)
        if value:
            settings = MemoryDriver.deserialize(value)
        return MemoryDriver(session_id, dictionary, **settings)

    def remove(self):
        if self._session_id in self._storage:
            del self._storage[self._session_id]

    def _save(self, data):
        if not self._dirty:
            return

        value = MemoryDriver.serialize({'data': data})

        self._storage[self._session_id] = value

        self._dirty = False


class MemcachedDriver(Driver):
    """Class responsible for Memcached stored sessions. It uses the pylibmc
    library because it's fast. It communicates with the memcached server
    through the binary protocol and uses async I/O (no_block set to 1) to
    speed things up even more.

    Session ID is used as a key. The value consists of colon separated values
    of serializes session object, expiry timestamp, IP address and User-Agent.

    Values are stored with timeout set to the difference between saving time
    and expiry time in seconds. Therefore, no old sessions will be held in
    Memcached memory.
    """

    @staticmethod
    def load(session_id, connection, settings):
        """Load the session from storage.
        """
        try:
            value = connection.get(session_id)
            if value:
                settings = MemcachedDriver.deserialize(value)
            return MemcachedDriver(session_id, connection, **settings)
        except:
            return None

    def remove(self):
        self._storage.delete(self._session_id)

    def _save(self, data):
        """Writes the session data to Memcached. Session ID is used as key,
        values is constructed as serialized string.
        """
        if not self._dirty:
            return

        value = MemcachedDriver.serialize({'data': data})

        self._storage.set(self._session_id, value,
                          time=datetime.timedelta.max.seconds*1)
        self._dirty = False


def mount_driver(session_id, settings):
    engine = settings.get('engine')
    storage = settings.get('storage')
    if engine is "memcached":
        loader = MemcachedDriver.load
    else:
        loader = MemoryDriver.load
    return loader(session_id, storage, settings.get('options', {}))

class SessionMixin(object):
    """Session handler.

    .. testcode::

        class MyHandler(durotar.web.RequestHandler, SessionMixin):
            def get(self):
                key, value = ("key", "value")
                self.session[key] = value
                self.finish(self.session[key])
    """
    @property
    def session(self):
        """Returns a SessionManager instance.
        """
        return mount_mixin(self, "__session", SessionManager)


def mount_mixin(handler, property_name, cls):
    manager = getattr(handler, property_name, None)
    if manager is None:
        # get current cookie
        session_id = handler.get_secure_cookie(SESSION_ID_ALIAS)
        manager = cls(session_id, handler.settings.get('session'))
        setattr(handler, property_name, manager)
        # set cookie
        handler.set_secure_cookie(SESSION_ID_ALIAS, manager.session_id)
    return manager