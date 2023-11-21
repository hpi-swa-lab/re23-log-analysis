import argparse
import os 
from ErrorAnalyser import ErrorAnalyser

parser = argparse.ArgumentParser()
parser.add_argument('--graalpy-files', default='graalpy-test-results.xml', help='name of the JunitXML-files with graalpy results')
parser.add_argument('--input', help='name of result folder')


if __name__ == "__main__":
    args = parser.parse_args()

    input_folder = args.input
    graalpy_files = args.graalpy_files

    files = list()
    for path, subdirs, _ in os.walk(input_folder):
        package = path.split('/')[-1]
        files.append((package, os.path.join(path, graalpy_files)))
    
    analyser = ErrorAnalyser(files)
    analyser.load()
    
    

        

