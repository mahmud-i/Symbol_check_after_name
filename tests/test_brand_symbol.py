
import os
import pytest
import pandas as pd
from urllib.parse import urlparse
from utils.report_styling import DataFrameStyler


prod_data = []


def get_slug_from_url(url):
    parsed_url = urlparse(url)
    return parsed_url.path.lstrip('/')


def test_brand_symbol(open_prod_page, url, prod_domain_url, name_to_check, symbol_to_check):
    try:
        slug = get_slug_from_url(url)
        prod_instance, page_type = open_prod_page
        if page_type in ['productListing', 'articleListing']:
            prod_instance.expand_list()
        prod_instance.expand_accordion()
        page_symbol_check = prod_instance.brand_symbol_check(name_to_check, symbol_to_check)
        meta_symbol_check = prod_instance.meta_content_check(name_to_check, symbol_to_check)
        prod_instance.close_page()
        print(f"missing Symbol data:\n{meta_symbol_check}\n{page_symbol_check}\n")

        for val in meta_symbol_check :
            row = {
                'URL': url,
                'Page Slug': slug,
                'Check Data': name_to_check+symbol_to_check,
                'section': "Meta Content",
                'Tag/Attribute': val['Meta Name'],
                'Position': None,
                'Surrounding text': val['Meta Content']
            }
            prod_data.append(row)

        for val in page_symbol_check:
            row = {
                'URL': url,
                'Page Slug': slug,
                'Check Data': name_to_check + symbol_to_check,
                'section': "Body Content",
                'Tag/Attribute': val['Tag Name'],
                'Position': val['Missing Position'],
                'Surrounding text': val['Surrounding Text']
            }
            prod_data.append(row)

        assert len(page_symbol_check) > 0, f"No {name_to_check} found on page data of {url} without {symbol_to_check}"
        assert len(meta_symbol_check) > 0, f"No {name_to_check} found on meta data of {url} without {symbol_to_check}"
    except Exception as e:
        print(f"Error processing {url}: {e}")



@pytest.fixture(scope='session', autouse=True)
def generate_report(brand_name, date_t, time_t, name_to_check, symbol_to_check):
    yield
    test_name = f"{name_to_check}{symbol_to_check}_missing_data"
    # After all tests run, generate the report
    df_prod_data = pd.DataFrame(prod_data)

    base_dc = f"Report/{brand_name}_Report/test_on_{date_t}/{time_t}/{brand_name}_{test_name}_Report"

    excel_report_dct = f"{base_dc}/{brand_name}_{test_name}_excel_Report"
    os.makedirs(excel_report_dct, exist_ok=True)
    print('Excel report generation start\n')
    with pd.ExcelWriter(f"{excel_report_dct}/{brand_name}_symbol_check_test_report.xlsx") as writer:
        df_prod_data.to_excel(writer, sheet_name=f"prod_data", index=False)

    html_report_dc = f"{base_dc}/{brand_name}_{test_name}_html_general_Report"
    os.makedirs(html_report_dc, exist_ok=True)
    print('HTML report generation start\n')

    style_report_dct = f"{base_dc}/{brand_name}_{test_name}Style_HTML_Report"
    os.makedirs(style_report_dct, exist_ok=True)

    if not df_prod_data.empty:
        df_prod_data.to_html(f"{html_report_dc}/{brand_name}_prod_{test_name}_Report.html", index=False)

        print('PROD Data HTML report styling and update start\n')
        styler_production = DataFrameStyler(df_prod_data)
        styler_production.apply_styling_report()
        styler_production.generate_style_report(f"{style_report_dct}/{brand_name}_prod_{test_name}_Report.html")

    else:
        print(f"No {test_name} is found. Skipping HTML report generation.")

    print(f"All data checking and Report creation is done for {brand_name}_{test_name}_at_{base_dc}.\n\n")