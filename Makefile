all: crime.json
	$(MAKE) -C img all

test: all
	python3 -m http.server

crime.json: scrape_crime.py
	python3 scrape_crime.py

.PHONY: all test
