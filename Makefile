
.PHONY: clean
clean:
	@ rm -rf beam-*txt-*

.PHONY: run
run: 
	DATAFLOW_RUNNER=DirectRunner ENVIRONMENT=development python web.py

.PHONY: lint
lint:
	@ pylint --output-format parseable --rcfile pylintrc *.py
	@ echo 'Linting code...'