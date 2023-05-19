from typing import List, Tuple
import pandas as pd
from utils import (
    convert_to_number_if_number
)


def get_html_table_header_and_rows(
    table
) -> Tuple[List, List]:
    """
    return header and rows from a html table as a list
    """
    header = []
    rows = []
    table_header = table.find("tr")
    table_rows = table.find_all("tr")[1:]
    for items in table_header:
        if items.get_text() != "\n":
            header.append(items.get_text())
    for table_row in table_rows:
        row = []
        for cell in table_row.findAll(['th', 'td']):
            row.append(cell)
        rows.append(row)

    return header, rows


def convert_html_table_to_dataframe(table) -> pd.DataFrame:
    """
    given table element from shareholders page returns DatFrame
    Containing the table
    """
    header, rows = get_html_table_header_and_rows(table)
    df_rows = []

    for row in rows:
        df_row = []
        for cell in row:
            cell_div = cell.find("div")
            if cell_div and cell_div.get_text() != "":
                df_row.append(convert_to_number_if_number(cell_div["title"]))
            else:
                df_row.append(
                    convert_to_number_if_number(cell.get_text().strip())
                )
        df_rows.append(df_row)
    return pd.DataFrame(data=df_rows, columns=header)
