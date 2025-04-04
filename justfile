install-deps:
	source config.sh
run:
	python3 -m src.main
test:
	pytest
snipe:
	python3 -m src.utilities.sniper --deck-type type_1 --mode png --deck-name nativity_herods
t2:
	python3 -m src.utilities.sniper --deck-type type_2 --deck-name T2 --mode pdf
t1:
	python3 -m src.utilities.sniper --deck-type type_1 --deck-name nativity_herods --mode pdf