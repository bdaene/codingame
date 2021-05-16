
import re
import sys
from pathlib import Path


IMPORT_PATTERN = re.compile(r'from (\w+) import|import (\w+)')


def order_imports(file_paths):
    local_modules = {file.stem for file in file_paths}
    imports = {}
    nonlocal_imports = set()
    for file_path in file_paths:
        imports[file_path] = set()
        with open(file_path) as file:
            for line in file:
                if match := IMPORT_PATTERN.match(line):
                    module = match.group(1)
                    if module in local_modules:
                        imports[file_path].add(module)
                    else:
                        nonlocal_imports.add(line)

    files_order = []
    imported_modules = set()
    while file_paths:
        file_paths_ = []
        for file_path in file_paths:
            if imports[file_path] <= imported_modules:
                files_order.append(file_path)
                imported_modules.add(file_path.stem)
            else:
                file_paths_.append(file_path)
        file_paths = file_paths_

    return sorted(nonlocal_imports), files_order


def main():
    directory = Path(sys.argv[1])
    files = list(file for file in directory.iterdir() if file.name != '__pycache__')
    nonlocal_imports, files_order = order_imports(files)

    with open(f'{directory.name}.merge.py', 'w') as out_file:
        for line in nonlocal_imports:
            print(line, file=out_file, end='')
        for file_path in files_order:
            print(f'\n\n"""  {file_path.name}  """', file=out_file)
            with open(file_path) as in_file:
                for line in in_file:
                    if IMPORT_PATTERN.match(line):
                        print(f'# {line}', file=out_file, end='')
                    else:
                        print(f'{line}', file=out_file, end='')


if __name__ == "__main__":
    main()
