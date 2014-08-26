#
# This code is a modified version of the django_windows_tools/service.py
# file located at https://github.com/antoinemartin/django-windows-tools/
#
# FastCGI-to-WSGI bridge for files/pipes transport (not socket)
#
# Copyright (c) 2012 Openance SARL
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import win32serviceutil
import subprocess
import os
import os.path
import sys
import platform

import multiprocessing.forking
import logging
import ConfigParser
import ctypes
import traceback

import win32service
import win32event
import win32con
import win32file

from os.path import abspath, dirname
from multiprocessing import Process
from multiprocessing.util import get_logger


GenerateConsoleCtrlEvent = ctypes.windll.kernel32.GenerateConsoleCtrlEvent

old_get_preparation_data = multiprocessing.forking.get_preparation_data


# Monkey patch the Windows Process implementation to avoid thinking
# That 'PythonService.exe' is a python script
def new_get_preparation_data(name):
    d = old_get_preparation_data(name)
    if 'main_path' in d and d['main_path'].lower().endswith('.exe'):
        del d['main_path']
    return d

multiprocessing.forking.get_preparation_data = new_get_preparation_data

# Do the same monkey patching on billiard which is a fork of
# multiprocessing
try:
    import billiard.forking as billiard_forking
    billiard_old_get_preparation_data = billiard_forking.get_preparation_data

    def billiard_new_get_preparation_data(name):
        d = billiard_old_get_preparation_data(name)
        if 'main_path' in d and d['main_path'].lower().endswith('.exe'):
            d['main_path'] = '__main__.py'
        return d

    billiard_forking.get_preparation_data = billiard_new_get_preparation_data
except:
    pass


def log(msg):
    '''Log a message in the Event Viewer as an informational message'''
    import servicemanager
    servicemanager.LogInfoMsg(str(msg))


def error(msg):
    '''Log a message in the Event Viewer as an error message'''
    import servicemanager
    servicemanager.LogErrorMsg(str(msg))


def initialize_logger(config):
    class StdErrWrapper:
        """
            Call wrapper for stderr
        """
        def write(self, s):
            get_logger().info(s)
    import logging

    logger = get_logger()
    values = dict(
        format='[%(levelname)s/%(processName)s] %(message)s',
        filename=None,
        level='INFO',
    )
    if config and config.has_section('log'):
        for (name, value) in config.items('log'):
            values[name] = value

    if values['filename']:
        formatter = logging.Formatter(values['format'])
        handler = logging.FileHandler(values['filename'])
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(
            getattr(logging, values['level'].upper(), logging.INFO)
        )
        sys.stderr = StdErrWrapper()


def start_command(config, args):
    initialize_logger(config)
    print('starting command: %s' % ' '.join(args))
    get_logger().info("Starting command: %s" % " ".join(args))
    try:
        subprocess.call(args, shell=True)
    except:
        pass


def spawn_command(config, server_name):
    '''
    Spawn a command specified in a configuration file and return the process
    object.
    '''
    args = []
    args.append(config.get(server_name, 'command'))
    args += config.get(server_name, 'parameters').split()
    process = Process(target=start_command, args=(config, args,))
    process.start()
    log('Spawned %s' % ' '.join(args))
    return process


def start_commands(config):
    '''
    Spawn all the commands specified in a configuration file and return an
    array containing all the processes.
    '''
    processes = []
    node_name = platform.node()
    if config.has_section(node_name):
        services = config.get(node_name, 'run')
    else:
        services = config.get('services', 'run')
    for server_name in services.split():
        processes.append(spawn_command(config, server_name))
    return processes


def end_commands(processes):
    '''
    Terminate all the processes in the specified array.
    '''
    for process in processes:

        process.terminate()
        process.join()


def test_commands(base_path=None, timeout=10):
    '''
    Method to test the spawn and termination of commands present in the
    configuration file.
    '''
    config = read_config(base_path)
    initialize_logger(config)
    processes = start_commands(config)
    import time
    time.sleep(timeout)
    end_commands(processes)


def get_config_modification_handle(path=None):
    '''Returns a Directory change handle on the configuration directory.

    This handle will be used to restart the IRMA commands child processes
    in case the configuration file has changed in the directory.
    '''
    if not path:
        path = dirname(abspath(__file__))

    change_handle = win32file.FindFirstChangeNotification(
        path,
        0,
        win32con.FILE_NOTIFY_CHANGE_LAST_WRITE
    )
    return change_handle


def read_config(base_path=None, filename='service.ini'):
    '''
    Reads the configuration file containing processes to spawn information
    '''
    if not base_path:
        base_path = dirname(abspath(__file__))
    config = ConfigParser.ConfigParser()
    config.optionxform = str
    path = os.path.join(base_path, filename)
    log(path)
    config.read(path)
    return config


class IRMAService(win32serviceutil.ServiceFramework):
    """NT Service."""

    _svc_name_ = "irma-service"
    _svc_display_name_ = "IRMA background Processes"
    _svc_description_ = "Run the IRMA background Processes"
    _config_filename = 'service.ini'
    _base_path = dirname(abspath(__file__))

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        log('Initialization')
        # create an event that SvcDoRun can wait on and SvcStop
        # can set.
        self.config = read_config(self._base_path, self._config_filename)
        initialize_logger(self.config)
        if self._base_path not in sys.path:
            sys.path.append(self._base_path)

        parent_path = dirname(self._base_path)
        if parent_path not in sys.path:
            sys.path.append(parent_path)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        log('starting')
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        base_path = self._base_path
        config_filename = self._config_filename
        self.modification_handle = get_config_modification_handle(base_path)
        config_filepath = os.path.join(base_path, config_filename)
        self.configuration_mtime = os.stat(config_filepath).st_mtime

        keep_running = True
        do_start = True
        while keep_running:
            # do the actual start
            if do_start:
                self.start()

            log('Started. Waiting for stop')
            index = win32event.WaitForMultipleObjects(
                [self.stop_event, self.modification_handle],
                False, win32event.INFINITE)
            if index == 0:
                # The stop event has been signaled. Stop execution.
                keep_running = False
            else:
                # re-initialise handle
                win32file.FindNextChangeNotification(self.modification_handle)

                base_path = self._base_path
                config_filename = self._config_filename
                config_filepath = os.path.join(base_path, config_filename)
                new_mtime = os.stat(config_filepath).st_mtime
                if new_mtime != self.configuration_mtime:
                    self.configuration_mtime = new_mtime
                    do_start = True
                    log('Restarting child processes as the configuration '
                        'has changed')
                    self.stop()
                    self.config = read_config(base_path, config_filename)
                else:
                    do_start = False

        win32file.FindCloseChangeNotification(self.modification_handle)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        log('Stopping')
        # Do the actual stop
        self.stop()
        log('Stopped')
        win32event.SetEvent(self.stop_event)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def start(self):
        self.processes = start_commands(self.config)

    def stop(self):
        if self.processes:
            end_commands(self.processes)
            self.processes = []
        node_name = platform.node()
        if self.config.has_section(node_name):
            clean = self.config.get(node_name, 'clean')
        else:
            clean = self.config.get('services', 'clean')
        if clean:
            for file in clean.split(';'):
                try:
                    os.remove(file)
                except:
                    error("Error while removing {0}\n{1}"
                          "".format(file, traceback.format_exc()))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_commands()
    else:
        IRMAService._base_path = dirname(abspath(__file__))
        win32serviceutil.HandleCommandLine(IRMAService)
