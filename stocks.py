import asyncio
from typing import List, Dict, Union
import pandas as pd

from tsetmc_scrape import (
    get_stocks_list_from_market_watch_init_page,
    get_stocks_list_from_stocks_list_page,
    get_stock_with_tse_id,
    get_stock_ids_with_symbol
)
from utils import (
    StockDataClass,
)


class Stocks:
    """
    get stocks data from tsetmc
    """

    def __init__(self):
        self._stocks_list: List[StockDataClass] = []

    def _get_all_stocks(self):
        """
        """
        async def _get_stocks():
            stocks_list = await asyncio.gather(
                get_stocks_list_from_market_watch_init_page(),
                get_stocks_list_from_stocks_list_page(),
                return_exceptions=True)
            stocks_list = set(stock for result in stocks_list if isinstance(
                result, list) for stock in result)
            self._stocks_list = await self._complete_stocks_list(list(stocks_list))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_get_stocks())
        loop.close()

    def _get_many_stocks(self, symbols):
        """
        """
        async def _get_stocks():
            self._stocks_list = await self._complete_ids_list(list(list_ids))
        list_ids = []
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        for symbol in symbols:
            if not symbol.isnumeric():
                current_id, _ = loop.run_until_complete(
                    get_stock_ids_with_symbol(symbol))
                list_ids.append(current_id)
                continue
            list_ids.append(symbol)
        loop.run_until_complete(_get_stocks())
        loop.close()

    async def _complete_ids_list(self, list_ids: List):
        complete_tasks = [get_stock_with_tse_id(tse_id) for tse_id in list_ids]
        _stocks_list = [result for result in await asyncio.gather(*complete_tasks, return_exceptions=True) if isinstance(result, StockDataClass)]
        if len(list_ids) != len(_stocks_list):
            print(
                f"stocks not complete download, check logger file : {len(list_ids)-len(_stocks_list)} Error", )
        return _stocks_list

    async def _complete_stocks_list(self, stocks_list: List[StockDataClass]):

        complete_tasks = [get_stock_with_tse_id(
            stock.current_id) for stock in stocks_list]
        _stocks_list = [result for result in await asyncio.gather(*complete_tasks, return_exceptions=True) if isinstance(result, StockDataClass)]
        if len(stocks_list) != len(_stocks_list):
            print(
                f"stocks not complete download, check logger file : {len(stocks_list)-len(_stocks_list)} Error", )
        return _stocks_list

    def get_all(self):
        self._get_all_stocks()

    def get_many(self, symbols: Union[List, str]):
        if isinstance(symbols, str):
            symbols = [symbols]
        self._get_many_stocks(symbols)

    @property
    def to_dataclass(self) -> List[StockDataClass]:
        """
        convert to dataclass
        """
        print("convert to dataclass")
        if len(self._stocks_list) == 0:
            raise ValueError("Nothing Exist")
        return self._stocks_list

    @property
    def to_dict(self) -> List[Dict]:
        """
        convert to dict
        """
        print("convert to dict")
        return [stock.__dict__ for stock in self.to_dataclass]

    @property
    def to_dataframe(self) -> pd.DataFrame:
        """
        convert to dataframe
        """
        print("convert to dataframe")
        return pd.DataFrame(self.to_dict).set_index('current_id')
