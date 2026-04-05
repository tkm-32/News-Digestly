# 画面を表示するためのpythonファイル

import streamlit as st
import pandas as pd
import datetime
import html
import re

# CSVファイルを読み込む
def load_data(file_path):
    return pd.read_csv(file_path)
    
# キーワードにツールチップを付与する関数
def add_tooltip_to_word(text, keywords):
    # キーワードをツールチップ付きHTMLで置き換える
    for keyword, info in keywords.items():
        # キーワードをツールチップ形式で置き換える
        text = text.replace(
            keyword,
            f'<span class="tooltip"><strong>{keyword}</strong><span class="tooltiptext">{info}</span></span>'
        )
        
    return text   

# 次の月曜日を計算する関数
def get_next_monday(selected_date):
    days_ahead = 7 - selected_date.weekday()  # 月曜日までの日数を計算
    if days_ahead == 7:  # すでに月曜日の場合
        days_ahead = 0
    return selected_date + datetime.timedelta(days=days_ahead)

# 選択した週の開始日（月曜日）と終了日（日曜日）を計算する関数
def get_week_range(selected_date):
    start_of_week = selected_date - datetime.timedelta(days=selected_date.weekday())  # 月曜日を計算
    end_of_week = start_of_week + datetime.timedelta(days=6)  # 日曜日を計算
    return start_of_week, end_of_week

# トップ10ニュースを表示する関数
def display_top10_news(news_data, keyword_data, genre=None):
    filtered_news = news_data
    if genre and genre != "全て":
        filtered_news = news_data[news_data["ジャンル"] == genre]

    if not filtered_news.empty:
        start_of_week, end_of_week = get_week_range(selected_date)
        st.write(f"#### 【期間】 {start_of_week.strftime('%Y-%m-%d')} ～ {end_of_week.strftime('%Y-%m-%d')}")
        st.write("#### ●共起ネットワーク図")
        st.image(f"../KHCorder_images/{selected_date_str}.png")
        st.write("---")
        st.write("### ●トップ10ニュース")
        for _, row in filtered_news.iterrows():
            st.write(f"##### {int(row['ランク'])}. {row['タイトル']}")
            st.write(f"###### ジャンル: **{row['ジャンル']}**")

            news_id = str(row["ニュース番号"])
            keywords = keyword_data[keyword_data["ニュース番号"] == int(news_id)]

            keywords_dict = dict(zip(
                keywords["キーワード"], 
                keywords["説明"].apply(lambda x: html.escape(str(x)).replace("\n", "<br>"))
            ))

            processed_text = re.sub(r'<1>', '✦', row['モデル要約'])
            processed_text = re.sub(r'<[23]>', '<br>✦', processed_text)
            processed_text = add_tooltip_to_word(processed_text, keywords_dict)

            html_content = f"""
            <div style="
                border: 2px solid #81D4FA; 
                padding: 15px; 
                border-radius: 10px; 
                background-color: #E0F7FA; 
                font-size: 16px;
                line-height: 1.6;
            ">
                {processed_text}
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
            st.write(f"詳しくは[こちら]({row['URL']})")

            st.write('\n\n')
        st.write("---")
    else:
        if genre != '全て':
            st.write(f"この週で{genre}関連で話題になったニュースはありません。")
        else:
            st.write(f"選択した週のニュースはありません。")

# ツールチップの設定
tooltip_style = """
<style>
.tooltip {
  position: relative;
  display: inline-block;
  cursor: help;
}

.tooltip .tooltiptext {
  visibility: hidden;
  width: 300px; /* 幅を拡大 */
  background-color: #555;
  color: #fff;
  text-align: center;
  border-radius: 10px; /* 角を少し丸める */
  padding: 10px 15px; /* パディングを拡大 */
  font-size: 16px; /* フォントサイズを大きく */
  position: absolute;
  z-index: 1;
  bottom: 150%; /* 表示位置を調整 */
  left: 50%;
  margin-left: -150px; /* 幅に合わせて中央揃え */
  opacity: 0;
  transition: opacity 0.3s;
}

.tooltip:hover .tooltiptext {
  visibility: visible;
  opacity: 1;
}
</style>
"""

# HTMLとCSSを埋め込む
st.markdown(tooltip_style, unsafe_allow_html=True)

st.title("📰News Digestly📰") 

# データの読み込み
news_data = load_data("news.csv")
keyword_data = load_data("../keyword_extraction/keywords.csv")

with st.sidebar:
    page = st.radio("ジャンル", ["全て", "社会", "政治", "経済", "国際", "スポーツ", "エンタメ"])

# 日付選択
default_date = datetime.date.today()
selected_date = st.date_input(
    "日付を選択してください",
    default_date
)

# 選択された日付に対応するデータを取得
selected_date_monday = get_next_monday(selected_date)
selected_date_str = selected_date_monday.strftime("%Y-%m-%d")
week_news = news_data[news_data["日付"] == selected_date_str]

display_top10_news(week_news, keyword_data, genre=page)
