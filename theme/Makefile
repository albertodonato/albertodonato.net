SCSS_SRC = style.scss
CSS_OUT = static/style.css

PYGMENTS_LIGHT_THEME ?= friendly
PYGMENTS_DARK_THEME ?= nord-darker

DARK_SELECTORS = \
	'[data-theme="dark"] .highlight' \
	':root:not([data-theme="light"]) .highlight' \
	'[data-theme="dark"] pre.literal-block' \
	':root:not([data-theme="light"]) pre.literal-block'

PYGMENTS_CSS = uv run python pygments_css.py

SASS ?= node_modules/.bin/sass
STYLELINT ?= node_modules/.bin/stylelint


all: css
.PHONY: all

install:
	npm install
.PHONY: install

css: $(SASS)
	$(SASS) --no-source-map $(SCSS_SRC) /tmp/style-combined.css
	$(PYGMENTS_CSS) $(PYGMENTS_LIGHT_THEME) .highlight pre.literal-block >> /tmp/style-combined.css
	$(PYGMENTS_CSS) $(PYGMENTS_DARK_THEME) $(DARK_SELECTORS) >> /tmp/style-combined.css
	$(SASS) --style=compressed --no-source-map /tmp/style-combined.css $(CSS_OUT)
	rm /tmp/style-combined.css
.PHONY: css

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
