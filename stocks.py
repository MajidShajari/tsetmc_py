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


class Stocks:
    """
    get stocks data from tsetmc
    """

    def __init__(self, stocks_list: List[str] | str = "all", ):
        self._stocks_list: List[StockDataClass] = []
        if stocks_list == "all":
            self._get_all_stocks()

    def _get_all_stocks(self):
        """
        """
        async def _get_stocks():
            stocks_list = await asyncio.gather(
                get_stocks_list_from_market_watch_init_page(),
                get_stocks_list_from_symbols_list_page(),
                return_exceptions=True)
            stocks_list = set(stock for result in stocks_list if isinstance(
                result, list) for stock in result)
            self._stocks_list = await self._complete_stocks_list(stocks_list)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_get_stocks())
        loop.close()

    async def _complete_stocks_list(self, stocks_list: List[StockDataClass]):

        complete_tasks = [get_stock_with_tse_id(
            stock.current_id) for stock in stocks_list]
        _stocks_list = [result for result in await asyncio.gather(*complete_tasks, return_exceptions=True) if isinstance(result, StockDataClass)]
        if len(stocks_list) != len(_stocks_list):
            print(
                f"stocks not complete download, check logger file : {len(stocks_list)-len(_stocks_list)} Error", )
        return _stocks_list

    @property
    def to_dataclass(self) -> List[StockDataClass]:
        """
        convert to dataclass
        """
        print("convert to dataclass")
        return self._stocks_list

    @property
    def to_dict(self) -> List[Dict]:
        """
        convert to dict
        """
        print("convert to dict")
        return [stock.__dict__ for stock in self._stocks_list]

    @property
    def to_dataframe(self) -> pd.DataFrame:
        """
        convert to dataframe
        """
        print("convert to dataframe")
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
    # asyncio.run(get_stock_with_tse_id("14985138705106402"))
