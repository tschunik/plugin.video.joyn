# -*- coding: utf-8 -*-

from os import path
from json import dumps, loads
from datetime import datetime, timedelta
from platform import system
from .const import CONST
from . import xbmc_helper as xbmc_helper


def _get(cache_key, file_name, override_expire_secs=None):

	expire_datetime = None

	if (override_expire_secs is not None):
		expire_datetime = datetime.now() - timedelta(seconds=override_expire_secs)
	elif 'expires' in CONST['CACHE'][cache_key].keys() and CONST['CACHE'][cache_key]['expires'] is not None:
		expire_datetime = datetime.now() - timedelta(seconds=CONST['CACHE'][cache_key]['expires'])

	cache_data = {
		'data': None,
		'is_expired': True,
	}

	if path.exists(file_name):

		filectime = datetime.fromtimestamp(path.getctime(file_name))
		filemtime = datetime.fromtimestamp(path.getmtime(file_name))

		if filemtime is None or filectime > filemtime:
			filemtime = filectime

		with open(file_name) as cache_infile:
			cache_data.update({'data': cache_infile.read()})

		if filemtime >= expire_datetime or expire_datetime is None:
			cache_data.update({'is_expired': False})

	return cache_data


def _set(cache_key, file_name, data):

	cache_path = xbmc_helper.get_file_path(CONST['CACHE_DIR'], file_name)
	with open (cache_path, 'w') as cache_outfile:
		cache_outfile.write(data)


def get_json(cache_key, override_expire_secs=None):

	cache_data = _get(cache_key, xbmc_helper.get_file_path(CONST['CACHE_DIR'], CONST['CACHE'][cache_key]['key'] + '.json'))

	if cache_data['data'] is not None:
		try:
			cache_data.update({'data': loads(cache_data['data'])})
		except ValueError:
			xbmc_helper.log_error('Could decode as json from cache: ' + cache_key)
			pass

	return cache_data


def set_json(cache_key, data):

	try:
		_set(cache_key, CONST['CACHE'][cache_key]['key'] + '.json', dumps(data))
	except ValueError:
		xbmc_helper.log_error('Could not encode json from cache: ' + cache_key)
		pass
