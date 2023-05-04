from utils import decorator
from stocks import Stocks


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
