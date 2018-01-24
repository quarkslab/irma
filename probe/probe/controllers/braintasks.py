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

import celery
import config.parser as config
from probe.helpers.celerytasks import async_call

# declare a new Remote Brain application
brain_app = celery.Celery('braintasks')
config.conf_brain_celery(brain_app)
config.configure_syslog(brain_app)


# ============
#  Task calls
# ============

def register_probe(name, display_name, category, mimetype_regexp):
    """ send a task to the brain to register local probes"""
    task = async_call(brain_app, "brain.scan_tasks", "register_probe",
                      args=[name, display_name, category, mimetype_regexp])
    return task
