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
			ips=self._get_octopi_ips(),
			hardware=self._get_octopi_hardware()
		))

	def _get_octopi_version(self):
		return self._get_file_contents("/etc/octopi_version", ["unknown"])[0]

	def _get_octopi_commit(self):
		return self._get_file_contents("/etc/octopi_commit", ["unknown"])[0]

	def _get_file_contents(self, path, default=None):
		import os
		if os.path.exists(path):
			try:
				with open(path, "r") as f:
					return f.readlines()
			except:
				self._logger.exception("Exception while reading {path}".format(**locals()))
		return default

	def _get_octopi_ips(self):
		from octoprint.util import interface_addresses
		import socket
		return sorted(filter(lambda x: x != "127.0.0.1", interface_addresses()), key=lambda x: socket.inet_aton(x))

	def _get_octopi_hardware(self):
		cpuinfo = self._get_file_contents("/proc/cpuinfo")
		if cpuinfo is None:
			return None

		interesting_keys = ("hardware", "revision", "serial")
		parsed = {key.lower(): value for key, value in map(lambda x: map(lambda y: y.strip(), x.split(":", 1)), cpuinfo) if key.lower() in interesting_keys}

		model = "unknown"
		revision = parsed["revision"] if "revision" in parsed else "unknown"

		# revision mapping from http://www.raspberrypi-spy.co.uk/2012/09/checking-your-raspberry-pi-board-version/
		if revision in ("0002"):
			model = "Raspberry Pi B Revision 1.0, 256MB RAM"
		elif revision in ("0003"):
			model = "Raspberry Pi B Revision 1.0 + ECN0001, 256 MB RAM"
		elif revision in ("0004", "0005", "0006"):
			model = "Raspberry Pi B Revision 2.0, 256 MB RAM"
		elif revision in ("0007", "0008", "0009"):
			model = "Raspberry Pi A, 256 MB RAM"
		elif revision in ("000d", "000e", "000f"):
			model = "Raspberry Pi B Revision 2.0, 512 MB RAM"
		elif revision in ("0010"):
			model = "Raspberry Pi B+, 512 MB RAM"
		elif revision in ("0011"):
			model = "Raspberry Pi Compute Module, 512 MB RAM"
		elif revision in ("0012"):
			model = "Raspberry Pi A+, 256 MB RAM"
		elif revision in ("a01041", "a21041"):
			model = "Raspberry Pi2 B, 1 GB RAM"

		return dict(
			model=model,
			revision=revision,
			chipset_family=parsed["hardware"] if "hardware" in parsed else "unknown",
			serial=parsed["serial"] if "serial" in parsed else "unknown"
		)

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

