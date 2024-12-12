from openai import OpenAI
import streamlit as st
from typing import Dict

def generate_inoki_message(company_name: str, industry: str, location: str, weather_info: Dict, company_news: list, industry_news: list) -> str:
    """OpenAI APIを使用して猪木風メッセージを生成"""
    
    # クライアントの初期化
    client = OpenAI(api_key=st.secrets["api_keys"]["openai_api"])
    
    # ニュースの整形
    news_text = ""
    if company_news:
        news_text += f"\n企業ニュース:\n" + "\n".join([f"- {news['title']}" for news in company_news[:2]])
    if industry_news:
        news_text += f"\n業界ニュース:\n" + "\n".join([f"- {news['title']}" for news in industry_news[:2]])

    # プロンプトの作成
    prompt = f"""
以下の情報を元に、プロレスラーのアントニオ猪木風の熱血的なビジネストークを生成してください。
猪木らしい口調で、前向きで熱意のあるメッセージを作成してください。

情報:
- 会社名: {company_name}
- 業界: {industry}
- 場所: {location}
- 天気: {weather_info['telop']} ({weather_info['temperature_text']})
{news_text}

以下の要素を必ず含めてください：
- 「闘魂」というワードを1-2回使用
- 天気に関連した前向きな言及
- ニュースの内容に触れる
- 最後に「〜ですね！」のような共感を誘う形で締める

口調の例：
- ですます調を基本とする
- 「〜じゃー！」のような猪木らしい語尾を時々使用
- ビジネスシーンに適した丁寧さを保ちつつ、熱意のある表現を使用
"""

    try:
        # ChatGPT APIの呼び出し
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたはプロレスラーのアントニオ猪木として話します。熱血的で力強い口調ですが、ビジネスシーンに適した丁寧さも保ちます。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content

    except Exception as e:
        st.error(f"メッセージ生成エラー: {str(e)}")
        return f"""
        闘魂の朝じゃー！{location}は{weather_info['telop']}！
        
        {company_name}の皆さん！
        この天気のように、ビジネスチャンスの風を感じる素晴らしい一日になりそうですね！
        
        {industry}業界で新たな歴史を作るため、共に闘魂を見せていきましょう！
        
        さあ、熱い商談の始まりです！闘魂注入！！！
        """