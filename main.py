
import argparse
from src.scraper.scraper_runner import ScraperRunner

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--iterations", type=int, default=1)
    parser.add_argument("-c", "--chunk_size", type=int, default=60)
    parser.add_argument("-t", "--threads", type=int, default=6)
    parser.add_argument("-f", "--csv_file", type=str, default=None)
    parser.add_argument("-n", "--dataset_name", type=str)


    args = parser.parse_args()
    iterations = args.iterations
    chunk_size = args.chunk_size
    threads = args.threads
    tweet_ids_path = args.csv_file
    source = args.dataset_name

    if tweet_ids_path and source:

        runner = ScraperRunner(
            iterations_number=iterations,
            chunk_size=chunk_size,
            threads=threads,
            tweet_ids_path=tweet_ids_path,
            data_source=source
        )
        runner.start_scraping()