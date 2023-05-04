import asyncio
from typing import List, Dict
import pandas as pd

from tsetmc_scrape import (
    get_stocks_list_from_market_watch_init_page,
    get_stocks_list_from_symbols_list_page,
    get_stock_with_tse_id
)
from utils import (
    custom_logger,
    StockDataClass,
    decorator
)

_logger = custom_logger.main_logger


class Stocks:
    """
    get stocks data from tsetmc
    """

    def __init__(self, stocks_list: List[str] | str = "all", ):
        self._stocks_list: List[StockDataClass] = []
        self._logger = _logger
        self._event_loop = asyncio.get_event_loop()
        if stocks_list == "all":
            self._event_loop.run_until_complete(self._get_all_stocks())
        self._event_loop.close()

    async def _get_all_stocks(self):
        """
        """
        stocks_list = await asyncio.gather(
            get_stocks_list_from_market_watch_init_page(),
            get_stocks_list_from_symbols_list_page(),
            return_exceptions=True)
        stocks_list = set(stock for result in stocks_list if isinstance(
            result, list) for stock in result)
        self._stocks_list = await self._complete_stocks_list(stocks_list)

    async def _complete_stocks_list(self, stocks_list: List[StockDataClass]):

        complete_tasks = [get_stock_with_tse_id(
            stock.current_id) for stock in stocks_list]
        stocks_list = [result for result in await asyncio.gather(*complete_tasks, return_exceptions=True) if isinstance(result, StockDataClass)]
        if len(stocks_list) != len(stocks_list):
            self._logger.info('stocks not complete download, check logger file %s', len(
                stocks_list)-len(stocks_list))
        return stocks_list

    @property
    def to_dataclass(self) -> List[StockDataClass]:
        """
        convert to dataclass
        """
        self._logger.info("convert to dataclass")
        return self._stocks_list

    @property
    def to_dict(self) -> List[Dict]:
        """
        convert to dict
        """
        self._logger.info("convert to dict")
        return [stock.__dict__ for stock in self._stocks_list]

    @property
    def to_dataframe(self) -> pd.DataFrame:
        """
        convert to dataframe
        """
        self._logger.info("convert to dataframe")
        return pd.DataFrame(self.to_dict).set_index('current_id')


@decorator.timeit
def main():
    """
    main
    """
    # print(asyncio.run(get_stock_with_tse_id("12660940572636629")))
    stocks_list = Stocks()
    stocks_list.to_dataframe.to_excel("symbols.xlsx")


if __name__ == "__main__":
    main()