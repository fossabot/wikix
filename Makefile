.PHONY: build
build:
	find base_wiki/output/ -type f -delete
	pipenv run -- python main.py --no-progress-bar -w base_wiki
	rm -rf base_wiki/output/s/
	cp -r base_wiki/static/ base_wiki/output/s/

.PHONY: serve
serve:
	pipenv run -- python main.py -w base_wiki/output --server
