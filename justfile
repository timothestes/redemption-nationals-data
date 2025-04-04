install-deps:
	source config.sh
run:
	python3 -m src.main
test:
	pytest
snipe:
	python3 -m src.utilities.sniper --deck-type type_1
pdf:
	python3 -m src.utilities.text_to_pdf
t2:
	python3 -m src.utilities.sniper --deck-type type_2 --deck-name T2 --mode generate_decklist_pdf
t1:
	python3 -m src.utilities.sniper --deck-type type_1 --deck-name nativity_herods --mode generate_decklist_pdf