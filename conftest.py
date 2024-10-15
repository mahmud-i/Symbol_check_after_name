
import os
import pytest
from playwright.sync_api import sync_playwright
from http.client import responses
from datetime import datetime
from pages.pages_component import PageInstance # Assuming this is your custom page class

# Add command-line options for the values passed from `main.py`
def pytest_addoption(parser):
    parser.addoption("--prod_domain_url", action="store")
    parser.addoption("--headless_chk", action="store")
    parser.addoption("--url", action="append")# Append allows multiple URL entries
    parser.addoption("--brand_name", action="store")
    parser.addoption("--name_to_check", action="store")
    parser.addoption("--symbol_to_check", action="store")


def pytest_configure(config):
    brand_name = config.getoption("--brand_name")
    print('\npytest-html report generation start\n')

    # Get the current date and time
    current_time = datetime.now()

    # Format the current time as a directory name (e.g., '2024-09-25_14-30-00')
    time = current_time.strftime("%H-%M")
    date = current_time.strftime("%Y-%m-%d")

    html_report_dct = f"Report/{brand_name}_Report/{brand_name}_pytest_html_reports/test_on_{date}"
    os.makedirs(html_report_dct, exist_ok=True)
    html_report_path = os.path.join(html_report_dct, f"{time}_{brand_name}_pytest_html_report.html")

    config.option.htmlpath = html_report_path
    config.option.title = f"{brand_name} Test Report"
    config.option.description = f"Automated Test Report for {brand_name}"
    config.option.self_contained_html = True

    print(f"\nHTML report will be generated at: {html_report_path}\n")


# Fixtures for each command-line argument
@pytest.fixture(scope="session")
def prod_domain_url(request):
    return request.config.getoption("--prod_domain_url")


@pytest.fixture(scope="session")
def name_to_check(request):
    return request.config.getoption("--name_to_check")


@pytest.fixture(scope="session")
def headless_chk(request):
    return request.config.getoption("--headless_chk")

@pytest.fixture(scope="session")
def symbol_to_check(request):
    return request.config.getoption("--symbol_to_check")


@pytest.fixture(scope="session")
def urls_to_check(request):
    return request.config.getoption("--url")  # This will return the list of URLs passed as `--url`

@pytest.fixture(scope="session")
def time_t(request):
    # Get the current date and time
    current_time = datetime.now()

    # Format the current time as a directory name (e.g., '2024-09-25_14-30-00')
    time = current_time.strftime("%H_%M")
    return time

@pytest.fixture(scope="session")
def date_t(request):
    # Get the current date and time
    current_time = datetime.now()

    # Format the current time as a directory name (e.g., '2024-09-25_14-30-00')
    date = current_time.strftime("%Y-%m-%d")
    return date

def pytest_generate_tests(metafunc):
    if "url" in metafunc.fixturenames:
        # Get URLs from the fixture
        urls = metafunc.config.getoption("--url")

        if urls:
            # Dynamically parameterize the test with URLs
            metafunc.parametrize("url", urls)
        else:
            pytest.skip("No URLs provided to test")


@pytest.fixture(scope="session")
def brand_name(request):
    return request.config.getoption("--brand_name")


# Function to check if headless mode should be enabled
def check_headless(headless_chk):
    return headless_chk == 'Y'


# Fixture to start Playwright browser session (shared across tests)
@pytest.fixture(scope="session")
def browser(headless_chk):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=check_headless(headless_chk))
        yield browser
        browser.close()


# Fixture to create a reusable browser context (preserves cookies, storage state)
@pytest.fixture(scope="session")
def context(browser):
    context = browser.new_context()
    yield context


'''# Fixture for setting up a Playwright page for staging domain
@pytest.fixture(scope="session", autouse=True)
def setup_stage_page(context, stage_domain_url):
    stage_url_cred = stage_domain_url.replace('https://', 'https://kenvueuser:KenvuePassword2024!@')  # Example for auth
    page = PageInstance(context.new_page())
    page.goto(stage_url_cred)
    page.wait_for_page_load()
    page.accept_cookies('button#onetrust-accept-btn-handler')
    page.close_email_signup_popup('button.vds-self_flex-end')
    page.close_page()
'''

# Fixture for setting up a Playwright page for production domain
@pytest.fixture(scope="session", autouse=True)
def setup_prod_page(context, prod_domain_url):
    page = PageInstance(context.new_page())
    page.goto(prod_domain_url)
    page.wait_for_page_load()
    page.accept_cookies('button#onetrust-accept-btn-handler')
    page.close_email_signup_popup('button.vds-self_flex-end')
    page.close_page()

def log_response(response, url):
    status = {}
    if response.url == url:
        status_code = response.status
        status_message = responses.get(status_code, "Unknown Status")
        status['status'] = status_code
        status['message'] = status_message
        print(f"URL: {url}\nResponse: {status_code} {status_message}")
        return status


@pytest.fixture(scope="function")
def open_prod_page(context, url):
    prod_page = context.new_page()
    prod_page.on("response", lambda response: log_response(response, url))
    prod_instance = PageInstance(prod_page)
    prod_instance.goto(url)
    page_type = prod_instance.get_page_type()
    yield prod_instance, page_type
    prod_instance.close_page()

'''@pytest.fixture(scope="function")
def open_stage_page(context, url, prod_domain_url, stage_domain_url):
    stage_url = url.replace(prod_domain_url, stage_domain_url)
    stage_page = context.new_page()
    stage_page.on("response", lambda response: log_response(response, stage_url))
    stage_instance = PageInstance(stage_page)
    stage_instance.goto(stage_url)
    page_type = stage_instance.get_page_type()
    yield stage_instance, page_type
    stage_instance.close_page()
'''