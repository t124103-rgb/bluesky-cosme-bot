import os
import requests
import random
from atproto import Client, client_utils
from PIL import Image
import io

# --- [設定エリア] ---
RAKUTEN_APP_ID = '1001199996494785241'
RAKUTEN_AFF_ID = '50418107.bebbb42f.50418108.77932439'
BLUESKY_HANDLE = os.getenv('BLUESKY_HANDLE')
BLUESKY_APP_PASSWORD = os.getenv('BLUESKY_APP_PASSWORD')

def run_bluesky_bot():
    print("🚀 Blueskyシステム起動中...")

    # 1. 検索キーワード（ヒットしやすいワードに調整）
    cosme_keywords = ["韓国コスメ 人気", "最新 バズりコスメ", "美容液 おすすめ", "プチプラ リップ","神ファンデ", "時短スキンケア", "保湿パック", "デパコス 似", "アイシャドウ パレット", "マスカラ 落ちない", "毛穴ケア", "美白ケア"]
    selected_keyword = random.choice(cosme_keywords)
    print(f"🔎 検索キーワード: {selected_keyword}")

    # 2. 楽天から商品取得
    r_url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
    r_params = {
        "applicationId": RAKUTEN_APP_ID,
        "affiliateId": RAKUTEN_AFF_ID,
        "keyword": selected_keyword,
        "hits": 5, # 複数取得して空振りを防ぐ
        "imageFlag": 1
    }
    res = requests.get(r_url, params=r_params).json()

    # ★安全装置：検索結果があるかチェック
    if "Items" not in res or len(res["Items"]) == 0:
        print(f"⚠️ キーワード '{selected_keyword}' で商品が見つかりませんでした。終了します。")
        return

    # 結果の中からランダムに1つ選ぶ（さらにバリエーションが増えます）
    item = random.choice(res["Items"])["Item"]
    item_name_full = item['itemName']
    print(f"📦 ヒット商品: {item_name_full[:20]}...")
    
    # 3. 画像生成
    img_url = item["mediumImageUrls"][0]["imageUrl"].replace("?_ex=128x128", "")
    img_data = requests.get(img_url).content
    base_img = Image.new("RGB", (600, 600), (255, 255, 255))
    item_img = Image.open(io.BytesIO(img_data)).convert("RGB").resize((500, 500))
    base_img.paste(item_img, (50, 20))
    
    img_byte_arr = io.BytesIO()
    base_img.save(img_byte_arr, format='JPEG')
    img_data_final = img_byte_arr.getvalue()

    # 4. Blueskyへ投稿
    print("📤 Blueskyへ送信中...")
    client = Client()
    client.login(BLUESKY_HANDLE, BLUESKY_APP_PASSWORD)

    tb = client_utils.TextBuilder()
    tb.tag("#韓国コスメ", "韓国コスメ")
    tb.text(" ")
    tb.tag("#美容", "美容")
    tb.text(" ")
    tb.tag("#楽天", "楽天")
    tb.text("\n")
    tb.text(f"テーマ：{selected_keyword}\n\n")
    tb.link("🔗 楽天で詳細をチェック", item['affiliateUrl'])
    tb.text("\n\n")
    
    # 文字数制限（300文字）の調整
    current_len = len(tb.build_text())
    max_name_len = 280 - current_len 
    display_name = item_name_full if len(item_name_full) <= max_name_len else item_name_full[:max_name_len] + "..."
    tb.text(display_name)

    client.send_image(text=tb, image=img_data_final, image_alt="Cosmetic Item")
    print(f"✅ 投稿完了しました！")

if __name__ == "__main__":
    run_bluesky_bot()



