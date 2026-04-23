SCSS_SRC  = style.scss
CSS_OUT   = static/style.css
SASS      ?= node_modules/.bin/sass
STYLELINT ?= node_modules/.bin/stylelint

all: build
.PHONY: all

install:
	npm install
.PHONY: install

build: $(SASS) assets
	$(SASS) --style=compressed --no-source-map $(SCSS_SRC) $(CSS_OUT)
.PHONY: build

lint: $(STYLELINT)
	$(STYLELINT) "*.scss"
.PHONY: lint

format: $(PRETTIER)
	$(PRETTIER) --write $(SCSS_SRC)
.PHONY: format

clean:
	rm -f $(CSS_OUT)
.PHONY: clean

$(SASS) $(STYLELINT) $(PRETTIER):
	$(MAKE) install
