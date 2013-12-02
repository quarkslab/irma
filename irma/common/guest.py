import pymongo
from pymongo import Connection

# See http://stackoverflow.com/questions/1305532/

class Guest:
    
    def __init__(self):
        self._label = None
        self._uuid = None
        self._os_type = None
        self._os_variant = None
        self._state = None
        self._locked = None
        self._disks = None
        self._master_label = None
        self._started_on = None
        self._shutdown_on = None

    ##########################################################################
    # Getters and setters
    ##########################################################################

    @property
    def label(self):
        return self._label;
    
    @label.setter
    def label(self, val):
        self._label = val

    @label.deleter
    def label(self):
        del self._label


    @property
    def uuid(self):
        return self._uuid;
    
    @uuid.setter
    def uuid(self, val):
        self._uuid = val

    @uuid.deleter
    def uuid(self):
        del self._uuid

    
    @property
    def os_type(self):
        return self._os_type;
    
    @os_type.setter
    def os_type(self, val):
        self._os_type = val

    @os_type.deleter
    def os_type(self):
        del self._os_type

     
    @property
    def os_variant(self):
        return self._os_variant;
    
    @os_variant.setter
    def os_variant(self, val):
        self._os_variant = val

    @os_variant.deleter
    def os_variant(self):
        del self._os_variant

     
    @property
    def state(self):
        return self._state;
    
    @state.setter
    def state(self, val):
        self._state = val

    @state.deleter
    def state(self):
        del self._state


    @property
    def locked(self):
        return self._locked;
    
    @locked.setter
    def locked(self, val):
        self._locked = val

    @locked.deleter
    def locked(self):
        del self._locked


    @property
    def disks(self):
        return self._disks;
    
    @disks.setter
    def disks(self, val):
        self._disks = val

    @disks.deleter
    def disks(self):
        del self._disks


    @property
    def master_label(self):
        return self._master_label;
    
    @master_label.setter
    def master_label(self, val):
        self._master_label = val

    @master_label.deleter
    def master_label(self):
        del self._master_label


    @property
    def started_on(self):
        return self._started_on;
    
    @started_on.setter
    def started_on(self, val):
        self._started_on = val

    @started_on.deleter
    def started_on(self):
        del self._started_on

    
    @property
    def shutdown_on(self):
        return self._shutdown_on;
    
    @shutdown_on.setter
    def shutdown_on(self, val):
        self._shutdown_on = val

    @shutdown_on.deleter
    def shutdown_on(self):
        del self._shutdown_on
    

    def test(self):
        self._label = None
        self._uuid = None
        self._os_type = None
        self._os_variant = None
        self._state = None
        self._locked = None
        self._disks = None
        self._master_label = None
        self._started_on = None
        self._shutdown_on = None

        return dict((key, getattr(self, key)) for key in dir(self) if not key.startswith('_') and not callable(getattr(self, key)))

if __name__ == '__main__':
    guest = Guest()
    print(guest.test())
