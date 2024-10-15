import re
import os
import json
from playwright.sync_api import Page



class PageInstance:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, url):
        self.page.goto(url)

    @staticmethod
    def safe_get_attribute(element, attribute_name):
        try:
            value = element.get_attribute(attribute_name)
            if value:
                # Encode the value to handle any special characters
                return value.encode('utf-8').decode('utf-8')
            return None
        except Exception as e:
            print(f"Error getting attribute '{attribute_name}': {e}")
            return None


    def wait_for_page_load(self):
        try:
            self.page.wait_for_load_state('networkidle')
        except Exception as e:
            return f"error: {e}"

    def wait_for_time(self, timeout):
        try:
            self.page.wait_for_timeout(timeout)
        except Exception as e:
            return f"error: {e}"

    def accept_cookies(self, cookie_selector):
        try:
            self.page.locator(cookie_selector).click()
            print("Accepted cookies")
        except Exception as e:
            print(f"Could not find or click cookie button: {e}")

    def close_email_signup_popup(self, popup_selector):
        try:
            self.page.locator(popup_selector).click()
            print("Closed email signup popup")
        except Exception as e:
            print(f"Could not find or close the email signup popup: {e}")

    def close_page(self):
        self.page.close()

    def get_page_type(self):
        try:
            self.wait_for_page_load()
            locator = self.page.locator("head script")
            count = locator.count()
            cc_element = None

            for i in range(count):
                element = locator.nth(i)

                # Get the text content of the current script element
                sc_content = element.text_content()

                # Check if 'careClubConfig' is in the script content
                if "page_type" in sc_content:
                    cc_element = element
                    break

            if cc_element:
                script_content = cc_element.text_content()

                data_layer_main_str = script_content.split('window[\'dataLayer\'] = window[\'dataLayer\'] || [];')[1]
                data_layer_push = data_layer_main_str.split('window[\'dataLayer\'].push(')
                data_layer = None

                for i in range(len(data_layer_push)):
                    data_layer_str = data_layer_push[i].split(");")[0]
                    if "page_type" in data_layer_str:
                        data_layer = json.loads(data_layer_str)
                        break

                if data_layer:
                    page_data = data_layer.get("page_data", {})
                    page_type = page_data.get("page_type", None)
                    return page_type
                else:
                    print("\n\n Page_type not found\n\n")
                    return None
        except Exception as e:
            print(f"Error processing: {e}")


    def expand_list(self):
        try:
            while True:
                self.wait_for_time(1000)
                # Check if the "See Less" button is visible
                see_less_visible = self.page.is_visible('button:has-text("SEE LESS")')

                if see_less_visible:
                    print('See Less button is visible. Stopping load more clicks.')
                    break

                # Check if the "Load More" button is visible and click it
                load_more_visible = self.page.is_visible('button:has-text("LOAD MORE")')
                if load_more_visible:
                    self.page.click('button:has-text("LOAD MORE")')
                    print('Clicked Load More button.')
                else:
                    print('Load More button is not visible anymore.')
                    break
        except Exception as e:
            print(f"Error processing: {e}")

    def expand_accordion(self):
        try:
            main = self.page.query_selector('main')
            accordion_button = main.query_selector_all('button.focusVisible\\:vds-ring_components\\.accordion\\.border\\.focus')
            if accordion_button is None:
                print('No accordion found')
            for buttons in accordion_button:
                aria_expanded = self.safe_get_attribute(buttons, 'aria-expanded')
                data_state = self.safe_get_attribute(buttons, 'data-state')
                if aria_expanded == "false" and data_state == "closed":
                    print('accordion found')
                    buttons.click()

        except Exception as e:
            print(f"Error processing: {e}")


    def meta_content_check(self, name_to_check, symbol):
        try:
            report_data = []
            meta_tags = self.page.query_selector_all("meta")
            print(f"Total meta tags found: {len(meta_tags)}")
            for meta in meta_tags:
                content = self.safe_get_attribute(meta, "content")
                meta_name = self.safe_get_attribute(meta, "name") or self.safe_get_attribute(meta,"property")
                if content:
                    if name_to_check in content and f"{name_to_check}{symbol}" not in content and f"{name_to_check}<sup>{symbol}</sup>" not in content:
                        print(f"Found {name_to_check} in meta content without {symbol}")
                        report_data.append({
                            "Name Check": name_to_check,
                            "Meta Content": content,
                            "Meta Name": meta_name
                        })
            title = self.page.title()
            if title:
                if name_to_check in title and f"{name_to_check}{symbol}" not in title and f"{name_to_check}<sup>{symbol}</sup>" not in title:
                    print(f"Found {name_to_check} in title without {symbol}")
                    report_data.append({
                        "Meta Content": title,
                        "Meta Name/Property": "title"
                    })
            return report_data
        except Exception as e:
            print(f"Error processing: {e}")


    def brand_symbol_check(self, name_to_check, symbol):
        try:
            self.wait_for_page_load()
            report_data = []
            content = self.page.content()
            page_content = self.page.evaluate("""
            () => {
                let mainContent = document.querySelector('main').cloneNode(true);

                // Remove specific sections (e.g., review section)
                let review = mainContent.querySelector('section#reviews');
                if (review) review.remove();
        
                // Remove all <script>, <style>, and other non-visual elements
                let scripts = mainContent.querySelectorAll('script, style, noscript');
                scripts.forEach(script => script.remove());
        
                // Return only the visible inner text
                return mainContent.innerText;
            }
        """)

            print(f"Page content length: {len(page_content)}\n")

            # Regular expression to find brand without ® symbol (case-insensitive)
            pattern = rf"{name_to_check}(?!\s*(<sup>{symbol}</sup>|{symbol}))"
            matches = re.finditer(pattern, page_content, re.IGNORECASE)

            match_count = 0

            # Log the matches where the symbol is missing
            for match in matches:
                match_count += 1
                print(f"Found {name_to_check} at position {match.start()} without {symbol}")

                element = self.page.query_selector(f"text={match.group(0)}")
                if element:
                    tag_name = element.evaluate("(element) => element.tagName")
                else:
                    tag_name = "Unknown"
                    print(f"Could not find an element for {match.group(0)}")

                report_data.append({
                    "Tag Name": tag_name,
                    "Missing Position": match.start(),
                    "Surrounding Text": page_content[match.start() - 20:match.end() + 20]
                })
            print(f"Total matches found for {name_to_check}{symbol}: {match_count}")
            return report_data
        except Exception as e:
            print(f"Error processing: {e}")