
import argparse
from src.scraper.runners.user.scraper_user_runner import ScraperUserRunner

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--iterations", type=int, default=1)
    parser.add_argument("-c", "--chunk_size", type=int, default=60)
    parser.add_argument("-t", "--threads", type=int, default=6)
    parser.add_argument("-f", "--csv_file", type=str, default=None)

    args = parser.parse_args()
    iterations = args.iterations
    chunk_size = args.chunk_size
    threads = args.threads
    usernames_path = args.csv_file

    if usernames_path:

        runner = ScraperUserRunner(
            iterations_number=iterations,
            chunk_size=chunk_size,
            threads=threads,
            usernames_path=usernames_path
        )
        runner.start_scraping()