# main.py

import sys
import pytest
from utils.get_urls import GetUrls


# Function to dynamically create command-line options for pytest
def run_tests(urls_to_check, prod_domain_url, headless_chk, brand_name, name_to_check, symbol_to_check):
    # Create the base pytest arguments
    pytest_args = [
        "--prod_domain_url=" + prod_domain_url,
        "--headless_chk=" + headless_chk,
        "--brand_name=" + brand_name,
        "--name_to_check=" + name_to_check,
        "--symbol_to_check=" + symbol_to_check
    ]

    # Add more configurations or custom test markers if needed
    for url in urls_to_check:
        pytest_args.append("--url=" + url)

    # Run pytest programmatically with the arguments
    return pytest.main(pytest_args)


# Main entry point
if __name__ == "__main__":

    # Example values for running tests (these could come from config files or user input)
    prod_domain_url = input("Please write the PROD site Domain Link: ")

    name_to_check = input("Enter Names to check: ")
    symbol_to_check = input("Enter symbol to check: ")

    def get_input(prompt):
        response = input(prompt).strip().upper()
        while response not in ['Y', 'N']:
            print("Invalid input. Please choose the right key (Y/N).")
            response = input(prompt).strip().upper()
        return response

    headless_chk = get_input("Do you want to run the test in Headless mode? (Y/N): ")
    urls_parse= get_input("Want to run test on all urls from sitemap.xml? (Y/N) [for No, just input list of Urls you want to test]: ")

    brand_name = prod_domain_url.replace('https://www.', '').split('.')[0].strip().upper()

    urls_list = GetUrls()

    if urls_parse == 'Y':
        urls_to_check = urls_list.get_urls_from_sitemap(prod_domain_url+'sitemap.xml') # List of URLs to test
    else:
        urls_to_check = urls_list.get_urls_from_others(prod_domain_url)



    # Running the test suite
    exit_code = run_tests(urls_to_check, prod_domain_url, headless_chk, brand_name, name_to_check, symbol_to_check)
    sys.exit(exit_code)