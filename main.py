from src.insta_scraper import InstaScraper
from src.utils import CSV_Utils
import config

if __name__ == '__main__':
    # Initialize utils
    scraper = InstaScraper(config.INSTA_USERNAME)

    # Read profiles from CSV file
    csv_utils = CSV_Utils(config.INPUT_FILE)
    profiles = csv_utils.read_profile_from_file()

    # Divide profiles into chunks
    profiles_chunks = csv_utils.divide_list_into_chunks(profiles, config.CHUNK_SIZE)

    scraper.get_data_parallel(profiles_chunks)
