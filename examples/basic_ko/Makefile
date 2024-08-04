all:
	cvgen filter extended_template.yaml --target-verbosity 1 --include-tags '' | cvgen collapse -k ko > output_ko.yaml && rendercv render output_ko.yaml --use-local-latex-command xelatex
