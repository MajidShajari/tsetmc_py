
import re
from typing import Dict, List, Tuple, Union

import pandas as pd
from bs4 import BeautifulSoup, PageElement

from tsetmc_scrape import scrape_url
from tsetmc_scrape.async_request import get_request
from utils import StockDataClass, custom_logger, replace_arabic
from .table_scraper import (
    get_html_table_header_and_rows,
    convert_html_table_to_dateframe
)

_logger = custom_logger.main_logger


async def get_stock_with_tse_id(tse_id: str) -> Union[StockDataClass, Tuple]:
    _logger.debug("scraping stock with tse id : %s", tse_id)
    url = scrape_url.TSETMC_STOCK_URL.format(tse_id)
    _stock = StockDataClass(current_id=tse_id)
    try:
        response = await get_request(url, timeout=60)
        assert response is not None
        symbol = replace_arabic(re.findall(
            r"LVal18AFC='([\w\s]*)',", response)[0])
        if symbol == "',DEven='',LSecVal='',CgrValCot='',Flow='',InstrumentID='":
            raise Exception(f"{tse_id}not found")
        _stock.symbol = symbol

        _stock.name = replace_arabic(re.findall(
            r"Title='(.*?)',", response)[0].split("-")[0].split("(")[0])

        _stock.full_title = replace_arabic(re.findall(
            r"Title='(.*?)',", response)[0].split("-")[0])

        _stock.instrument_id = re.findall(
            r"InstrumentID='([\w\d]*)|',$", response)[0]

        _stock.ci_sin = re.findall(r"CIsin='([\w\d]*)|',$", response)[0]

        _stock.industry_id = re.findall(r"CSecVal='([\w\d]*)|$',", response)[0]

        _stock.industry_name = replace_arabic(
            re.findall(r"LSecVal='([\D]*)',", response)[0])

        _stock.volume = re.findall(r"ZTitad=([-,\d]*),", response)[0]

        _stock.base_volume = re.findall(r"BaseVol=([-,\d]*),", response)[0]

        _stock.flow = re.findall(r"Flow='(.*?)'", response)[0]

        _, _stock.old_ids = await get_stock_ids_with_symbol(symbol)

        _logger.debug("scraped stock with tse id : %s", tse_id)
    except AssertionError:
        return (tse_id, "Server not respond")
    except Exception as error:
        _logger.debug("scraping stock with this error: %s", error)
        return (tse_id, f"{error}")
    return _stock


async def get_stock_ids_with_symbol(stock_symbol: str):
    """
    get stock ids from tse symbol search page
    """
    _logger.debug("scraping stock ids with symbol : %s", stock_symbol.encode())
    url = scrape_url.TSETMC_SEARCH_WITH_SYMBOL.format(stock_symbol.strip())
    response = await get_request(url)
    assert response is not None
    symbols = response.split(';')
    current_id = None
    old_ids = []
    for symbol_full_info in symbols:
        if symbol_full_info.strip() == "":
            continue
        symbol_full_info = symbol_full_info.split(',')
        if replace_arabic(symbol_full_info[0]) == stock_symbol:
            if symbol_full_info[7] == '1':
                current_id = symbol_full_info[2]  # active stock id
            else:
                old_ids.append(symbol_full_info[2])  # old stock id
    _logger.debug("scraped stock ids with symbol : %s", stock_symbol.encode())
    return current_id, old_ids


# logger config
_logger = custom_logger.main_logger


async def get_stocks_list_from_symbols_list_page() -> List[StockDataClass]:
    """
    uses SYMBOLS_LIST_URL and scrapes stocks information from the page
    :return: list of all stocks
    :rtype: List[StockDataClass]
    """
    _logger.info("scraping stocks information from symbols list page")
    stocks_list = []
    url = scrape_url.SYMBOLS_LIST_URL
    response = await get_request(url)
    assert response is not None
    soup = BeautifulSoup(response, 'html.parser')
    table = soup.find("table")
    if not isinstance(table, PageElement):
        return stocks_list
    _, table_rows = get_html_table_header_and_rows(table)
    for row_data in table_rows:
        # escape old symbols
        if row_data[7].a.text.startswith('حذف-'):
            continue
        if row_data[6].a.text.isdigit():
            continue
        stocks_list.append(
            StockDataClass(
                instrument_id=row_data[0].text,
                symbol=replace_arabic(row_data[6].a.text),
                name=replace_arabic(row_data[7].a.text).replace('\u200c', ' '),
                current_id=row_data[6].a.get('href').partition('inscode=')[2],
            )
        )
    _logger.info("scraped stocks information from symbols list page")
    return stocks_list


async def get_stocks_list_from_market_watch_init_page() -> List[StockDataClass] | Dict:
    """
    get stocks information from market watch page
    :return: list of stock
    :rtype: List[StockDataClass]
    """
    _logger.info("scraping stocks information from market watch page")
    stocks_list = []
    url = scrape_url.MARKET_WATCH_INIT_URL
    response = await get_request(url)
    assert response is not None, "error"
    response_groups = response.split("@")
    if len(response_groups) < 3:
        _logger.error(
            "stocks information from market watch page is not valid",
            extra={"response": response}
        )
        return stocks_list
    symbols_data = response_groups[2].split(";")
    for symbol_data in symbols_data:
        data = symbol_data.split(",")
        # if symbol name ends with number it's some kind of symbol
        # like 'اختیار خرید و فروش،اوراق مشارکت،امتیاز تسهیلات' and we don't want it
        symbol_name_ends_with_number = re.search(r'\d+$', data[2])
        if symbol_name_ends_with_number:
            continue
        if "گواهی" in replace_arabic(data[3]).replace('\u200c', ''):
            # if name contains 'گواهی' it's some kind of symbol
            # like 'گواهی شیشه' and we don't want it
            continue
        if data[2].isdigit():
            # if symbol name is number it's some kind of symbol
            continue
        stocks_list.append(
            StockDataClass(
                instrument_id=replace_arabic(data[1]),
                symbol=replace_arabic(data[2]),
                current_id=replace_arabic(data[0]),
                name=replace_arabic(data[3]).replace('\u200c', ' '),
            )
        )
    _logger.info("scraped stocks information from market watch page")
    return stocks_list


async def get_share_capital_increase_html() -> pd.DataFrame:
    _logger.debug("scraping share capital increase html")
    url = scrape_url.TSETMC_MAIN_URL
    response = await get_request(url)
    assert response is not None
    soup = BeautifulSoup(response, 'html.parser')
    divs_node = soup.find_all("div", text=re.compile("افزایش سرمایه"))
    tables = [div_node.parent.find("table") for div_node in divs_node]
    all_df = pd.DataFrame()
    for table in tables:
        table_dfs = convert_html_table_to_dateframe(table)
        all_df = pd.concat([all_df, table_dfs])
    all_df = all_df.reset_index(drop=True)
    _logger.debug("scraped share capital increase html")
    return all_df
