PYTHON  = `which python`
DESTDIR = /
DISTDIR = $(CURDIR)/deb_dist
BUILDIR = $(CURDIR)/debian/irma-frontend
PROJECT = irma-frontend
VERSION = 1.1.0

all: help

help:
	@echo "make web-static - create static web files"
	@echo "make web-dist - create dist (minified and uglyfied) version for web files"
	@echo "make source - Create source package"
	@echo "make install - Install on local system"
	@echo "make buildrpm - Generate a rpm package"
	@echo "make builddeb - Generate a deb package"
	@echo "make clean - Get rid of scratch and byte files"

web-static:
	@cd web/ && npm install
	@cd web/ && bower install

web-dist: web-static
	@cd web/ && gulp build && gulp dist

source: web-dist
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
	rm -rf $(CURDIR)/debian/*.log
	rm -rf $(CURDIR)/debian/*.substvars
	rm -rf $(CURDIR)/debian/irma-frontend
	rm -rf $(CURDIR)/debian/irma-frontend-uwsgi
	rm -rf $(CURDIR)/debian/irma-frontend-app
	rm -rf $(CURDIR)/debian/irma-frontend-rsyslog
	rm -rf $(CURDIR)/debian/irma-frontend-logrotate
	rm -rf $(CURDIR)/debian/irma-frontend-nginx
	rm -rf build/ MANIFEST $(DISTDIR) $(BUILDIR)
	find . -name '*.pyc' -delete
