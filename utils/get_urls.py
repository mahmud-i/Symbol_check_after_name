import requests
import random
import xml.etree.ElementTree as ET
import pandas as pd

class GetUrls:
    def _init_(self):pass

    @staticmethod
    def get_urls_from_sitemap(sitemap_url):
        # Fetch the sitemap XML
        response = requests.get(sitemap_url)

        if response.status_code == 200:
            # Parse the XML content
            root = ET.fromstring(response.content)

            # Extract URLs from <url><loc> tags
            urls_list = [url_elem.text for url_elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
            return urls_list
        else:
            print(f"Failed to fetch sitemap: {response.status_code}")
            return []

    @staticmethod
    def get_urls_from_list():
        urls = input("Enter URLs separated by commas: ").split(',')
        urls = [url.strip() for url in urls]
        return urls

    @staticmethod
    def get_urls_from_csv():
        file_path = input("Enter your .csv file path where all urls are listed for check\n"
                          "(ex: a/b/c/df.csv) [make sure the column name as url]: ")
        try:
            df = pd.read_csv(file_path)
            if 'url' in df.columns:
                urls = df['url'].tolist()
                return urls
            else:
                raise ValueError("The CSV file does not contain a 'url' column.")

        except Exception as e:
            print(f"Error reading the CSV file: {e}")
            return []

    @staticmethod
    def sample_from_array(arr, min_items=5, max_items=8):
        # Ensure the sample size is within the array length
        sample_size = min(max_items, len(arr))

        # If there are enough elements, sample between min_items and sample_size
        if sample_size >= min_items:
            return random.sample(arr, random.randint(min_items, sample_size))
        else:
            print(f"Array contains fewer than {min_items} elements. Returning the full array.")
            return arr

    def get_random_urls_from_sitemap(self, domain_url):
        full_url_list = self.get_urls_from_sitemap(domain_url+'sitemap.xml')
        url_list = self.sample_from_array(full_url_list)
        return url_list


    def get_urls_from_others(self,prod_domain_url):
        urls = None
        def get_choice(prompt):
            response = input(prompt)
            while response not in ['1', '2', '3']:
                print("Invalid input. Please choose the right number (1,2,3)!!")
                response = input(prompt)
            return response

        method = get_choice("Choose any methods for get urls for test: \n"
                            "1. Get urls from csv file\n2. Input a list of urls for test\n"
                            "3. Use some random urls collected from the sitemap.xml\n\n"
                            "Enter your preference: ")

        if method == '1':
            urls = self.get_urls_from_csv()
        elif method == '2':
            urls = self.get_urls_from_list()
        elif method == '3':
            urls = self.get_random_urls_from_sitemap(prod_domain_url)

        return urls