#!/usr/local/autopkg/python
# Created 06/22/23; NRJA

import platform
import logging
import threading

from autopkglib import Processor

__all__ = ["StopIfDownloadUnchanged"]

###########################
######### LOGGING #########
###########################

# Get hostname for log record
hostname = platform.node()
# Local logging location
path_to_log = "/var/tmp/stop_if_dl_same.log"

logging_level = logging.INFO

logging.basicConfig(
    level=logging_level,
    format="{asctime} " + f"[{hostname}]" + ": {levelname}: {message}",
    handlers=[logging.FileHandler(path_to_log), logging.StreamHandler()],
    style="{",
    datefmt="%Y-%m-%d %I:%M:%S %p",
)

log = logging.getLogger(__name__)

class StopIfDownloadUnchanged(Processor):
    description = ( "Aborts a recipe run if download_changed value is defined and set to False" )
    input_variables = {}

    output_variables = {
        "stop_processing_recipe": {
            "description": "Bool to stop eval of recipe"
        }
    }
    __doc__ = description

    def get_download_changed(self):
        """Loops until AutoPkg env download_changed is defined
        If defined as False, sets AutoPkg env stop_processing_recipe
        to True, aborting the current recipe run"""
        log.info(f"Starting background thread for {self.app_name}...")
        if "download_changed" not in self.env:
            log.warning(f"download_changed not in self.env for {self.app_name}")
        while "download_changed" not in self.env:
            pass
        self.env["stop_processing_recipe"] = True
        if self.env.get("download_changed") is True:
            self.env["stop_processing_recipe"] = False
        log.info(f"download_changed now in self.env for {self.app_name}")
        log.info(f"Got {self.env.get('download_changed')} for DL changed for {self.app_name}")
        # log.info(f"Got {self.env} for ENV for {self.app_name}")
        log.info(f"Got {self.env.get('stop_processing_recipe')} for stop_processing_recipe")
        return

    def main(self):
        """Sets initial DL changed value to None
        Sets get_download_changed func as bg func
        Starts it to run in parallels with AutoPkg recipe execution"""
        self.download_changed = None
        self.app_name = self.env.get("NAME")
        log.info(f"Got {self.app_name} for app name")
        bg_thread = threading.Thread(target=self.get_download_changed)
        bg_thread.start()

if __name__ == '__main__':
    processor = StopIfDownloadUnchanged()
    processor.execute_shell()
