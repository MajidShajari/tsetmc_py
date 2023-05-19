
TSETMC_SEARCH_WITH_SYMBOL = (
    "http://www.tsetmc.com/tsev2/data/search.aspx?skey={}")

# returns list of all symbols
SYMBOLS_LIST_URL = "http://www.tsetmc.com/Loader.aspx?ParTree=111C1417"

# market watch init, has initial data for market watch like symbols name etc.
MARKET_WATCH_INIT_URL = (
    "http://www.tsetmc.com/tsev2/data/MarketWatchInit.aspx?h=0&r=0"
)

TSETMC_MAIN_URL = "http://www.tsetmc.com/Loader.aspx?ParTree=15"
# stock page url
TSETMC_STOCK_URL = "http://tsetmc.com/Loader.aspx?ParTree=151311&i={}"
# historical price between two dates
TSETMC_PRICE_UPDATE_URL = (
    "http://www.tsetmc.com/tse/data/Export-txt.aspx?a=InsTrade&InsCode={}" +
    "&DateFrom={}&DateTo={}&b=0")
