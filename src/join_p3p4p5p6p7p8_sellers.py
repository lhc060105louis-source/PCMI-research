#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 out/p3p4p5p6p7p8_claims_in_claims.csv 和
out/p3p4p5p6p7p8_claims_in_claims_with_seller.csv 生成一张 115 行的表，
为每条 claim(iid) 汇总所有 seller_id 和 seller_name（逗号分隔）。
"""

from pathlib import Path
import pandas as pd

# 这个文件在 src/ 下面，parents[1] 就是项目根目录 vscode_python_data_starter
BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "out"

F_CLAIMS = OUT / "p3p4p5p6p7p8_claims_in_claims.csv"
F_WITH_SELLER = OUT / "p3p4p5p6p7p8_claims_in_claims_with_seller.csv"
F_OUT = OUT / "p3p4p5p6p7p8_claims_in_claims_115_with_sellers.csv"


def main() -> None:
    print(">>> join_p3p4p5p6p7p8_sellers 开始运行")
    print("项目根目录:", BASE)

    # 1. 读入数据
    print("读取:", F_CLAIMS)
    claims = pd.read_csv(F_CLAIMS)

    print("读取:", F_WITH_SELLER)
    with_seller = pd.read_csv(F_WITH_SELLER, low_memory=False)

    # 2. 只保留与 seller 相关的列，并去重
    tmp = (
        with_seller[["iid", "seller_id", "seller_name"]]
        .dropna(subset=["seller_id"])
        .drop_duplicates()
        .sort_values(["iid", "seller_id"])
    )

    # 3. 对每个 iid 聚合 seller_id / seller_name（逗号分隔）
    seller_agg = (
        tmp.groupby("iid")
        .agg(
            seller_ids=(
                "seller_id",
                lambda x: ",".join(str(int(v)) for v in x if pd.notna(v)),
            ),
            seller_names=(
                "seller_name",
                lambda x: ",".join(map(str, x)),
            ),
        )
        .reset_index()
    )

    # 4. 回并到 115 条 claim 表
    merged = claims.merge(seller_agg, on="iid", how="left")

    # 5. 简单 sanity check
    print(f"claims 行数: {len(claims)}")
    print(f"合并后行数: {len(merged)}")
    print(
        "唯一 iid 数量: "
        f"claims={claims['iid'].nunique()}, "
        f"with_seller={with_seller['iid'].nunique()}, "
        f"agg={seller_agg['iid'].nunique()}"
    )

    # 6. 写出结果
    merged.to_csv(F_OUT, index=False)
    print("写出文件:", F_OUT)
    print(">>> join_p3p4p5p6p7p8_sellers 完成")


if __name__ == "__main__":
    main()
