import requests
from typing import Dict, Optional

def get_weather_info(location: str) -> Dict:
    """指定された地域の天気予報を取得"""
    # 地域コードの定義（一部抜粋）
    city_codes = {
        # 東京23区
        "千代田区": "130010",
        "中央区": "130010",
        "港区": "130010",
        "新宿区": "130010",
        "渋谷区": "130010",
        "品川区": "130010",
        
        # 主要都市
        "横浜市": "140010",
        "川崎市": "140010",
        "さいたま市": "110010",
        "千葉市": "120010",
        "名古屋市": "230010",
        "大阪市": "270000",
        "神戸市": "280010",
        "福岡市": "400010",
        "札幌市": "016010",
        "仙台市": "040010",
    }

    try:
        # 地域コードの取得
        city_code = city_codes.get(location)
        if not city_code:
            raise ValueError(f"未対応の地域です: {location}")

        # API呼び出し
        url = f"https://weather.tsukumijima.net/api/forecast/city/{city_code}"
        response = requests.get(url)
        response.raise_for_status()
        
        # JSONデータの取得
        weather_data = response.json()
        today = weather_data["forecasts"][0]
        
        # 気温の取得
        temp_max = today["temperature"]["max"]["celsius"] if today["temperature"]["max"] else None
        temp_min = today["temperature"]["min"]["celsius"] if today["temperature"]["min"] else None
        
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

        return {
            "temperature_text": temp_text,
            "description": weather_data["description"]["text"],
            "telop": today["telop"],
            "image_url": today["image"]["url"]
        }

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return {
            "temperature_text": "データなし",
            "description": "天気情報を取得できませんでした",
            "telop": "不明",
            "image_url": None
        }