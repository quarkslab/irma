PYTHON=`which python`
DESTDIR=/
DISTDIR=$(CURDIR)/deb_dist
BUILDIR=$(CURDIR)/debian/irma-brain
PROJECT=irma-brain
VERSION=1.0.4

all:
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
	dpkg-buildpackage -i -I -rfakeroot -us -uc

clean:
	$(PYTHON) setup.py clean
	#$(MAKE) -f $(CURDIR)/debian/rules clean
	rm -rf $(CURDIR)/debian/*.substvars $(CURDIR)/debian/*.log
	rm -rf $(CURDIR)/debian/irma-rsyslog-server
	rm -rf $(CURDIR)/debian/irma-brain-rsyslog
	rm -rf $(CURDIR)/debian/irma-brain-celery
	rm -rf $(CURDIR)/debian/irma-brain-logrotate
	rm -rf $(CURDIR)/debian/irma-brain-rabbitmq
	rm -rf $(CURDIR)/debian/irma-brain-ftpd
	rm -rf $(CURDIR)/debian/irma-brain-redis
	rm -rf build/ MANIFEST $(DISTDIR) $(BUILDIR)
	find . -name '*.pyc' -delete

