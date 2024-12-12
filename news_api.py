import requests
from typing import List, Dict, Optional
import streamlit as st

def get_company_news(company_name: str) -> List[Dict]:
    """会社名でニュースを検索"""
    base_url = "https://newsapi.org/v2/everything"
    api_key = st.secrets["api_keys"]["news_api"]
    
    params = {
        "q": company_name,
        "language": "jp",
        "sortBy": "publishedAt",
        "pageSize": 3,
        "apiKey": api_key
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        news_data = response.json()
        
        if news_data["status"] == "ok":
            articles = news_data["articles"]
            return [
                {
                    "title": article["title"],
                    "description": article["description"],
                    "url": article["url"],
                    "published_at": article["publishedAt"]
                }
                for article in articles
            ]
    except Exception as e:
        st.error(f"企業ニュース取得エラー: {str(e)}")
        return []
    
    return []

def get_industry_news(industry: str) -> List[Dict]:
    """業界のニュースを検索"""
    base_url = "https://newsapi.org/v2/everything"
    api_key = st.secrets["api_keys"]["news_api"]
    
    params = {
        "q": industry,
        "language": "jp",
        "sortBy": "publishedAt",
        "pageSize": 3,
        "apiKey": api_key
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        news_data = response.json()
        
        if news_data["status"] == "ok":
            articles = news_data["articles"]
            return [
                {
                    "title": article["title"],
                    "description": article["description"],
                    "url": article["url"],
                    "published_at": article["publishedAt"]
                }
                for article in articles
            ]
    except Exception as e:
        st.error(f"業界ニュース取得エラー: {str(e)}")
        return get_mock_news(industry)
    
    return []