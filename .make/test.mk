# How to test unit-test cases
unit-test:
	cd tmcprototype; \
	chmod 755 run_tox.sh; \
	./run_tox.sh;
# How to run lint job
lint:
	chmod 755 run_lint.sh; \
	./run_lint.sh;