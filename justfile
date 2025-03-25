install-deps:
	source config.sh
run:
	python3 -m src.main
test:
	pytest
snipe:
	python3 -m src.utilities.sniper
pdf:
	python3 -m src.utilities.text_to_pdf