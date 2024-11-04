# -*- coding: utf-8 -*-
"""

    Copyright (C) 2018-2018 plugin.video.youtube

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""

from __future__ import absolute_import, division, unicode_literals

import json
import os
from io import open

from ..constants import DATA_PATH
from ..logger import Logger
from ..utils import make_dirs, merge_dicts, to_unicode


class JSONStore(Logger):
    BASE_PATH = make_dirs(DATA_PATH)

    def __init__(self, filename):
        if self.BASE_PATH:
            self.filename = os.path.join(self.BASE_PATH, filename)
        else:
            self.log_error('JSONStore.__init__ - temp directory not available')
            self.filename = None

        self._data = {}
        self.load()
        self.set_defaults()

    def set_defaults(self, reset=False):
        raise NotImplementedError

    def save(self, data, update=False, process=None):
        if not self.filename:
            return

        if update:
            data = merge_dicts(self._data, data)
        if data == self._data:
            self.log_debug('JSONStore.save - data unchanged'
                           '\n\tFile: {0}'.format(self.filename))
            return
        self.log_debug('JSONStore.save - saving'
                       '\n\tFile: {0}'.format(self.filename))
        try:
            if not data:
                raise ValueError
            _data = json.loads(json.dumps(data, ensure_ascii=False))
            with open(self.filename, mode='w', encoding='utf-8') as jsonfile:
                jsonfile.write(to_unicode(json.dumps(_data,
                                                     ensure_ascii=False,
                                                     indent=4,
                                                     sort_keys=True)))
            self._data = process(_data) if process is not None else _data
        except (IOError, OSError):
            self.log_error('JSONStore.save - access error'
                           '\n\tFile: {0}'.format(self.filename))
            return
        except (TypeError, ValueError):
            self.log_error('JSONStore.save - invalid data'
                           '\n\tData: |{0}|'.format(data))
            self.set_defaults(reset=True)

    def load(self, process=None):
        if not self.filename:
            return

        self.log_debug('JSONStore.load - loading'
                       '\n\tFile: {0}'.format(self.filename))
        try:
            with open(self.filename, mode='r', encoding='utf-8') as jsonfile:
                data = jsonfile.read()
            if not data:
                raise ValueError
            _data = json.loads(data)
            self._data = process(_data) if process is not None else _data
        except (IOError, OSError):
            self.log_error('JSONStore.load - access error'
                           '\n\tFile: {0}'.format(self.filename))
        except (TypeError, ValueError):
            self.log_error('JSONStore.load - invalid data'
                           '\n\tData: |{0}|'.format(data))

    def get_data(self, process=None):
        try:
            if not self._data:
                raise ValueError
            _data = json.loads(json.dumps(self._data, ensure_ascii=False))
            return process(_data) if process is not None else _data
        except (TypeError, ValueError):
            self.log_error('JSONStore.get_data - invalid data'
                           '\n\tData: |{0}|'.format(self._data))
            self.set_defaults(reset=True)
        _data = json.loads(json.dumps(self._data, ensure_ascii=False))
        return process(_data) if process is not None else _data
