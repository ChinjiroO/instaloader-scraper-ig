import time
import pandas as pd
import datetime
import csv
import os
from instaloader import Instaloader, Profile
from multiprocessing.pool import ThreadPool
from instaloader.exceptions import ProfileNotExistsException
from .utils import Scraping_Utils


class InstaScraper:
    def __init__(self, username):
        self.loader = Instaloader()
        self.username = username
        self.loader.interactive_login(username)
        self.loader.context.log(f"Logging in... {username}")

    def __del__(self):
        self.loader.close()

    def get_profile_data(self, profile):
        complete_sleep_time = 2
        sleep_time = 2
        try:
            profile_obj = Profile.from_username(
                self.loader.context, profile)

            if profile_obj.is_private:
                followers_count = profile_obj.followers
                likes_count = 0
                posts_count = 0
                status = "Private"
            else:
                scraping = Scraping_Utils(profile_obj, self.loader.context)
                followers_count = profile_obj.followers
                likes_count = scraping.get_average_likes()
                posts_count = scraping.get_posts_count()
                status = "Public"

            print(
                f"Profile: {profile}, Followers: {followers_count}, Likes: {likes_count}, Posts: {posts_count}, Status: {status}")
            print(f"Sleeping for {complete_sleep_time} seconds...")
            time.sleep(complete_sleep_time)
            return (profile, followers_count, likes_count, posts_count, status)
        except ProfileNotExistsException:
            print(
                f"Profile: {profile}, Followers: 0, Likes: 0, Posts: 0, Status: 'Profile not exists'")
            print(f"Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            return (profile, 0, 0, 0, "Profile not exists")

    def get_profiles_data(self, profiles):
        start_time = time.time()
        profiles_data = []
        num_profiles = len(profiles)
        completed_tasks = 0
        sleep_time = 5

        # pool = ThreadPool(6)
        for profile in profiles:
            result = self.get_profile_data(profile)
            profiles_data.append(result)
            # pool.apply_async(self.get_profile_data, args=(
            #     profile,), callback=lambda result: profiles_data.append(result))
            completed_tasks += 1

        while completed_tasks < num_profiles:
            print(f"Waiting ... {sleep_time} seconds")
            time.sleep(sleep_time)
        # pool.close()
        # pool.join()

        self.loader.context.log(
            f"Time taken: {time.time() - start_time} seconds, Profiles: {num_profiles}, Waiting time: {sleep_time} seconds...")

        return profiles_data

    def get_data_parallel(self, profiles_chunks):
        # Create a directory for the output CSV files
        output_dir = f"output-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        start_time = time.time()
        for i, chunk in enumerate(profiles_chunks):
            profiles_data = self.get_profiles_data(chunk)

            # Write profile data to CSV file with sequential numbering
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{output_dir}/profiles_data_{i+1}_{timestamp}.csv"

            try:
                with open(filename, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        ["Username", "Followers", "Avg Likes", "Posts", "Status"])
                    writer.writerows(profiles_data)
            except IOError:
                print("Error: could not write to CSV file")
                exit(1)

            print(f"Done with chunk {i+1} of {len(profiles_chunks)}")
            self.loader.close()
            time.sleep(5)

        # Merge all CSV files into one dataframe
        all_dataframes = []
        for file in os.listdir(output_dir):
            if file.startswith("profiles_data") and file.endswith(".csv"):
                df = pd.read_csv(f"{output_dir}/{file}")
                all_dataframes.append(df)
        merged_df = pd.concat(all_dataframes)

        # Write merged data to CSV file
        merged_filename = f"{output_dir}/merged_profiles_data_{timestamp}.csv"
        merged_df.to_csv(merged_filename, index=False)

        end_time = time.time()
        total_time = end_time - start_time
        print(f"All done! Time used: {total_time:.2f} seconds")
        # Open the merged CSV file in Excel
        try:
            os.system(f'open {merged_filename}')
        except OSError:
            print("Error: could not open merged CSV file in Excel")
