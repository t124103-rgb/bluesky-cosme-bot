import requests
import random
from atproto import Client, client_utils
from PIL import Image
import io

# --- [設定エリア] ---
RAKUTEN_APP_ID = '1001199996494785241'
RAKUTEN_AFF_ID = '50418107.bebbb42f.50418108.77932439'
BLUESKY_HANDLE = 'dailypromotiontt.bsky.social'
BLUESKY_APP_PASSWORD = 'm3uu-pfs7-yhay-5lpx'

def run_bluesky_bot():
    print("🚀 Blueskyシステム起動中...")

    # 1. 検索キーワード
    cosme_keywords = ["韓国コスメ 人気", "最新 バズりコスメ", "美容液 おすすめ", "プチプラ リップ"]
    selected_keyword = random.choice(cosme_keywords)
    
    # 2. 楽天から商品取得
    r_url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
    r_params = {
        "applicationId": RAKUTEN_APP_ID,
        "affiliateId": RAKUTEN_AFF_ID,
        "keyword": selected_keyword,
        "hits": 1,
        "imageFlag": 1
    }
    res = requests.get(r_url, params=r_params).json()
    item = res["Items"][0]["Item"]
    
    # 商品名を取得（全文）
    item_name_full = item['itemName']
    
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

    # TextBuilderで指定の順番（タグ→テーマ→リンク→商品名）に構築
    tb = client_utils.TextBuilder()
    
    # ① タグ
    tb.tag("#韓国コスメ", "韓国コスメ")
    tb.text(" ")
    tb.tag("#美容", "美容")
    tb.text(" ")
    tb.tag("#楽天", "楽天")
    tb.text("\n")
    
    # ② テーマ
    tb.text(f"テーマ：{selected_keyword}\n\n")
    
    # ③ リンク
    tb.link("🔗 楽天で詳細をチェック", item['affiliateUrl'])
    tb.text("\n\n")
    
    # ④ 商品名（文字数制限を考慮しつつ全文表示を目指す）
    # Blueskyの最大文字数は300文字。タグやリンクを除いた残りの枠を計算
    current_len = len(tb.build_text())
    max_name_len = 290 - current_len # 少し余裕を持たせる
    
    if len(item_name_full) > max_name_len:
        display_name = item_name_full[:max_name_len-3] + "..."
    else:
        display_name = item_name_full
        
    tb.text(display_name)

    # ⑤ 画像（send_imageで自動的にテキストの下に配置されます）
    client.send_image(
        text=tb,
        image=img_data_final,
        image_alt=display_name[:50]
    )

    print(f"✅ 指定の順番で全文投稿が完了しました！")

if __name__ == "__main__":
    run_bluesky_bot()