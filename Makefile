PYTHON  = `which python`
DESTDIR = /
DISTDIR = $(CURDIR)/deb_dist
BUILDIR = $(CURDIR)/debian/irma-probe
PROJECT = irma-probe
VERSION = 1.1.0

all: help

help:
	@echo "make source - Create source package"
	@echo "make install - Install on local system"
	@echo "make buildrpm - Generate a rpm package"
	@echo "make builddeb - Generate a deb package"
	@echo "make clean - Get rid of scratch and byte files"

source:
	$(PYTHON) setup.py sdist $(COMPILE)

install:
	$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)

buildrpm:
	$(PYTHON) setup.py bdist_rpm --post-install=rpm/postinstall --pre-uninstall=rpm/preuninstall

builddeb:
	# build the source package in the parent directory
	# then rename it to project_version.orig.tar.gz
	$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=$(DISTDIR) 
	rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' $(DISTDIR)/*
	# build the package
	dpkg-buildpackage -i -I -rfakeroot -uc -us

clean:
	$(PYTHON) setup.py clean
	#$(MAKE) -f $(CURDIR)/debian/rules clean
	rm -rf $(CURDIR)/irma_probe_app.egg-info
	rm -rf $(CURDIR)/debian/*.log
	rm -rf $(CURDIR)/debian/*.substvars
	rm -rf $(CURDIR)/debian/irma-probe
	rm -rf $(CURDIR)/debian/irma-probe-logrotate
	rm -rf $(CURDIR)/debian/irma-probe-rsyslog
	rm -rf build/ MANIFEST $(DISTDIR) $(BUILDIR)
	find . -name '*.pyc' -delete
