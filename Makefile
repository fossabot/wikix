.PHONY: build
build:
	find test_wiki/output/ -type f -delete \
	&& pipenv run -- python main.py --no-progress-bar -w test_wiki \
	&& cp -r test_wiki/static/* test_wiki/output/s

.PHONY: serve
serve:
	pipenv run -- python main.py -w test_wiki/output --server
