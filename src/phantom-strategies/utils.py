import time
from typing import Generator
from collections import OrderedDict
from pathlib import Path

import pandas as pd


def get_data(table: str | None) -> pd.DataFrame:
    if table is None:
        raise ValueError("table cannot be None")
    return pd.read_feather(Path(__file__).resolve().parents[2] / "db" / f"{table}.feather")


def concat_items(df: pd.DataFrame, item: pd.Series, iterations: int) -> str:
    result = item["content"]

    for i in range(iterations):
        result += " "

        mask = df["sentence"] == item["sentence"] + i
        row = df.loc[mask].iloc[0]
        result += row["content"]

    return result


def fake_stream(sentence: str) -> Generator[str, None, None]:
    for word in sentence.split(" "):
        yield word + " "
        time.sleep(0.05)


def get_base_model(model_id: str) -> str:
    return model_id.split(":")[1]


def write_roman(num):

    roman = OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, y = divmod(num, r)
            yield roman[r] * x
            num -= r * x
            if num <= 0:
                break

    return "".join([a for a in roman_num(num)])
