import os
import requests
import random
import google.generativeai as genai
from atproto import Client, client_utils
from PIL import Image
import io

# --- [設定エリア] ---
RAKUTEN_APP_ID = '1001199996494785241'
RAKUTEN_AFF_ID = '50418107.bebbb42f.50418108.77932439'
BLUESKY_HANDLE = os.getenv('BLUESKY_HANDLE')
BLUESKY_APP_PASSWORD = os.getenv('BLUESKY_APP_PASSWORD')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Geminiの設定
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_ai_text(item_name, price):
    prompt = f"商品名「{item_name}」、価格「{price}円」のコスメを紹介する、親しみやすいSNS投稿文を100文字以内で作成してください。絵文字を使い、最後は「詳細はリンクをチェック👇」で締めてください。"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return f"✨ おすすめコスメ紹介 ✨\n{item_name[:50]}...\n価格：{price}円\n詳細はリンクをチェック👇"

def run_bluesky_bot():
    print("🚀 高機能版システム起動中...")

    # 1. 楽天から商品取得
    cosme_keywords = ["韓国コスメ", "新作コスメ", "神スキンケア", "ベストコスメ"]
    selected_keyword = random.choice(cosme_keywords)
    
    r_params = {
        "applicationId": RAKUTEN_APP_ID,
        "affiliateId": RAKUTEN_AFF_ID,
        "keyword": selected_keyword,
        "hits": 10,
        "imageFlag": 1
    }
    res = requests.get("https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706", params=r_params).json()
    item = random.choice(res["Items"])["Item"]

    # 2. 情報を抽出（価格・ポイント）
    price = item['itemPrice']
    point_rate = item.get('pointRate', 1)
    point_txt = f" 🔥 ポイント{point_rate}倍！" if point_rate > 1 else ""
    
    # 3. AIで紹介文作成
    ai_text = generate_ai_text(item['itemName'], price)

    # 4. 画像を4枚まで取得・加工
    img_data_list = []
    # 楽天の画像URLリストを取得
    raw_images = [img['imageUrl'].replace("?_ex=128x128", "") for img in item["mediumImageUrls"][:4]]
    
    for url in raw_images:
        img_res = requests.get(url).content
        # 600x600の白背景に中央配置
        base_img = Image.new("RGB", (600, 600), (255, 255, 255))
        item_img = Image.open(io.BytesIO(img_res)).convert("RGB")
        item_img.thumbnail((550, 550)) # アスペクト比を維持してリサイズ
        base_img.paste(item_img, ((600-item_img.width)//2, (600-item_img.height)//2))
        
        buf = io.BytesIO()
        base_img.save(buf, format='JPEG')
        img_data_list.append(buf.getvalue())

    # 5. Blueskyへ投稿
    client = Client()
    client.login(BLUESKY_HANDLE, BLUESKY_APP_PASSWORD)

    tb = client_utils.TextBuilder()
    tb.tag("#韓国コスメ", "韓国コスメ")
    tb.text(" ")
    tb.tag("#楽天", "楽天")
    tb.text(f"\nテーマ：{selected_keyword}\n\n")
    tb.text(f"{ai_text}\n\n")
    tb.text(f"💰 価格: {price}円{point_txt}\n")
    tb.link("🔗 楽天で詳細を見る", item['affiliateUrl'])

    # 画像を4枚添付して送信
    client.send_images(text=tb, images=img_data_list)
    print("✅ 4枚画像・AI文章・価格情報付きで投稿完了！")

if __name__ == "__main__":
    run_bluesky_bot()
