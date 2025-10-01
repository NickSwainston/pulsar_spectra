import re
import glob

# Find all Python files to process
py_files = glob.glob("*.py")  # adjust path if needed

# Regex pattern to match the open + safe_dump block
pattern = re.compile(
    r'with open\(\s*"([^"]+\.yaml)"\s*,\s*"w"\s*\) as cat_file:\s*\n\s*yaml\.safe_dump\(\s*pulsar_dict\s*,\s*cat_file\s*,\s*sort_keys=False\s*,\s*indent=2\s*\)',
    re.MULTILINE
)

for py_file in py_files:
    with open(py_file, "r") as f:
        content = f.read()

    # Replace the block with dump_yaml(filename)
    new_content, count = pattern.subn(r'dump_yaml(pulsar_dict, "\1")', content)

    if count > 0:
        with open(py_file, "w") as f:
            f.write(new_content)
        print(f"Updated {count} occurrence(s) in {py_file}")
