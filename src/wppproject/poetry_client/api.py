from functools import wraps
import time
import requests
from typeguard import typechecked

class PoetryDB:
    def __init__(self , url = "https://poetrydb.org"):
        self.base_url = url

    def timer(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f"Time taken: {round(end - start, 2)}s for {func.__name__}.")
            return result
        return wrapper


    @typechecked
    def _get(self, path: str):
        """Internal method to perform a GET request."""
        response = requests.get(f"{self.base_url}/{path}").json()

        if 'status' in response:
            if response['status'] == 404:
                raise ValueError("Poem not found.")

        if isinstance(response, list) or isinstance(response, dict):
            return response
        
        raise TypeError("Unexpected response type.")

    @typechecked
    def get_poems_by_author(self, author: str):
        """Get poems by a specific author."""
        return self._get(f"author/{author}")

    @typechecked
    def get_poems_by_title(self, title: str):
        """Get poems by title."""
        return self._get(f"title/{title}")

    @typechecked
    def get_poem_lines_by_title(self, title: str):
        """Get the lines of a poem by its title."""
        return self._get(f"title/{title}/lines.json")

    @timer
    def get_random_poems(self, count=1, min_lines=None, max_lines=None, author=None):
        """Get a specified number of random poems, optionally filtering by line length.""" 
        for _ in range(5):
            poems = self._get(f"random/{count*10}")  # Fetch more poems to increase chances of matching criteria
            filtered_poems = []

            for poem in poems:
                if min_lines or max_lines:
                    line_count = int(poem.get('linecount', 0))
                    if min_lines and line_count < min_lines:
                        continue
                    if max_lines and line_count > max_lines:
                        continue
                filtered_poems.append(poem)
                if len(filtered_poems) == count:  # Stop when desired count is reached
                    break
            if len(filtered_poems) >= count:
                return filtered_poems[:count]  # Return up to 'count' poems
        raise ValueError("No poems found matching criteria.")