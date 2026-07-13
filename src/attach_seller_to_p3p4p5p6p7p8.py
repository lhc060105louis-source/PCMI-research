#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
给 p3p4p5p6p7p8 交集结果补充 “实际 seller_id 和 seller_name”。

逻辑：
- 交集表里有 icontractid（合同 id）
- contracts.csv 里：
    iId        = 合同 id（对应 icontractid）
    iParentId  = 这份合同的实际 seller_id
- entity_sellers.csv 里：
    iId        = seller_id
    sSellerName= seller_name

输出：
- out/p3p4p5p6p7p8_claims_in_claims_with_seller.csv
- out/data.sqlite 里的表 p3p4p5p6p7p8_claims_in_claims_with_seller
"""

import sqlite3
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent          # .../src
PROJECT_ROOT = HERE.parent                      # .../vscode_python_data_starter
DATA_DIR = PROJECT_ROOT / "data"
OUT_DIR = PROJECT_ROOT / "out"

# 1) 输入：交集结果
IN_CSV = OUT_DIR / "p3p4p5p6p7p8_claims_in_claims.csv"

# 2) 输入：原始 CSV
CONTRACTS_CSV = DATA_DIR / "contracts.csv"
SELLERS_CSV   = DATA_DIR / "entity_sellers.csv"

# 3) 输出
OUT_CSV = OUT_DIR / "p3p4p5p6p7p8_claims_in_claims_with_seller.csv"
OUT_DB  = OUT_DIR / "data.sqlite"


def main() -> None:
    # ---------- 1. 读交集 CSV ----------
    print(f"Reading intersection file from: {IN_CSV}")
    nodes = pd.read_csv(IN_CSV)

    # 处理 icontractid 大小写/命名问题
    lower_map = {c.lower(): c for c in nodes.columns}
    if "icontractid" not in lower_map:
        raise ValueError(
            f"交集文件列名里找不到 icontractid（不区分大小写）。实际列：{list(nodes.columns)}"
        )
    real_contract_col = lower_map["icontractid"]
    if real_contract_col != "icontractid":
        nodes = nodes.rename(columns={real_contract_col: "icontractid"})

    # ---------- 2. 读 contracts（icontractid -> seller_id = iParentId） ----------
    print(f"Reading contracts from: {CONTRACTS_CSV}")
    contracts = pd.read_csv(CONTRACTS_CSV, low_memory=False)

    c_lower = {c.lower(): c for c in contracts.columns}
    for needed in ["iid", "iparentid"]:
        if needed not in c_lower:
            raise ValueError(
                f"contracts.csv 中找不到列 {needed}（不区分大小写）。实际列：{list(contracts.columns)}"
            )

    contracts_small = contracts[
        [c_lower["iid"], c_lower["iparentid"]]
    ].rename(
        columns={
            c_lower["iid"]: "icontractid",
            c_lower["iparentid"]: "seller_id",
        }
    )

    # ---------- 3. 读 entity_sellers（seller_id -> seller_name） ----------
    print(f"Reading entity_sellers from: {SELLERS_CSV}")
    sellers = pd.read_csv(SELLERS_CSV, low_memory=False)

    s_lower = {c.lower(): c for c in sellers.columns}
    for needed in ["iid", "ssellername"]:
        if needed not in s_lower:
            raise ValueError(
                f"entity_sellers.csv 中找不到列 {needed}。实际列：{list(sellers.columns)}"
            )

    sellers_small = sellers[
        [s_lower["iid"], s_lower["ssellername"]]
    ].rename(
        columns={
            s_lower["iid"]: "seller_id",
            s_lower["ssellername"]: "seller_name",
        }
    )

    # ---------- 4. 逐步 merge：claim -> contract -> seller ----------
    print("Merging contracts (icontractid -> seller_id via iParentId)...")
    df = nodes.merge(contracts_small, on="icontractid", how="left")

    print("Merging entity_sellers (seller_id -> seller_name)...")
    df = df.merge(sellers_small, on="seller_id", how="left")

    # 只保留：原始列 + seller_id + seller_name
    keep_cols = list(nodes.columns) + ["seller_id", "seller_name"]
    df = df[keep_cols]

    # 简单检查
    col_claim_id = next(c for c in df.columns if c.lower() in ("iid", "claim_id", "sclaimid"))
    print(f"交集 claims 行数: {len(nodes)}")
    print(f"合并后行数: {len(df)}")
    print(f"唯一 claim 数量: {df[col_claim_id].nunique()}")
    print(f"唯一 seller_id 数量: {df['seller_id'].nunique()}")

    # ---------- 5. 写新的 CSV ----------
    print(f"Writing updated CSV with seller info to: {OUT_CSV}")
    df.to_csv(OUT_CSV, index=False)

    # ---------- 6. 写进 out/data.sqlite ----------
    print(f"Writing to SQLite DB: {OUT_DB}")
    con_out = sqlite3.connect(OUT_DB)
    df.to_sql(
        "p3p4p5p6p7p8_claims_in_claims_with_seller",
        con_out,
        if_exists="replace",
        index=False
    )
    con_out.close()

    print("Done! 每条 claim 已配上实际 seller_id 和 seller_name。")


if __name__ == "__main__":
    main()
