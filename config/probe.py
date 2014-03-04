from lib.irma.configuration.ini import TemplatedConfiguration

##############################################################################
# probe configuration
##############################################################################

template_probe_config = {
    'broker_probe': [ 
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 5672),
        ('vhost', TemplatedConfiguration.string, None),
        ('username', TemplatedConfiguration.string, None),
        ('password' , TemplatedConfiguration.string, None)
    ],
    'backend_probe': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 6379),
        ('db', TemplatedConfiguration.integer, None),
    ],
    'ftp_brain': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 21),
        ('username', TemplatedConfiguration.string, None),
        ('password' , TemplatedConfiguration.string, None),
    ],
}

probe_config = TemplatedConfiguration("config/probe.ini", template_probe_config)
