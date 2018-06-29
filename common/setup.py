from distutils.core import setup
from src import __version__

setup(
    name="irma.common",
    version=__version__,
    author="Quarkslab",
    author_email="irma@quarkslab.com",
    description="The common component of the IRMA software",
    packages=["irma.common",
              "irma.common.base",
              "irma.common.utils",
              "irma.common.configuration",
              "irma.common.ftp",
              "irma.common.plugins"],
    package_dir={"irma.common": "src",
                 "irma.common.utils": "src/utils",
                 "irma.common.base": "src/base",
                 "irma.common.plugins": "src/plugins"},
    namespace_packages=["irma"]
)
