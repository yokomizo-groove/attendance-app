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

    # Excel読込
    df = pd.read_excel(uploaded_file)

    st.subheader("アップロードデータ確認")
    st.dataframe(df.head())

    # ====== ここに計算ロジックを書く ======
    # 例：単純な合計
    result_df = df.copy()
    
    if "勤務時間" in result_df.columns:
        total_hours = result_df["勤務時間"].sum()
    else:
        total_hours = 0

    summary_df = pd.DataFrame({
        "支店": [branch],
        "処理日時": [datetime.now()],
        "合計勤務時間": [total_hours]
    })

    # ====== Excel生成 ======
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        result_df.to_excel(writer, index=False, sheet_name="集計結果")
        summary_df.to_excel(writer, index=False, sheet_name="サマリー")

    output.seek(0)

    st.subheader("集計結果サマリー")
    st.dataframe(summary_df)

    # ダウンロードボタン
    st.download_button(
        label="Excelをダウンロード",
        data=output,
        file_name=f"{branch}_集計結果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )