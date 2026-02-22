import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="勤怠集計アプリ", layout="centered")

st.title("勤怠データ集計アプリ")

# 支店選択
branch = st.selectbox(
    "支店を選択してください",
    ["本社", "支店A", "支店B", "支店C", "支店D", "支店E"]
)

# ファイルアップロード
uploaded_file = st.file_uploader(
    "勤怠データ（Excel）をアップロードしてください",
    type=["xlsx"]
)

if uploaded_file is not None:

    st.success("ファイルを読み込みました")

    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    st.subheader("アップロードデータ確認")
    st.dataframe(df.head())

    # ====== 勤務時間集計ロジック ======
    result_df = df.copy()
    total_minutes = 0

    if "勤務時間" in result_df.columns:

        col = result_df["勤務時間"]

        # --- 数値型（830形式など） ---
        if pd.api.types.is_numeric_dtype(col):

            hours = col // 100
            minutes = col % 100

            total_minutes = (hours * 60 + minutes).sum()

        else:
            # --- 文字列や時刻形式 ---
            parsed = pd.to_datetime(col, errors="coerce")

            total_minutes = (
                parsed.dt.hour.fillna(0) * 60 +
                parsed.dt.minute.fillna(0)
            ).sum()

    # 分 → 時:分 表示
    total_h = int(total_minutes // 60)
    total_m = int(total_minutes % 60)

    total_display = f"{total_h}:{total_m:02d}"

    summary_df = pd.DataFrame({
        "支店": [branch],
        "処理日時": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "合計勤務時間": [total_display]
    })

    # ====== Excel生成 ======
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        result_df.to_excel(writer, index=False, sheet_name="集計結果")
        summary_df.to_excel(writer, index=False, sheet_name="サマリー")

    output.seek(0)

    st.subheader("集計結果サマリー")
    st.dataframe(summary_df)

    st.download_button(
        label="Excelをダウンロード",
        data=output,
        file_name=f"{branch}_集計結果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
