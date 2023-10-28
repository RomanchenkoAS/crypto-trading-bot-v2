import cProfile
from scraping.scraper import Scraper

SETUP = {
    "currency_pair": "btcusdt",
    "range_size": 10,  # Number of Days in scraping period
    "interval": 60,  # Length of one cline
    "filename": "data.csv",  # Where to save the data | None to not save
}


def main():
    scraper = Scraper(currency_pair=SETUP["currency_pair"])
    scraper.set_time_range(range_size=SETUP["range_size"])
    scraper.scrape(interval=SETUP["interval"])
    scraper.visualize()
    scraper.save_to_csv(filename=SETUP["filename"])


if __name__ == "__main__":
    cProfile.run("main()")
