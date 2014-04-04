import platform
from probes.processing import Processing


class System(Processing):

    def run(self, *args, **kwargs):
        results = dict()
        results = {
            'architecture': platform.machine(),
            'system': platform.system(),
            'version': platform.version(),
            'release': platform.release(),
            'description': None
        }
        # add specific results
        system = results['system']
        if system == 'Linux':
            results['description'] = str(platform.linux_distribution())
        elif system == 'Windows':
            results['description'] = str(platform.win32_ver())
        elif system == 'Darwin':
            results['description'] = str(platform.mac_ver())
        return results
