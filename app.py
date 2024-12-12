import streamlit as st
from weather_api import get_weather_info
from news_api import get_company_news, get_industry_news
from openai_api import generate_inoki_message

def display_news_section(company_name: str, industry: str):
    """ニュース表示セクション"""
    # 企業ニュース
    company_news = get_company_news(company_name)
    if company_news:
        st.markdown(f"### 📰 {company_name}の最新ニュース")
        for news in company_news:
            with st.expander(news["title"], expanded=False):
                if news["description"]:
                    st.write(news["description"])
                st.write(f"公開日: {news['published_at']}")
                st.write(f"[詳細を読む]({news['url']})")
    
    # 業界ニュース
    industry_news = get_industry_news(industry)
    if industry_news:
        st.markdown(f"### 📈 {industry}業界の最新ニュース")
        for news in industry_news:
            with st.expander(news["title"], expanded=False):
                if news["description"]:
                    st.write(news["description"])
                st.write(f"公開日: {news['published_at']}")
                st.write(f"[詳細を読む]({news['url']})")
    
    if not company_news and not industry_news:
        st.info("関連ニュースが見つかりませんでした")
    
    return company_news, industry_news

def main():
    st.title("猪木のビジネストークジェネレーター 🔥")

    # サイドバーフォーム
    with st.sidebar:
        st.markdown("### 訪問先の情報を入力してください")
        
        with st.form("input_form"):
            location = st.selectbox(
                "訪問場所",
                [
                    # 東京23区
                    "千代田区", "中央区", "港区", "新宿区", "渋谷区", "品川区",
                    # 主要都市
                    "横浜市", "川崎市", "さいたま市", "千葉市", 
                    "名古屋市", "大阪市", "神戸市", "福岡市", 
                    "札幌市", "仙台市"
                ],
                key='location'
            )
            
            company_name = st.text_input(
                "会社名",
                key='company_name',
                placeholder="例：株式会社..."
            )
            
            industry = st.selectbox(
                "業種",
                ["IT・通信", "製造業", "小売業", "金融業", "不動産業", "建設業", "サービス業"],
                key='industry'
            )

            submit_button = st.form_submit_button("闘魂トーク生成！")

    # 結果の表示
    if submit_button and company_name:
        with st.spinner("データ取得中..."):
            # 天気情報の取得
            weather_info = get_weather_info(location)
            
            # 2カラムレイアウト
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # ニュースセクション（戻り値を受け取る）
                company_news, industry_news = display_news_section(company_name, industry)
            
            with col2:
                # 天気情報の表示
                st.markdown("### 🌤️ 現地の天気")
                st.write(f"天気: {weather_info['telop']}")
                st.write(f"{weather_info['temperature_text']}")
            
            # 猪木メッセージの生成と表示
            st.markdown("### 🔥 猪木からのメッセージ")
            message = generate_inoki_message(
                company_name, 
                industry, 
                location, 
                weather_info, 
                company_news, 
                industry_news
            )
            st.info(message)
    
    elif submit_button:
        st.warning("会社名を入力してください！")

if __name__ == "__main__":
    main()