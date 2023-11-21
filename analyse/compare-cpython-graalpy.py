import argparse
import os 
from CpythonGraalpyComparator import CpythonGraalpyComparator
import csv

parser = argparse.ArgumentParser()
parser.add_argument('--output', help='output csv file with results')
parser.add_argument('--cpython-files', default='cpython-test-results.xml', help='name of the JunitXML-files with cpython results')
parser.add_argument('--graalpy-files', default='graalpy-test-results.xml', help='name of the JunitXML-files with graalpy results')
parser.add_argument('--input', help='name of result folder')


if __name__ == "__main__":
    args = parser.parse_args()

    input_folder = args.input
    output = args.output
    cpython_files = args.cpython_files
    graalpy_files = args.graalpy_files

    graalpy_packages = list()
    cpython_packages = list()
    for path, subdirs, _ in os.walk(input_folder):
        package = path.split('/')[-1]
        graalpy_packages.append((package, os.path.join(path, graalpy_files)))
        cpython_packages.append((package, os.path.join(path, cpython_files)))
    
    comparator = CpythonGraalpyComparator(cpython_packages, graalpy_packages)
    comparator.load()
    comparator.save(output)
        

