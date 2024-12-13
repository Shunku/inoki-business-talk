import streamlit as st
import requests
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional

###################
# 定数の定義
###################

# 場所のデータ構造
LOCATIONS = {
    "北海道": ["札幌市", "旭川市", "函館市", "釧路市", "帯広市", "北見市"],
    "東京都": [
        "千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", 
        "墨田区", "江東区", "品川区", "目黑区", "大田区", "世田谷区",
        "渋谷区", "中野区", "杉並区", "豊島区", "北区", "荒川区",
        "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区"
    ],
    "神奈川県": ["横浜市", "川崎市", "相模原市", "横須賀市", "藤沢市", "茅ヶ崎市"],
    "埼玉県": ["さいたま市", "川越市", "川口市", "所沢市", "越谷市", "草加市"],
    "千葉県": ["千葉市", "市川市", "船橋市", "松戸市", "柏市", "浦安市"],
    "大阪府": ["大阪市", "堺市", "豊中市", "吹田市", "高槻市", "茨木市"],
    "京都府": ["京都市", "宇治市", "亀岡市"],
    "兵庫県": ["神戸市", "姫路市", "西宮市", "尼崎市", "明石市"],
    "愛知県": ["名古屋市", "豊橋市", "岡崎市", "一宮市", "豊田市"],
    "福岡県": ["福岡市", "北九州市", "久留米市", "春日市"]
}

# 業種のデータ構造
INDUSTRIES = {
    "製造業": [
        "自動車・輸送機器", "電機・電子機器", "機械・産業機器",
        "化学・素材", "食品・飲料", "医薬品・医療機器",
        "繊維・アパレル", "金属・鉄鋼", "印刷・包装"
    ],
    "広告業": [
        "総合広告代理店", "メディアレップ", "クリエイティブエージェンシー",
        "デジタル広告代理店", "PR・広報代理店", "OOH広告",
        "ブランディング", "マーケティングリサーチ", "プロモーション"
    ],
    "情報通信業": [
        "ソフトウェア・情報サービス", "通信キャリア", "インターネットサービス",
        "デジタルメディア", "クラウドサービス", "システムインテグレーション"
    ],
    "小売業": [
        "総合小売", "専門店", "コンビニエンスストア",
        "ドラッグストア", "家電量販店", "eコマース"
    ],
    "金融業": [
        "銀行", "証券", "保険", "クレジットカード",
        "消費者金融", "フィンテック", "資産運用"
    ],
    "不動産業": [
        "不動産開発", "不動産賃貸", "不動産売買",
        "ビル管理", "住宅メーカー", "不動産仲介"
    ],
    "建設業": [
        "総合建設", "住宅建設", "土木", "設備工事",
        "内装工事", "建設コンサルタント"
    ],
    "運輸・物流業": [
        "陸運", "海運", "航空", "倉庫・物流",
        "宅配", "フォワーダー"
    ],
    "エネルギー": [
        "電力", "ガス", "石油", "再生可能エネルギー",
        "省エネルギー", "蓄電"
    ],
    "サービス業": [
        "人材サービス", "広告・マーケティング", "コンサルティング",
        "警備・清掃", "介護・福祉", "教育", "外食・フードサービス"
    ],
    "医療・ヘルスケア": [
        "病院・医療機関", "調剤薬局", "介護施設",
        "健康機器・用品", "医療情報サービス"
    ]
}

# 地域コード（天気予報用）
CITY_CODES = {
    "札幌市": "016010",
    "旭川市": "012010",
    "函館市": "017010",
    "千代田区": "130010",
    "中央区": "130010",
    "港区": "130010",
    "新宿区": "130010",
    "渋谷区": "130010",
    "品川区": "130010",
    "横浜市": "140010",
    "川崎市": "140010",
    "さいたま市": "110010",
    "千葉市": "120010",
    "名古屋市": "230010",
    "大阪市": "270000",
    "神戸市": "280010",
    "京都市": "260010",
    "福岡市": "400010",
    "北九州市": "401000"
}

###################
# Weather API 関連の実装
###################

def get_weather_info(city: str, target_date: date) -> Dict:
    """指定された地域と日付の天気予報を取得"""
    try:
        # 地域コードの取得
        city_code = CITY_CODES.get(city)
        if not city_code:
            raise ValueError(f"未対応の地域です: {city}")

        # 日付に応じた処理
        days_ahead = (target_date - date.today()).days
        if days_ahead < 0:
            return {
                "temperature_text": "過去の日付です",
                "description": "過去の天気情報は取得できません",
                "telop": "不明",
                "image_url": None,
                "is_reference": False,
                "days_ahead": None
            }
        elif days_ahead > 7:
            return {
                "temperature_text": "予報準備中",
                "description": "7日以上先の天気予報はまだ準備できていません",
                "telop": "予報準備中",
                "image_url": None,
                "is_reference": True,
                "days_ahead": days_ahead
            }

        # API呼び出し
        url = f"https://weather.tsukumijima.net/api/forecast/city/{city_code}"
        response = requests.get(url)
        response.raise_for_status()
        
        # JSONデータの取得
        weather_data = response.json()
        
        # 予報日のインデックスを決定（0:今日, 1:明日, 2:明後日）
        forecast_index = min(days_ahead, len(weather_data["forecasts"])-1)
        target_forecast = weather_data["forecasts"][forecast_index]
        
        # 気温の取得
        temp_max = target_forecast["temperature"]["max"]["celsius"] if target_forecast["temperature"]["max"] else None
        temp_min = target_forecast["temperature"]["min"]["celsius"] if target_forecast["temperature"]["min"] else None
        
        # 気温テキストの作成
        temp_text = ""
        if temp_max and temp_min:
            temp_text = f"気温: {temp_min}℃ ～ {temp_max}℃"
        elif temp_max:
            temp_text = f"最高気温: {temp_max}℃"
        elif temp_min:
            temp_text = f"最低気温: {temp_min}℃"
        else:
            temp_text = "気温データなし"

        # 予報の信頼度を設定
        is_reference = days_ahead > 2  # 3日以上先は参考値とする

        return {
            "temperature_text": temp_text,
            "description": weather_data["description"]["text"],
            "telop": target_forecast["telop"],
            "image_url": target_forecast["image"]["url"],
            "is_reference": is_reference,
            "days_ahead": days_ahead
        }

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return {
            "temperature_text": "データなし",
            "description": "天気情報を取得できませんでした",
            "telop": "不明",
            "image_url": None,
            "is_reference": False,
            "days_ahead": None
        }

###################
# OpenAI API 関連の実装
###################

def generate_inoki_message(
    company_name: str, 
    industry_category: str,
    industry_detail: str,
    city: str, 
    weather_info: dict, 
    company_news: list, 
    industry_news: list
) -> str:
    """OpenAI APIを使用して猪木風メッセージを生成"""
    try:
        from openai import OpenAI
        
        # クライアントの初期化
        client = OpenAI(api_key=st.secrets["api_keys"]["openai_api"])
        
        # ニュースの整形
        news_text = ""
        if company_news:
            news_text += f"\n企業ニュース:\n" + "\n".join([f"- {news['title']}" for news in company_news[:3]])
        if industry_news:
            news_text += f"\n業界ニュース:\n" + "\n".join([f"- {news['title']}" for news in industry_news[:3]])

        # システムプロンプトの作成
        system_prompt = """あなたはプロレスラーのアントニオ猪木として話します。以下の特徴を持つメッセージを生成してください：

話し方の特徴：
- リズム感のある短いフレーズ
- 「ですます」調を基調としつつ熱血的
- 闘魂や元気を感じさせるフレーズを自然に挿入
- ビジネスに適した丁寧さを維持"""

        # ユーザープロンプトの作成
        prompt = f"""以下の情報を元に、猪木風のビジネス挨拶メッセージを生成してください。

基本情報:
- 会社名: {company_name}
- 業界: {industry_category}（{industry_detail}）
- 場所: {city}
- 天気: {weather_info['telop']} ({weather_info['temperature_text']})
{news_text}

### メッセージの要件
1. 「元気ですかー！ 元気があれば何でもできる。」からスタート。
1. 次に天気に触れた前向きな挨拶
2. 業界の現状や御社の取り組みへの共感
3. 企業ニュースに対するコメント（3件）
4. 業界ニュースの展望（3件）
5. 最後に「それでは本日も張り切って参りましょう。123ダー！」で締める

### フレーズ例
- 「燃える闘魂を感じました！」
- 「この調子で、元気いっぱいで参りましょう！」
- 「闘魂注入！」"""

        # ChatGPT APIの呼び出し
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            temperature=0.8
        )
        
        return response.choices[0].message.content

    except Exception as e:
        st.error(f"メッセージ生成エラー: {str(e)}")
        # エラー時のフォールバックメッセージ
        return f"""
        元気があれば何でもできる！本日はありがとうございます！{city}の天気は{weather_info['telop']}、気温は{weather_info['temperature_text']}です。

        御社の取り組みには、燃える闘魂を感じております！特に{industry_category}業界における{industry_detail}の挑戦に敬意を表します。

        それでは本日も張り切って参りましょう。123ダー！
        """

###################
# News API 関連の実装
###################

def get_company_news(company_name: str) -> List[Dict]:
    """会社名でニュースを検索"""
    base_url = "https://newsapi.org/v2/everything"
    api_key = st.secrets["api_keys"]["news_api"]
    
    params = {
        "q": company_name,
        "language": "jp",
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": api_key
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        news_data = response.json()
        
        if news_data["status"] == "ok" and news_data["articles"]:
            articles = news_data["articles"]
            
            # NGワードリスト
            ng_words = ["ちょいブス", "エ□", "まとめ", "2ch", "アフィリエイト", "まとめサイト", "速報"]
            
            # 記事の評価とフィルタリング
            scored_articles = []
            for article in articles:
                title_lower = article["title"].lower()
                desc_lower = article["description"].lower() if article["description"] else ""
                company_lower = company_name.lower()
                
                # NGワードチェック
                if any(ng_word.lower() in title_lower for ng_word in ng_words):
                    continue
                
                # スコア計算
                score = 0
                
                # タイトルに会社名が含まれる
                if company_lower in title_lower:
                    score += 5
                
                # 説明文に会社名が含まれる
                if company_lower in desc_lower:
                    score += 3
                
                # 新しい記事ほど高スコア
                days_old = (datetime.now() - datetime.strptime(article["publishedAt"][:10], "%Y-%m-%d")).days
                score += max(0, 2 - (days_old * 0.1))
                
                # ドメインスコアの追加
                domain = article["url"].lower()
                if any(d in domain for d in ["nikkei.com", "reuters.com", "bloomberg.", "nhk.or.jp"]):
                    score *= 1.5
                elif any(d in domain for d in ["itmedia.co.jp", "techcrunch.com", "businessinsider.jp"]):
                    score *= 1.3
                
                if score >= 3:  # 最小スコアのしきい値
                    scored_articles.append({
                        "title": article["title"],
                        "description": article["description"],
                        "url": article["url"],
                        "published_at": article["publishedAt"],
                        "relevance_score": score
                    })
            
            # スコアで降順ソートして上位3件を返す
            return sorted(scored_articles, key=lambda x: x["relevance_score"], reverse=True)[:3]

    except Exception as e:
        st.error(f"企業ニュース取得エラー: {str(e)}")
        return []
    
    return []

def get_industry_news(industry_category: str, industry_detail: str) -> List[Dict]:
    """業界のニュースを検索"""
    base_url = "https://newsapi.org/v2/everything"
    api_key = st.secrets["api_keys"]["news_api"]
    
    # NGワードリスト
    ng_words = ["ちょいブス", "エ□", "まとめ", "2ch", "アフィリエイト", "まとめサイト", "速報"]
    
    # 業界特有の検索キーワード
    category_keywords = {
        "製造業": ["製造", "メーカー", "工場"],
        "情報通信業": ["IT", "情報通信", "テクノロジー"],
        "小売業": ["小売", "販売", "店舗"],
        "金融業": ["金融", "銀行", "投資"],
        "不動産業": ["不動産", "住宅", "建物"],
        "建設業": ["建設", "工事", "施工"],
        "運輸・物流業": ["物流", "運送", "輸送"],
        "エネルギー": ["エネルギー", "電力", "発電"],
        "サービス業": ["サービス", "顧客"],
        "医療・ヘルスケア": ["医療", "健康", "病院"],
        "広告業": ["広告", "宣伝", "CM", "マーケティング", "プロモーション", "PR"]
    }
    
    detail_keywords = {
        "自動車・輸送機器": ["自動車", "車", "EV", "電気自動車"],
        "電機・電子機器": ["電機", "電子", "家電"],
        "ソフトウェア・情報サービス": ["ソフトウェア", "アプリ", "システム", "IT"],
        "通信キャリア": ["通信", "携帯", "モバイル"],
        "インターネットサービス": ["インターネット", "オンライン", "デジタル"],
        "総合広告代理店": ["広告代理店", "電通", "博報堂", "ADK"],
        "メディアレップ": ["メディアレップ", "媒体社", "広告配信"],
        "クリエイティブエージェンシー": ["クリエイティブ", "広告制作", "デザイン"],
        "デジタル広告代理店": ["デジタル広告", "ネット広告", "オンライン広告"],
        "PR・広報代理店": ["PR", "広報", "パブリシティ"],
        "OOH広告": ["屋外広告", "交通広告", "デジタルサイネージ"],
        "ブランディング": ["ブランド", "企業ブランド", "ブランドイメージ"],
        "マーケティングリサーチ": ["市場調査", "消費者調査", "マーケティング調査"],
        "プロモーション": ["販促", "キャンペーン", "イベント"]
    }
    
    # 検索キーワードの準備
    search_terms = []
    # カテゴリーのキーワードを追加
    search_terms.extend(category_keywords.get(industry_category, [industry_category]))
    # 詳細業種のキーワードを追加
    search_terms.extend(detail_keywords.get(industry_detail, [industry_detail]))
    
    # 重複を除去してクエリを構築
    search_terms = list(set(search_terms))
    search_query = " OR ".join(search_terms)

    params = {
        "q": search_query,
        "language": "jp",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": api_key
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        news_data = response.json()
        
        if news_data["status"] == "ok" and news_data["articles"]:
            articles = news_data["articles"]
            scored_articles = []
            
            for article in articles:
                title_lower = article["title"].lower()
                desc_lower = article["description"].lower() if article["description"] else ""
                
                # NGワードチェック
                if any(ng_word.lower() in title_lower for ng_word in ng_words):
                    continue
                
                # スコア計算
                score = 0
                
                # キーワードとの関連性チェック
                for term in search_terms:
                    if term.lower() in title_lower:
                        score += 2
                    if term.lower() in desc_lower:
                        score += 1
                
                # ドメインスコアの追加
                domain = article["url"].lower()
                if any(d in domain for d in ["nikkei.com", "reuters.com", "bloomberg.", "nhk.or.jp"]):
                    score *= 1.5
                elif any(d in domain for d in ["itmedia.co.jp", "techcrunch.com", "businessinsider.jp"]):
                    score *= 1.3
                
                # 新しさによるスコア
                days_old = (datetime.now() - datetime.strptime(article["publishedAt"][:10], "%Y-%m-%d")).days
                score += max(0, 2 - (days_old * 0.1))
                
                if score >= 2:  # スコアの閾値を下げる
                    scored_articles.append({
                        "title": article["title"],
                        "description": article["description"],
                        "url": article["url"],
                        "published_at": article["publishedAt"],
                        "relevance_score": score
                    })
            
            # スコアで降順ソートして上位3件を返す
            return sorted(scored_articles, key=lambda x: x["relevance_score"], reverse=True)[:3]

    except Exception as e:
        st.error(f"業界ニュース取得エラー: {str(e)}")
        return []

    return []

###################
# UI コンポーネント
###################

def location_selector(form_key=""):
    """場所選択のUI"""
    # キーの定義
    pref_key = f'prefecture{form_key}'
    city_key = f'city{form_key}'
    
    # 都道府県が変更された時のコールバック
    def on_prefecture_change():
        pref = st.session_state[pref_key]
        st.session_state[city_key] = LOCATIONS[pref][0]
    
    # 都道府県選択
    prefecture = st.selectbox(
        "都道府県 🗾",
        options=list(LOCATIONS.keys()),
        key=pref_key,
        on_change=on_prefecture_change
    )
    
    # 市区町村選択
    city = st.selectbox(
        "市区町村 📍",
        options=LOCATIONS[prefecture],
        key=city_key
    )
    
    return prefecture, city

def industry_selector(form_key=""):
    """業種選択のUI"""
    # キーの定義
    cat_key = f'industry_category{form_key}'
    detail_key = f'industry_detail{form_key}'
    
    # 業種カテゴリーが変更された時のコールバック
    def on_category_change():
        cat = st.session_state[cat_key]
        st.session_state[detail_key] = INDUSTRIES[cat][0]
    
    # 業種カテゴリー選択
    industry_category = st.selectbox(
        "業種カテゴリー 🏭",
        options=list(INDUSTRIES.keys()),
        key=cat_key,
        on_change=on_category_change
    )
    
    # 詳細業種選択
    industry_detail = st.selectbox(
        "詳細業種 🔍",
        options=INDUSTRIES[industry_category],
        key=detail_key
    )
    
    return industry_category, industry_detail

def display_news_section(company_name: str, industry_category: str, industry_detail: str):
    """ニュース表示セクション"""
    tabs = st.tabs(["🏢 企業ニュース", "📈 業界ニュース"])
    
    with tabs[0]:
        company_news = get_company_news(company_name)
        if company_news:
            for news in company_news:
                with st.container():
                    st.markdown(f"""
                    <div class="news-card">
                        <h4>{news['title']}</h4>
                        <p>{news['description']}</p>
                        <small>関連度: {news['relevance_score']:.1f} | 
                        公開日: {datetime.strptime(news['published_at'][:10], '%Y-%m-%d').strftime('%Y年%m月%d日')}</small><br>
                        <a href="{news['url']}" target="_blank">詳細を読む ↗</a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(f"{company_name}に関する最新ニュースは見つかりませんでした")

    with tabs[1]:
        industry_news = get_industry_news(industry_category, industry_detail)
        if industry_news:
            for news in industry_news:
                with st.container():
                    st.markdown(f"""
                    <div class="news-card">
                        <h4>{news['title']}</h4>
                        <p>{news['description']}</p>
                        <small>関連度: {news['relevance_score']:.1f} | 
                        公開日: {datetime.strptime(news['published_at'][:10], '%Y-%m-%d').strftime('%Y年%m月%d日')}</small><br>
                        <a href="{news['url']}" target="_blank">詳細を読む ↗</a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(f"{industry_category}（{industry_detail}）の最新ニュースは見つかりませんでした")
    
    return company_news, industry_news

def display_weather_card(weather_info: dict, location: str):
    """天気情報の表示"""
    with st.container():
        st.markdown(f"### 🌤️ {location}の天気")
        if weather_info["is_reference"]:
            st.warning("⚠️ 参考値の天気予報です")
        
        cols = st.columns(3)
        with cols[0]:
            telop = weather_info.get('telop', '不明')
            st.metric(label="天気", value=telop)
        with cols[1]:
            # 気温の表示を改善
            temperature = weather_info.get('temperature_text', '').replace('気温:', '')
            st.metric(label="気温", value=temperature)
        with cols[2]:
            days = weather_info.get("days_ahead")
            if days is not None:
                st.metric(label="予報日", value=f"{days}日後")
        
        if weather_info.get("description"):
            with st.expander("天気の詳細", expanded=False):
                st.write(weather_info["description"])

###################
# メイン処理
###################

def main():
    st.set_page_config(
        page_title="🔥 燃える闘魂アイスブレイク",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # スタイルの適用
    st.markdown("""
    <style>
    /* ベースとなる背景色 */
    .stApp {
        background: linear-gradient(to bottom right, #800020, #000000);
    }
    
    /* メッセージカードのスタイル */
    .message-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }

    /* サイドバーのスタイル調整 */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.8);
    }
    
    /* サイドバーの文字色を白に */
    [data-testid="stSidebar"] [data-testid="stMarkdown"] p {
        color: white !important;
    }
    [data-testid="stSidebar"] .stSelectbox label {
        color: white !important;
    }
    [data-testid="stSidebar"] .stDateInput label {
        color: white !important;
    }
    [data-testid="stSidebar"] .stTextInput label {
        color: white !important;
    }
    
    /* メトリクス（天気情報など）の文字色を白に */
    [data-testid="stMetricLabel"] {
        color: white !important;
    }
    [data-testid="stMetricValue"] {
        color: white !important;
    }
    
    /* タブの文字色を白に */
    .stTabs [data-baseweb="tab"] {
        color: white !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    /* ニュースのタイトルと内容の文字色を白に */
    .news-content {
        color: white !important;
    }
    
    /* 天気詳細の展開部分のスタイル */
    [data-testid="stExpander"] {
        color: white !important;
    }
    [data-testid="stExpander"] .streamlit-expanderContent {
        color: white !important;
    }

    /* スピナーのテキストを白に */
    .stSpinner > div {
        color: white !important;
    }

    /* メッセージカード内のすべてのテキストを白に */
    .message-card p {
        color: white !important;
    }

    /* 猪木アドバイスのテキストを白に */
    .message-card div p {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # タイトル
    st.markdown("""
    <h1 style='text-align: center; color: white; padding: 20px;'>
        🔥 燃える闘魂アイスブレイク
    </h1>
    """, unsafe_allow_html=True)
    
    # 画像を中央寄せで表示
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("inoki.png")

    # サイドバー
    with st.sidebar:
        st.markdown("""
        <h3 style='color: white; margin-bottom: 20px;'>
            📝 訪問先の情報を入力
        </h3>
        """, unsafe_allow_html=True)
        
        prefecture, city = location_selector()
        industry_category, industry_detail = industry_selector()

        with st.form("input_form"):
            visit_date = st.date_input(
                "訪問日 📅",
                min_value=date.today(),
                max_value=date.today() + timedelta(days=7),
                value=date.today()
            )
            company_name = st.text_input("会社名 🏢")
            
            cols = st.columns(2)
            with cols[0]:
                clear = st.form_submit_button("クリア 🔄")
            with cols[1]:
                submit = st.form_submit_button("生成 ✨")

    if submit and company_name:
        with st.spinner("🔥 闘魂注入中..."):
            # データ取得
            weather_info = get_weather_info(city, visit_date)
            company_news = get_company_news(company_name)
            industry_news = get_industry_news(industry_category, industry_detail)

            # アドバイス生成
            message = generate_inoki_message(
                company_name, industry_category, industry_detail,
                city, weather_info, company_news, industry_news
            )

            # メッセージ表示
            st.markdown(f"""
            <div class="message-card">
                <h2 style="color: #FFD700; margin-bottom: 15px;">
                    💬 猪木からのアドバイス
                </h2>
                <div style="background: rgba(255, 0, 0, 0.1); padding: 20px; border-radius: 8px;">
                    <p style="color: white; font-size: 1.1em; line-height: 1.6;">
                        {message}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 天気情報
            st.markdown("""
            <div class="message-card">
                <h3 style="color: white;">🌤️ 天気情報</h3>
            """, unsafe_allow_html=True)
            
            cols = st.columns(2)
            with cols[0]:
                st.metric("天気", weather_info.get('telop', '不明'))
            with cols[1]:
                st.metric("気温", weather_info.get('temperature_text', '').replace('気温:', ''))

            if weather_info.get("description"):
                with st.expander("天気の詳細", expanded=False):
                    # 改行を事前に処理してからf-stringで使用
                    description_html = weather_info["description"].replace('\n', '<br>')
                    st.markdown(f"""
                    <div style="color: white;">
                        {description_html}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

            # ニュース表示
            st.markdown("""
            <div class="message-card">
                <h3 style="color: white;">📰 関連ニュース</h3>
            """, unsafe_allow_html=True)
            
            tabs = st.tabs(["🏢 企業ニュース", "📈 業界ニュース"])
            
            with tabs[0]:
                if company_news:
                    for news in company_news:
                        st.markdown(f"""
                        <div class="news-content" style="background: rgba(0,0,0,0.2); 
                             padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                            <h4 style="color: white; margin: 0;">{news['title']}</h4>
                            <p style="color: white; opacity: 0.9;">{news['description']}</p>
                            <small style="color: white; opacity: 0.7;">
                                関連度: {news['relevance_score']:.1f} | 
                                {datetime.strptime(news['published_at'][:10], '%Y-%m-%d').strftime('%Y年%m月%d日')}
                            </small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"{company_name}に関する最新ニュースは見つかりませんでした")

            with tabs[1]:
                if industry_news:
                    for news in industry_news:
                        st.markdown(f"""
                        <div class="news-content" style="background: rgba(0,0,0,0.2); 
                             padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                            <h4 style="color: white; margin: 0;">{news['title']}</h4>
                            <p style="color: white; opacity: 0.9;">{news['description']}</p>
                            <small style="color: white; opacity: 0.7;">
                                関連度: {news['relevance_score']:.1f} | 
                                {datetime.strptime(news['published_at'][:10], '%Y-%m-%d').strftime('%Y年%m月%d日')}
                            </small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"{industry_category}（{industry_detail}）の最新ニュースは見つかりませんでした")
            
            st.markdown("</div>", unsafe_allow_html=True)

    elif submit:
        st.warning("会社名を入力してください")

if __name__ == "__main__":
    main()