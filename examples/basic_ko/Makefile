all:
	uv run cvgen filter extended_template.yaml --target-verbosity 1 --include-tags '' | uv run cvgen collapse -k ko > output_ko.yaml && uv run rendercv render output_ko.yaml

# Usage: make render INPUT=your_input_file.yaml
# Example: make render INPUT=raw_ai.yaml
render:
	uv run cvgen filter $(INPUT) --target-verbosity 1 --include-tags '' | uv run cvgen collapse -k ko > output_ko.yaml && uv run rendercv render output_ko.yaml
