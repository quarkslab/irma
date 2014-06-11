PYTHON=`which python`
DESTDIR=/
DISTDIR=$(CURDIR)/deb_dist
BUILDIR=$(CURDIR)/debian/irma-frontend
PROJECT=irma-frontend
VERSION=1.1.0

all:
	@echo "make web-dist - do magic on web files"
	@echo "make source - Create source package"
	@echo "make install - Install on local system"
	@echo "make buildrpm - Generate a rpm package"
	@echo "make builddeb - Generate a deb package"
	@echo "make clean - Get rid of scratch and byte files"

web-dist:
	@cd web/ && npm install
	@cd web/ && bower install
	@cd web/ && ln -sf `pwd`/bower_components `pwd`/app/bower_components
	@cd web/ && grunt build --force
	@cd web/ && cp -r `pwd`/.tmp/styles `pwd`/dist/styles

source:
	$(PYTHON) setup.py sdist $(COMPILE)

install:
	$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)

buildrpm:
	$(PYTHON) setup.py bdist_rpm --post-install=rpm/postinstall --pre-uninstall=rpm/preuninstall

builddeb: web-dist
	# build the source package in the parent directory
	# then rename it to project_version.orig.tar.gz
	$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=$(DISTDIR) 
	rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' $(DISTDIR)/*
	# build the package
	dpkg-buildpackage -i -I -rfakeroot -us -uc

clean:
	$(PYTHON) setup.py clean
	#$(MAKE) -f $(CURDIR)/debian/rules clean
	rm -rf $(CURDIR)/debian/irma-frontend
	rm -rf $(CURDIR)/debian/irma-frontend-api-uwsgi
	rm -rf $(CURDIR)/debian/irma-frontend-api
	rm -rf $(CURDIR)/debian/irma-frontend-web-data
	rm -rf $(CURDIR)/debian/irma-frontend-rsyslog
	rm -rf $(CURDIR)/debian/irma-frontend-logrotate
	rm -rf $(CURDIR)/debian/irma-frontend-web-nginx
	rm -rf build/ MANIFEST $(DISTDIR) $(BUILDIR)
	find . -name '*.pyc' -delete

