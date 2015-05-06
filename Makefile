TESTS=./tests
# this DB_PATH must match the path in the tests/brain.ini conf file
DB_PATH=${TESTS}/db/brain.db
RESULTS=${TESTS}/results
PACKAGES=brain
OPTIONS=--cover-erase --with-coverage --cover-package=${PACKAGES} --cover-html --cover-html-dir=${RESULTS} --with-xunit --xunit-file=${RESULTS}/brain_xunit.xml

test-env:
	rm ${DB_PATH} || exit 0
	mkdir -p ${RESULTS}
	export IRMA_BRAIN_CFG_PATH=${TESTS} && PYTHONPATH=. python scripts/create_user.py  test_brain test_brain test_brain

test: test-env
	nosetests ${TESTS}


testc: test-env
	pylint ${PACKAGES} 2>&1 > ${RESULTS}/brain.pylint || exit 0
	nosetests ${OPTIONS} ${TESTS}
