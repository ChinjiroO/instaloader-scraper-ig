import csv
import os
import json
from instaloader.nodeiterator import FrozenNodeIterator, resumable_iteration

class CSV_Utils:
    def __init__(self, input_file):
        self.input_file = input_file
        pass

    def read_profile_from_file(self):
        profiles = []
        with open(self.input_file) as f:
            reader = csv.reader(f)
            for row in reader:
                profiles.append(row[0])

        return profiles

    def divide_list_into_chunks(self, profiles, n):
        return [profiles[i:i+n] for i in range(0, len(profiles), n)]

class Scraping_Utils:
    def __init__(self, profile, ctx):
        self.profile_obj = profile
        self.ctx = ctx
        self.post_iterator = profile.get_posts()


    def get_posts_count(self):
      try:
          post_count = self.post_iterator.count
          return post_count
      except:
          return 0


    def get_average_likes(self):
        try:
            def load(fni, path):
                if not os.path.isfile(path):
                    return None
                return FrozenNodeIterator(**json.load(open(path)))

            def save(fni, path):
                json.dump(fni._asdict(), open(path, 'w'))

            def format_path(magic):
                return f"resume_info_{magic}.json"

            with resumable_iteration(
                    context=self.ctx,
                    iterator=self.post_iterator,
                    load=load,
                    save=save,
                    format_path=format_path
            ) as (is_resuming, start_index):
                likes_count = 0
                post_count = 0
                for post in self.post_iterator:
                    if post.likes > 0:
                        likes_count += post.likes
                        post_count += 1
                        if post_count == 5:
                            break
                return likes_count / post_count if post_count > 0 else 0
        except:
            return -1

        
      