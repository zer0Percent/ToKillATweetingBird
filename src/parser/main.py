import argparse
from parser_runner import ParserRunner

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--dataset_name", type=str)
    
    args = parser.parse_args()
    data_source = args.dataset_name

    parse_runner = ParserRunner()
    parse_runner.start(data_source)