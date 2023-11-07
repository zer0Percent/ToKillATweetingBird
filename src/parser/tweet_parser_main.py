import argparse
from src.parser.tweet.parser_runner import TweetParserRunner

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--dataset_name", type=str)
    
    args = parser.parse_args()
    data_source = args.dataset_name

    parse_runner = TweetParserRunner()
    parse_runner.start(data_source)