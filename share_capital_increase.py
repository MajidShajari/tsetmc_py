import logging
import asyncio
import time
import pandas as pd

from utils import (
    custom_logger,
    convert_jalaali_to_gregorian,
    convert_to_jalali_date
)
from tsetmc_scrape import get_share_capital_increase_html, translations

logger = logging.getLogger(__name__)
logger.addHandler(custom_logger.MyStreamHandler())


def get_increase_data() -> pd.DataFrame:
    logger.info("get increase data")
    increase_df = pd.DataFrame()
    increase_df = asyncio.run(get_share_capital_increase_html())
    increase_df = increase_df.rename(
        columns=translations.SHARE_CAPITAL_INCREASE)
    _adjust_dataframe(increase_df)
    return increase_df


def _adjust_dataframe(dataframe: pd.DataFrame):
    dataframe['jdate'] = dataframe['jdate'].apply(convert_to_jalali_date)
    dataframe['date'] = dataframe["jdate"].map(convert_jalaali_to_gregorian)
    dataframe = dataframe.sort_values(by='date')


if __name__ == "__main__":
    tic = time.perf_counter()
    get_increase_data().to_excel("share_capital_increase.xlsx")
    toc = time.perf_counter()
    print(f"Excution in {toc-tic:4.2f} seconds")
