import random
import urllib.parse
import time
import datetime
import streamlit as st
import requests

def get_temperature():
    """
    東京の現在気温（℃）を取得する関数
    APIキー不要・無料
    """
    url = "https://api.open-meteo.com/v1/forecast?latitude=35.6895&longitude=139.6917&current_weather=true&timezone=Asia/Tokyo"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        temp = data["current_weather"]["temperature"]
        return temp
    except:
        return None  # 取得失敗時は None を返す


# ==============================
# ページ設定
# ==============================
st.set_page_config(
    page_title="献立ルーレット",
    page_icon="🍚"
)

# ==============================
# タイトル
# ==============================
st.title("🍚 今日の献立ルーレット🎰")
st.write("ボタンを押すと今日の献立を決めます。")

# ==============================
# 料理リスト（最新版）
# ==============================
menu_list = [
    # ===== メイン料理 =====
    "カレー", "親子丼", "焼きそば", "パスタ",
    "麻婆豆腐", "オムライス", "ハンバーグ",
    "生姜焼き", "チャーハン", "豚丼",
    "うどん", "そば", "鍋", "そうめん",
    "おでん", "シチュー", "豚キムチ",
    "焼き魚", "魚のホイル焼き", "魚のムニエル",
    "なす味噌炒め", "もやし炒め",
    "キャベツと豚肉の炒め物",
    "南蛮漬け", "チキン南蛮",
    "牛丼", "甘酢あん炒め",
    "ピーマンの肉詰め", "青椒肉絲",
    "しゃぶしゃぶ", "豆腐料理",

    # ===== 麺類（夏向け） =====
    "冷やし中華",
    "冷やしうどん",
    "冷製パスタ",
    "冷やし担々麺",
    "ざるそば",
    "ぶっかけうどん",
    "冷しゃぶ麺",
    "そうめん・ひやむぎ",

    # ===== 簡単系 =====
    "簡単ご飯系（卵かけ・納豆）",
    "お茶漬け・雑炊系",
    "味噌汁＋おにぎり",
    "パン料理（トースト系・サンドイッチ・ホットサンド）",
    "冷奴",
    "冷凍チャーハン",
    "レトルトカレー",
    "カップ麺",
    "冷凍レンチン料理"
]

# ==============================
# メイン料理リスト（新規追加）
# ==============================
main_dishes = [
    "カレー", "親子丼", "焼きそば", "パスタ",
    "麻婆豆腐", "オムライス", "ハンバーグ",
    "生姜焼き", "チャーハン", "豚丼",
    "うどん", "そば", "鍋", "そうめん",
    "おでん", "シチュー", "豚キムチ",
    "焼き魚", "魚のホイル焼き", "魚のムニエル",
    "なす味噌炒め", "もやし炒め",
    "キャベツと豚肉の炒め物",
    "南蛮漬け", "チキン南蛮",
    "牛丼", "甘酢あん炒め",
    "ピーマンの肉詰め", "青椒肉絲",
    "しゃぶしゃぶ", "豆腐料理"
]

# ==============================
# 簡単系リスト（新規追加）
# ==============================
easy_dishes = [
    "簡単ご飯系（卵かけ・納豆）",
    "お茶漬け・雑炊系",
    "味噌汁＋おにぎり",
    "パン料理（トースト系・サンドイッチ・ホットサンド）",
    "冷奴",
    "冷凍チャーハン",
    "レトルトカレー",
    "カップ麺",
    "冷凍レンチン料理"
]

# 季節ロジックの前に置く
current_temp = get_temperature()

# ==============================
# 季節による鍋の確率調整
# ==============================
def seasonal_weight(item, temp):
    month = datetime.datetime.now().month
    weight = 1.0

    # 夏向け麺類（冷たい麺カテゴリ）
    summer_cold_noodles = [
        "冷やし中華",
        "冷やしうどん",
        "冷製パスタ",
        "冷やし担々麺",
        "ざるそば",
        "ぶっかけうどん",
        "冷しゃぶ麺",
        "そうめん・ひやむぎ"
    ]

    # 冬に強い料理
    hot_dishes = ["鍋", "おでん", "シチュー"]

    # 気温ロジック
    if temp is not None:
        if temp >= 30:
            if item in hot_dishes:
                weight *= 0.2
            if item in summer_cold_noodles:
                weight *= 1.5
        elif temp >= 15:
            if item in summer_cold_noodles:
                weight *= 1.2
        elif temp <= 10:
            if item in hot_dishes:
                weight *= 1.5
            if item in summer_cold_noodles:
                weight *= 0.6

    # 月ロジック（夏向け麺類）
    if item in summer_cold_noodles:
        weight *= 1.3 if 6 <= month <= 9 else 0.7

    # メイン料理の「そうめん」は別扱い（にゅうめん需要）
    if item == "そうめん":
        weight *= 1.15 if 6 <= month <= 9 else 0.9

    return weight

# ==============================
# 再抽選に上限をつけた抽選関数
# ==============================
def pick_menu(menu_list, temp, exclude_item=None):
    weights = [seasonal_weight(item, temp) for item in menu_list]

    for _ in range(10):
        result = random.choices(menu_list, weights=weights, k=1)[0]
        if exclude_item is not None and result == exclude_item:
            continue
        return result

    return random.choice(menu_list)


# ==============================
# 再抽選ロジック（除外＋簡単系UP）
# ==============================
def reroll_menu(excluded, temp):
    weights = []

    for item in menu_list:
        # 前回の料理は除外
        if item == excluded:
            weights.append(0)
            continue

        # 季節ロジックを適用
        weight = seasonal_weight(item, temp)

        # 簡単系は 1.5倍
        if item in easy_dishes:
            weight *= 1.5

        # メイン料理は 1.2倍
        if item in main_dishes:
            weight *= 1.2

        weights.append(weight)

    return random.choices(menu_list, weights=weights, k=1)[0]

# ==============================
# カスタムCSS
# ==============================
st.markdown("""
<style>
button[kind="primary"] {
    background: linear-gradient(135deg, #ff7bb8, #ff3f8e) !important;
    border-radius: 18px !important;
    height: 4.2em !important;
    border: none !important;
    box-shadow: 0 6px 16px rgba(255, 80, 150, 0.55) !important;
    transition: 0.25s !important;
}
button[kind="primary"] p {
    color: white !important;
    font-size: 1.8rem !important;
    font-weight: 900 !important;
    letter-spacing: 1px;
}
button[kind="primary"]:hover {
    background: linear-gradient(135deg, #ff3f8e, #ff1f6e) !important;
    transform: scale(1.05);
}

button[kind="secondary"] {
    background: linear-gradient(135deg, #dff5ff, #bfe9ff) !important;
    border-radius: 14px !important;
    height: 3.2em !important;
    border: 1px solid #b7e7ff !important;
    transition: 0.25s !important;
}
button[kind="secondary"] p {
    color: #4a6a84 !important;
    font-size: 1.15rem !important;
    font-weight: 600 !important;
}
button[kind="secondary"]:hover {
    background: linear-gradient(135deg, #cdefff, #a9e2ff) !important;
    transform: scale(1.02);
}

.result-box {
    font-size: 1.8rem;
    font-weight: 900;
    padding: 1.2em;
    border-radius: 12px;
    border: 3px solid #4CAF50;
    background-color: rgba(76, 175, 80, 0.15);
    text-align: center;
    margin-top: 1.4em;
    margin-bottom: 1.4em;
    animation: fadeIn 0.8s ease-out;
}

.reroll-space {
    margin-top: 1.4em;
    margin-bottom: 1.4em;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)


# ==============================
# メインボタン処理
# ==============================
if "result" not in st.session_state:
    st.session_state.result = None

if st.button("今日の献立を決める！", type="primary"):
    st.balloons()
    time.sleep(1.5)
    st.session_state.result = pick_menu(menu_list, current_temp)


# ==============================
# 結果表示
# ==============================
if st.session_state.result:
    result = st.session_state.result

    st.markdown(
        f'<div class="result-box">今日の献立は… {result} です！</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="reroll-space"></div>', unsafe_allow_html=True)

    reroll = st.button(
        "やっぱ違うにゃ😺…もう一回！🎯",
        key="reroll",
        type="secondary"
    )

    if reroll:
        st.session_state.result = reroll_menu(result, current_temp)
        st.rerun()

    # ==============================
    # レシピ検索リンク（スマホ対応）
    # ==============================
    encoded = urllib.parse.quote(result)
    st.write("レシピ検索はこちら👇")

    col1, col2 = st.columns(2)

    # リュウジ（通常検索で安定）
    with col1:
        url_ryuji = f"https://www.youtube.com/results?search_query={encoded}+リュウジ"
        st.markdown(
            f'<a href="{url_ryuji}" target="_blank" '
            'style="display:block; padding:0.7em 1em; background:#f0f0f0; '
            'border-radius:10px; text-align:center; text-decoration:none; '
            'font-weight:600; color:#333;">リュウジのバズレシピ</a>',
            unsafe_allow_html=True
        )

    # macaroni（チャンネル内検索＋HTMLで安定）
    with col2:
        url_macaroni = f"https://www.youtube.com/results?search_query={encoded}+macaroni+レシピ"
        st.markdown(
            f'<a href="{url_macaroni}" target="_blank" '
            'style="display:block; padding:0.7em 1em; background:#f0f0f0; '
            'border-radius:10px; text-align:center; text-decoration:none; '
            'font-weight:600; color:#333;">macaroni | マカロニ</a>',
            unsafe_allow_html=True
        )

else:
    st.info("まだルーレットは回っていません。")
