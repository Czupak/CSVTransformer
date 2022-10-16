# CSVTransformer
Transform CSV files

# Usage
JSON profile file should be created based on empty_profile.json

Usage:

`python csv_transformer.py -p profile.json [-i input.csv] [-o output.csv] [-id input_dir] [-io output_dir] [-s]`

Example:
1. Simple columns filter and map, one column uses value taken from input file name, input has headers

```python csv_transformer.py -p examples/column_filter.json```

2. Same as above, but input doesn't have headers

```python csv_transformer.py -p examples/column_filter_no_headers.json```

Output files will be created in `examples/output/`
