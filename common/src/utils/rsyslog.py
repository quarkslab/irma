#
# Copyright (c) 2013-2018 Quarkslab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

import logging.handlers
import ssl
import socket
import time

#
# Some constants ...
#
SYSLOG_UDP_PORT = 514


class SysLogHandler(logging.handlers.SysLogHandler):
    """
    A handler class which sends formatted logging records to a syslog
    server. Extends the default SysLogHandler with SSL and enable lazy
    connection.

    .. code-block:: python

        address = ('localhost', 514)
        [...]
        syslog = SysLogHandler(address=address,
                               socktype=socket.SOCK_STREAM,
                               use_ssl=True,
                               keyfile  = "client.key",
                               certfile = "client.crt",
                               ca_certs = "ca.crt",
                               cert_reqs= ssl.CERT_REQUIRED)
        [...]
        logger.addHandler(syslog)
    """

    # ================================
    #  Priorities (these are ordered)
    # ================================
    # system is unusable
    LOG_EMERG = logging.handlers.SysLogHandler.LOG_EMERG
    # action must be taken immediately
    LOG_ALERT = logging.handlers.SysLogHandler.LOG_ALERT
    # critical conditions
    LOG_CRIT = logging.handlers.SysLogHandler.LOG_CRIT
    # error conditions
    LOG_ERR = logging.handlers.SysLogHandler.LOG_ERR
    # warning conditions
    LOG_WARNING = logging.handlers.SysLogHandler.LOG_WARNING
    # normal but significant condition
    LOG_NOTICE = logging.handlers.SysLogHandler.LOG_NOTICE
    # informational
    LOG_INFO = logging.handlers.SysLogHandler.LOG_INFO
    # debug-level messages
    LOG_DEBUG = logging.handlers.SysLogHandler.LOG_DEBUG

    # ================
    #  Facility codes
    # ================
    # kernel messages
    LOG_KERN = logging.handlers.SysLogHandler.LOG_KERN
    # random user-level messages
    LOG_USER = logging.handlers.SysLogHandler.LOG_USER
    # mail system
    LOG_MAIL = logging.handlers.SysLogHandler.LOG_MAIL
    # system daemons
    LOG_DAEMON = logging.handlers.SysLogHandler.LOG_DAEMON
    # security/authorization messages
    LOG_AUTH = logging.handlers.SysLogHandler.LOG_AUTH
    # messages generated internally by syslogd
    LOG_SYSLOG = logging.handlers.SysLogHandler.LOG_SYSLOG
    # line printer subsystem
    LOG_LPR = logging.handlers.SysLogHandler.LOG_LPR
    # network news subsystem
    LOG_NEWS = logging.handlers.SysLogHandler.LOG_NEWS
    # UUCP subsystem
    LOG_UUCP = logging.handlers.SysLogHandler.LOG_UUCP
    # clock daemon
    LOG_CRON = logging.handlers.SysLogHandler.LOG_CRON
    # security/authorization messages (private)
    LOG_AUTHPRIV = logging.handlers.SysLogHandler.LOG_AUTHPRIV
    # FTP daemon
    LOG_FTP = logging.handlers.SysLogHandler.LOG_FTP

    # ========================
    #  Reserved for local use
    # ========================
    LOG_LOCAL0 = logging.handlers.SysLogHandler.LOG_LOCAL0
    LOG_LOCAL1 = logging.handlers.SysLogHandler.LOG_LOCAL1
    LOG_LOCAL2 = logging.handlers.SysLogHandler.LOG_LOCAL2
    LOG_LOCAL3 = logging.handlers.SysLogHandler.LOG_LOCAL3
    LOG_LOCAL4 = logging.handlers.SysLogHandler.LOG_LOCAL4
    LOG_LOCAL5 = logging.handlers.SysLogHandler.LOG_LOCAL5
    LOG_LOCAL6 = logging.handlers.SysLogHandler.LOG_LOCAL6
    LOG_LOCAL7 = logging.handlers.SysLogHandler.LOG_LOCAL7

    # ================================================
    #  Other codes through 15 reserved for system use
    # ================================================

    priority_names = {
        "alert":    LOG_ALERT,
        "crit":     LOG_CRIT,
        "critical": LOG_CRIT,
        "debug":    LOG_DEBUG,
        "emerg":    LOG_EMERG,
        "err":      LOG_ERR,
        "error":    LOG_ERR,        # DEPRECATED
        "info":     LOG_INFO,
        "notice":   LOG_NOTICE,
        "panic":    LOG_EMERG,      # DEPRECATED
        "warn":     LOG_WARNING,    # DEPRECATED
        "warning":  LOG_WARNING,
        }

    facility_names = {
        "auth":     LOG_AUTH,
        "authpriv": LOG_AUTHPRIV,
        "cron":     LOG_CRON,
        "daemon":   LOG_DAEMON,
        "ftp":      LOG_FTP,
        "kern":     LOG_KERN,
        "lpr":      LOG_LPR,
        "mail":     LOG_MAIL,
        "news":     LOG_NEWS,
        "security": LOG_AUTH,       # DEPRECATED
        "syslog":   LOG_SYSLOG,
        "user":     LOG_USER,
        "uucp":     LOG_UUCP,
        "local0":   LOG_LOCAL0,
        "local1":   LOG_LOCAL1,
        "local2":   LOG_LOCAL2,
        "local3":   LOG_LOCAL3,
        "local4":   LOG_LOCAL4,
        "local5":   LOG_LOCAL5,
        "local6":   LOG_LOCAL6,
        "local7":   LOG_LOCAL7,
        }

    # The map below appears to be trivially lowercasing the key. However,
    # there's more to it than meets the eye - in some locales, lowercasing
    # gives unexpected results. See SF #1524081: in the Turkish locale,
    # "INFO".lower() != "info"

    priority_map = {
        "DEBUG":    "debug",
        "INFO":     "info",
        "WARNING":  "warning",
        "ERROR":    "error",
        "CRITICAL": "critical"
    }

    def __init__(self, address=('localhost', SYSLOG_UDP_PORT),
                 facility=LOG_USER, socktype=socket.SOCK_DGRAM, **kwargs):
        """
        Initialize a handler.

        If address is specified as a string, a UNIX socket is used. To log to a
        local syslogd, "SysLogHandler(address="/dev/log")" can be used.
        If facility is not specified, LOG_USER is used.
        """
        logging.Handler.__init__(self)

        self.socket = None
        self.unixsocket = None

        self.address = address
        self.facility = facility
        self.socktype = socktype
        self.use_ssl = kwargs.pop("use_ssl", False)
        self.timeout = kwargs.pop("timeout", 1)
        self.kwargs = kwargs

        self.closeOnError = 0
        self.retryTime = None
        # Exponential backoff parameters.
        self.retryStart = 1.0
        self.retryMax = 30.0
        self.retryFactor = 2.0

    def makeSocket(self):
        if isinstance(self.address, str):
            self.unixsocket = 1
            self._connect_unixsocket(self.address)
        else:
            self.unixsocket = 0
            self.socket = socket.socket(socket.AF_INET, self.socktype)
            if self.socktype == socket.SOCK_STREAM:
                if self.use_ssl:
                    self.socket = ssl.wrap_socket(self.socket, **self.kwargs)
                self.socket.connect(self.address)

    def _connect_unixsocket(self, address):
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        # syslog may require either DGRAM or STREAM sockets
        try:
            if hasattr(self.socket, 'settimeout'):
                self.socket.settimeout(self.timeout)
            self.socket.connect(address)
        except socket.error:
            self.socket.close()
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                if self.use_ssl:
                    self.socket = ssl.wrap_socket(self.socket, **self.kwargs)
                if hasattr(self.socket, 'settimeout'):
                    self.socket.settimeout(self.timeout)
                self.socket.connect(address)
            except socket.error:
                self.socket.close()
                raise

    def createSocket(self):
        """
        Try to create a socket, using an exponential backoff with
        a max retry time. Thanks to Robert Olson for the original patch
        (SF #815911) which has been slightly refactored.
        """
        now = time.time()
        # Either retryTime is None, in which case this
        # is the first time back after a disconnect, or
        # we've waited long enough.
        if self.retryTime is None:
            attempt = 1
        else:
            attempt = (now >= self.retryTime)

        if attempt:
            try:
                self.makeSocket()
                self.retryTime = None  # next time, no delay before trying
            except socket.error:
                # Creation failed, so set the retry time and return.
                if self.retryTime is None:
                    self.retryPeriod = self.retryStart
                else:
                    self.retryPeriod = self.retryPeriod * self.retryFactor
                    if self.retryPeriod > self.retryMax:
                        self.retryPeriod = self.retryMax
                self.retryTime = now + self.retryPeriod

    def send(self, msg):
        """
        This function allows for partial sends which can happen when the
        network is busy.
        """
        if self.socket is None:
            self.createSocket()

        # self.socket can be None either because we haven't reached the retry
        # time yet, or because we have reached the retry time and retried,
        # but are still unable to connect.
        if self.socket:
            try:
                if hasattr(self.socket, "sendall"):
                    try:
                        self.socket.sendall(msg)
                    except socket.error:
                        self.closeSocket()
                        self.createSocket()
                        self.socket.sendall(msg)
                else:
                    sentsofar = 0
                    left = len(msg)
                    while left > 0:
                        sent = 0
                        try:
                            _msg = msg[sentsofar:]
                            if self.unixsocket:
                                sent = self.socket.send(_msg)
                            elif self.socktype == socket.SOCK_DGRAM:
                                sent = self.socket.sendto(_msg, self.address)
                        except Exception:
                            self.closeSocket()
                            self.createSocket()
                            if self.unixsocket:
                                sent = self.socket.send(_msg)
                            elif self.socktype == socket.SOCK_DGRAM:
                                sent = self.socket.sendto(_msg, self.address)
                        sentsofar = sentsofar + sent
                        left = left - sent
            except socket.error:
                self.closeSocket()
                self.socket = None  # so we can call createSocket next time

    def emit(self, record):
        """
        Emit a record.

        The record is formatted, and then sent to the syslog server. If
        exception information is present, it is NOT sent to the server.
        """
        # when talking to the unix-domain '/dev/log' socket, a zero-terminator
        # seems to be required.  this string is placed into a class variable so
        # that it can be overridden if necessary.

        log_tail = '\000' if self.unixsocket else '\n'
        msg = self.format(record) + log_tail
        """
        We need to convert record level to lowercase, maybe this will
        change in the future.
        """
        prio = '<%d>' % self.encodePriority(self.facility,
                                            self.mapPriority(record.levelname))
        # Message is a string. Convert to bytes as required by RFC 5424
        if type(msg) is str:
            msg = msg.encode('utf-8')
        msg = prio + msg
        try:
            self.send(msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    def handleError(self, record):
        """
        Handle an error during logging.

        An error has occurred during logging. Most likely cause -
        connection lost. Close the socket so that we can retry on the
        next event.
        """
        if self.closeOnError and self.socket:
            self.close()
            self.socket = None  # try to reconnect next time
        else:
            logging.Handler.handleError(self, record)

    def closeSocket(self):
        if not self.socket:
            return
        if self.unixsocket:
            self.socket.close()
        if isinstance(self.socket, ssl.SSLSocket):
            self.socket = self.socket.unwrap()
            self.socket.close()

    def close(self):
        self.acquire()
        try:
            self.closeSocket()
        finally:
            self.release()
        logging.Handler.close(self)
