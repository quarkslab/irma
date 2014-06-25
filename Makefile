PYTHON=`which python`
DESTDIR=/
DISTDIR=$(CURDIR)/deb_dist
BUILDIR=$(CURDIR)/debian/irma-frontend
PROJECT=irma-frontend
VERSION=1.0.3

all:
	#@echo "make web-dist - do magic on web files"
	@echo "make source - Create source package"
	@echo "make install - Install on local system"
	@echo "make buildrpm - Generate a rpm package"
	@echo "make builddeb - Generate a deb package"
	@echo "make clean - Get rid of scratch and byte files"

web-dist:
	@cd client/ && gulp build

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
	rm -rf build/ MANIFEST $(DISTDIR) $(BUILDIR)
	find . -name '*.pyc' -delete

