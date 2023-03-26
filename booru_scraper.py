# Import necessary modules
import requests
import logging
from bs4 import BeautifulSoup
import os

# Set up logging to output info messages to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Define a class for Booru posts


class BooruPost:
    """
    Everything you'd need for a single post.
    """

    def __init__(self, post_id):
        """
        Initialize a new Booru post instance with given post ID.
        """

        # Set instance variables for post ID, URL, page HTML, and page BeautifulSoup object
        self.post_id = post_id
        self.page_url = f"http://booru.soy/post/view/{post_id}"
        self.page = requests.get(self.page_url)
        self.page_soup = BeautifulSoup(self.page.text, "html.parser")

        # Find image URL in page HTML and set as instance variable
        self.image_url = self.page_soup.find(
            "input", {"id": "text_image-src"}).get("value")

        # Extract file extension from image URL and set as instance variable
        self.file_ext = self.image_url.split(".")[-1]

    def download(self, download_directory):
        """
        Downloads the image of the post to the 'soyjaks' folder.
        """
        try:
            # Send GET request for image URL and write image data to file
            response = requests.get(self.image_url)
            soyjak_filepath = os.path.join(
                download_directory, f"Soyjak #{self.post_id}.{self.file_ext}")
            with open(soyjak_filepath, 'wb') as f:
                f.write(response.content)

            # Print success message if download is successful
            output_message = f"Downloaded #{self.post_id} from {self.page_url}!"
        except:
            # Print error message if download fails
            output_message = f'Failed to download #{self.post_id} from {self.page_url}!'
        print(output_message)


def max_online_soyjaks():
    """
    Returns the highest post number from booru.soy by finding the latest file uploaded to the catalog.
    :return: int
    """

    # Send GET request for catalog page and parse HTML with BeautifulSoup
    catalog_page_url = "http://booru.soy/post/list"
    catalog_page = requests.get(catalog_page_url)
    catalog_page_soup = BeautifulSoup(catalog_page.text, "html.parser")

    # Find list of catalog images and extract the post ID of the first (most recent) image
    catalog_image_list = catalog_page_soup.find(
        "div", {"class": "shm-image-list"})
    catalog_images = catalog_image_list.findChildren("a")
    latest_post_number = int(catalog_images[0]["data-post-id"])

    return int(latest_post_number)


def number_to_start_with(download_directory):
    """
    Returns the highest post number already downloaded, so that we don't download the same images again.
    :param download_directory: str - path to directory where soyjak files are stored
    :return: int
    """

    # Generate list of already downloaded soyjak post numbers
    if not os.path.exists(download_directory):
        os.mkdir(f'{download_directory}')
    
    downloaded_soyjak_numbers = [int(file.split("#")[1].split(
        ".")[0]) for file in os.listdir(download_directory) if "Soyjak #" in file]

    # If no soyjaks have been downloaded, start with post ID 0
    if not downloaded_soyjak_numbers:
        return 0
    else:
        # Otherwise, return the highest downloaded post number
        return max(downloaded_soyjak_numbers)


def recheck_missing_soyjaks(download_directory):
    """
    If you want to recheck all the missing soyjaks, this function will go through each downloaded soyjak and check if there are any gaps.
    """
    if not os.path.exists(download_directory):
        os.mkdir(f'{download_directory}')
    
    downloaded_soyjaks = [int(file.split("#")[1].split(".")[0])
                          for file in os.listdir(download_directory) if "#" in file]
    downloaded_soyjaks.sort()

    for i in range(len(downloaded_soyjaks)-1):
        current_post = downloaded_soyjaks[i]
        next_post = downloaded_soyjaks[i + 1]
        post_gap = int(next_post) - int(current_post) - 1

        if post_gap > 0:
            posts_to_check = list(range(current_post + 1, next_post))
            for post in posts_to_check:
                BooruPost(post).download()
