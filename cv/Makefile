PYTHON ?= python3
LATEXMK ?= latexmk
PDF_NAME := Bernardin_Tamo_Amougou_CV.pdf
LATEX_DIR := latex
BUILD_DIR := $(LATEX_DIR)/build
OUTPUT_PDF := ../assets/pdf/$(PDF_NAME)

.PHONY: all generate pdf validate clean

all: validate

generate:
	$(PYTHON) scripts/generate_cv.py

pdf: generate
	mkdir -p $(BUILD_DIR) ../assets/pdf
	cd $(LATEX_DIR) && $(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build main.tex
	install -m 0644 $(BUILD_DIR)/main.pdf $(OUTPUT_PDF)

validate: pdf
	pdfinfo $(OUTPUT_PDF)
	pdftotext -layout $(OUTPUT_PDF) $(BUILD_DIR)/extracted.txt
	@test -s $(BUILD_DIR)/extracted.txt
	$(PYTHON) scripts/validate_cv.py

clean:
	cd $(LATEX_DIR) && $(LATEXMK) -C -outdir=build main.tex
	rm -f $(BUILD_DIR)/extracted.txt
