# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import flask

class OctopiPlugin(octoprint.plugin.TemplatePlugin,
                   octoprint.plugin.AssetPlugin,
                   octoprint.plugin.SimpleApiPlugin):

	##~~ AssetPlugin

	def get_assets(self):
		return dict(
			js=["js/octopi.js"]
		)

	##~~ SimpleApiPlugin

	def on_api_get(self, request):
		return flask.jsonify(dict(
			version=self._get_octopi_version(),
			commit=self._get_octopi_commit(),
			ips=self._get_octopi_ips()
		))

	def _get_octopi_version(self):
		return self._get_file_contents("/etc/octopi_version", "unknown")

	def _get_octopi_commit(self):
		return self._get_file_contents("/etc/octopi_commit", "unknown")

	def _get_file_contents(self, path, default=None):
		import os
		if os.path.exists(path):
			try:
				with open(path, "r") as f:
					return f.readline()
			except:
				self._logger.exception("Exception while reading {path}".format(**locals()))
		return default

	def _get_octopi_ips(self):
		from octoprint.util import interface_addresses
		import socket
		return sorted(filter(lambda x: x != "127.0.0.1", interface_addresses()), key=lambda x: socket.inet_aton(x))

__plugin_name__ = "OctoPi"

def __plugin_check__():
	import os
	import sys

	import logging
	logger = logging.getLogger("octoprint.plugins.octopi")

	if not sys.platform == "linux2":
		logger.warn("Linux platform expected, not {}, disabling plugin".format(sys.platform))
		return False

	if not os.path.exists("/etc/octopi_version"):
		logger.warn("/etc/octopi_version does not exist, this is not an OctoPi installation, disabling plugin")
		return False

	return True

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = OctopiPlugin()

