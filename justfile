install-deps:
	source config.sh
run:
	python3 -m src.main
test:
	pytest