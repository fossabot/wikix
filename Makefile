.PHONY: build
build:
	find base_wiki/output/ -type f -delete
	pipenv run -- python -m wikix --no-progress-bar -w base_wiki
	rm -rf base_wiki/output/s/
	cp -r base_wiki/static/ base_wiki/output/s/

.PHONY: serve
serve:
	pipenv run -- python -m wikix -w base_wiki/output --server
