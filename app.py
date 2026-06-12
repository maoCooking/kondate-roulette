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
    "カレー",
    "親子丼",
    "焼きそば",
    "パスタ",
    "麻婆豆腐",
    "オムライス",
    "ハンバーグ",
    "生姜焼き",
    "チャーハン",
    "豚丼",
    "うどん",
    "そば",
    "鍋",
    "そうめん",
    "冷やし中華",
    "おでん",
    "シチュー",


    # ===== 簡単系 =====
    "簡単ご飯系（卵かけ・納豆）",
    "お茶漬け",
    "おかゆ（雑炊）",
    "パン料理（トースト系・サンドイッチ・ホットサンド）",
    "冷奴",
    "冷凍チャーハン",
    "レトルトカレー",

    # ===== 冷凍おかず系 =====
    "冷凍唐揚げ",
    "冷凍餃子",
    "冷凍シュウマイ",

    # ===== ヘルシー系 =====
    "もやし炒め",
    "豆腐ステーキ",
    "キャベツ炒め",
    "味噌汁＋おにぎり"
]

# 季節ロジックの前に置く
current_temp = get_temperature()

# ==============================
# 季節による鍋の確率調整
# ==============================
def seasonal_weight(item, temp):
    month = datetime.datetime.now().month
    weight = 1.0

    # 温かい料理グループ
    hot_dishes = ["鍋", "おでん", "シチュー"]

    # 冷たい料理グループ
    cold_dishes = ["冷やし中華", "そうめん"]

    # --- 気温ロジック ---
    if temp is not None:

        # 30℃以上 → 温かい料理ほぼ出ない、冷たい料理UP
        if temp >= 30:
            if item in hot_dishes:
                weight *= 0.2
            if item in cold_dishes:
                weight *= 1.5

        # 15℃以上 → 冷やし中華UP
        elif temp >= 15:
            if item in cold_dishes:
                weight *= 1.2

        # 10℃以下 → 温かい料理UP、冷たい料理DOWN
        elif temp <= 10:
            if item in hot_dishes:
                weight *= 1.5
            if item in cold_dishes:
                weight *= 0.6

    # --- 既存の季節ロジック（気温と併用） ---
    if item == "鍋":
        weight *= 0.3 if 6 <= month <= 9 else 1.0

    if item == "冷やし中華":
        weight *= 1.2 if 6 <= month <= 9 else 0.6

    if item == "そうめん":
        weight *= 1.3 if 6 <= month <= 9 else 0.8

    return weight

# ==============================
# 再抽選に上限をつけた抽選関数
# ==============================
def pick_menu(menu_list, temp, exclude_item=None):
    weights = [seasonal_weight(item, temp) for item in menu_list]

    # 最大10回まで再抽選
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
        if item == excluded:
            weights.append(0)
        elif item in [
            "簡単ご飯系（卵かけ・納豆）",
            "お茶漬け",
            "おかゆ（雑炊）",
            "パン料理（トースト系・サンドイッチ・ホットサンド）",
            "豆腐ステーキ",
            "冷凍チャーハン",
            "レトルトカレー",
            "冷凍唐揚げ",
            "冷凍餃子",
            "冷凍シュウマイ"
        ]:
            weights.append(2.0 * seasonal_weight(item, temp))
        else:
            weights.append(1.0 * seasonal_weight(item, temp))

    return random.choices(menu_list, weights=weights, k=1)[0]

# ==============================
# カスタムCSS（再抽選ボタンのみ修正）
# ==============================
st.markdown("""

<style>

/* ==============================
   メインボタン
============================== */

button[kind="primary"] {
    background: linear-gradient(
        135deg,
        #ff7bb8,
        #ff3f8e
    ) !important;

    border-radius: 18px !important;

    height: 4.2em !important;

    border: none !important;

    box-shadow:
        0 6px 16px rgba(
            255,
            80,
            150,
            0.55
        ) !important;

    transition: 0.25s !important;
}

button[kind="primary"] p {
    color: white !important;
    font-size: 1.8rem !important;
    font-weight: 900 !important;
    letter-spacing: 1px;
}

button[kind="primary"]:hover {
    background: linear-gradient(
        135deg,
        #ff3f8e,
        #ff1f6e
    ) !important;

    transform: scale(1.05);
}

/* ==============================
   再抽選ボタン
============================== */

button[kind="secondary"] {
    background: linear-gradient(
        135deg,
        #dff5ff,
        #bfe9ff
    ) !important;

    border-radius: 14px !important;

    height: 3.2em !important;

    border: 1px solid #b7e7ff !important;

    box-shadow: none !important;

    transition: 0.25s !important;
}

button[kind="secondary"] p {
    color: #4a6a84 !important;

    font-size: 1.15rem !important;

    font-weight: 600 !important;

    letter-spacing: 0.3px !important;
}

button[kind="secondary"]:hover {
    background: linear-gradient(
        135deg,
        #cdefff,
        #a9e2ff
    ) !important;

    transform: scale(1.02);
}

/* ==============================
   結果表示
============================== */

.result-box {
    font-size: 1.8rem;
    font-weight: 900;
    padding: 1.2em;
    border-radius: 12px;
    border: 3px solid #4CAF50;
    background-color: rgba(
        76,
        175,
        80,
        0.15
    );
    text-align: center;
    margin-top: 1.4em;
    margin-bottom: 1.4em;
    animation: fadeIn 0.8s ease-out;
}

/* ==============================
   行間
============================== */

.reroll-space {
    margin-top: 1.4em;
    margin-bottom: 1.4em;
}

/* ==============================
   アニメーション
============================== */

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

</style>

""", unsafe_allow_html=True)


# ==============================
# メインボタン処理
# ==============================
if "result" not in st.session_state:
    st.session_state.result = None

if st.button(
    "今日の献立を決める！",
    type="primary"
):
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

    # ===== 行間スペース =====
    st.markdown('<div class="reroll-space"></div>', unsafe_allow_html=True)

    # ===== 再抽選ボタン（水色） =====
    reroll = st.button(
        "やっぱ違うにゃ😺…もう一回！🎯",
        key="reroll",
        type="secondary"
    )

    if reroll:
        st.session_state.result = reroll_menu(result, current_temp)
        st.rerun()

    # ==============================
    # レシピ検索リンク（ここは if の中に入れる）
    # ==============================
    encoded = urllib.parse.quote(result)
    st.write("レシピ検索はこちら👇")

    col1, col2 = st.columns(2)

    with col1:
        url_ryuji = f"https://www.youtube.com/results?search_query={encoded}+リュウジ"
        st.link_button("リュウジのバズレシピ", url_ryuji)

    with col2:
    url_macaroni = f"https://www.youtube.com/@macaroni_recipe/search?query={encoded}"
    st.markdown(
        f'<a href="{url_macaroni}" target="_blank" '
        'style="display:block; padding:0.7em 1em; background:#f0f0f0; '
        'border-radius:10px; text-align:center; text-decoration:none; '
        'font-weight:600; color:#333;">macaroni | マカロニ</a>',
        unsafe_allow_html=True
    )


else:
    st.info("まだルーレットは回っていません。")