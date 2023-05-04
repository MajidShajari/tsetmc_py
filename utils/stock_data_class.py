import locale
from typing import List
from dataclasses import dataclass, field


@dataclass
class StockDataClass:
    current_id: str
    symbol: str = ""
    name: str = ""
    instrument_id: str = ""
    ci_sin: str = ""
    old_ids: List[str] = field(default_factory=list)
    full_title: str = ""
    industry_id: str = ""
    industry_name: str = ""
    volume: str = ""
    base_volume: str = "1"
    flow: str = ""

    def __post_init__(self):
        self.name = self.name.replace("  ", " ")
        self.name = self.name.replace('\u200c', ' ')

    def __hash__(self):
        """Hash function is used for deduplication"""
        return hash(self.symbol)

    def __lt__(self, other):
        return not locale.strcoll(other.symbol, self.symbol) < 0

    def __eq__(self, other):
        return locale.strcoll(other.symbol, self.symbol) == 0
