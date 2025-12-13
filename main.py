import streamlit as st
from rembg import remove
from PIL import Image
import io

# ================= 設定區 =================
st.set_page_config(page_title="AI 圖片去背 & 壓縮神器", page_icon="✂️", layout="centered")

# --- 關鍵修改：注入 CSS 讓圖片完美置中 ---
# 這段 CSS 會強制讓所有圖片容器變成彈性盒子(Flexbox)，達到上下左右置中的效果
st.markdown(
    """
    <style>
    /* 讓圖片容器置中 */
    div[data-testid="stImage"] {
        display: flex;
        justify-content: center; /* 水平置中 */
        align-items: center;     /* 垂直置中 */
        width: 100%;
        margin-top: 20px;       /* 上方留點白 */
        margin-bottom: 20px;    /* 下方留點白 */
    }
    /* 確保圖片本身不會超過螢幕寬度，但保持原比例 */
    div[data-testid="stImage"] > img {
        max-width: 100%;
        height: auto;
        border-radius: 10px;    /* 加一點圓角讓圖片更好看 */
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* 加一點陰影增加立體感 */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 輔助函式：智慧壓縮圖片 (PNG) ---
def compress_png_to_target_kb(pil_img, target_kb):
    """
    嘗試將 PNG 圖片壓縮到指定 KB 大小。
    方法：啟用優化存檔，如果還是太大，就逐步縮小尺寸直到符合要求。
    """
    current_img = pil_img.copy()
    max_attempts = 10 
    
    for i in range(max_attempts):
        buffer = io.BytesIO()
        current_img.save(buffer, format='PNG', optimize=True)
        size_kb = buffer.tell() / 1024

        if size_kb <= target_kb:
            return buffer.getvalue(), size_kb, current_img.size

        if i < max_attempts - 1:
            width, height = current_img.size
            new_width = int(width * 0.9)
            new_height = int(height * 0.9)
            if new_width < 50 or new_height < 50:
                 break
            current_img = current_img.resize((new_width, new_height), Image.LANCZOS)
    
    return buffer.getvalue(), size_kb, current_img.size

# ================= 主程式開始 =================

st.title("✂️ AI 圖片去背 & 壓縮工具")
st.write("一鍵去背，並支援調整尺寸與壓縮檔案大小！")

# --- 側邊欄設定 ---
st.sidebar.header("⚙️ 設定選項")

# 1. 修改尺寸
st.sidebar.subheader("1️⃣ 尺寸調整 (選填)")
resize_option = st.sidebar.checkbox("我要手動修改影像尺寸", value=False)
new_width = 0
new_height = 0

if resize_option:
    col1, col2 = st.sidebar.columns(2)
    with col1:
        new_width = st.number_input("寬度 (Width)", min_value=1, value=500)
    with col2:
        new_height = st.number_input("高度 (Height)", min_value=1, value=500)

# 2. 壓縮設定
st.sidebar.markdown("---")
st.sidebar.subheader("2️⃣ 檔案壓縮 (選填)")
compress_option = st.sidebar.checkbox("我要壓縮檔案大小 (KB)", value=False)
target_kb = 500

if compress_option:
    target_kb = st.sidebar.number_input("目標大小 (KB)", min_value=50, value=500, step=50, help="為了達到目標大小，系統可能會自動縮小圖片尺寸以符合要求。")
    st.sidebar.info(f"系統將嘗試把檔案壓縮至 {target_kb} KB 以下。")

# --- 主要區域 ---
st.markdown("---")
uploaded_file = st.file_uploader("請上傳圖片 (支援 JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 讀取圖片
    original_image = Image.open(uploaded_file)
    
    # 顯示原始圖片 (直接呼叫 st.image，CSS 會自動幫我們置中)
    st.subheader("原始圖片")
    st.image(original_image, caption=f"原始尺寸: {original_image.size[0]}x{original_image.size[1]}")

    # 置中按鈕 (利用 Streamlit 的 columns 排版技巧)
    col_spacer1, col_btn, col_spacer2 = st.columns([2, 1, 2])
    with col_btn:
        process_button = st.button("🚀 開始處理圖片", use_container_width=True)

    if process_button:
        with st.spinner("AI 正在去背與處理中，請稍候..."):
            try:
                # 1. 去背
                processed_image = remove(original_image)
                status_text = "✅ 去背完成！"

                # 2. 尺寸調整
                if resize_option and new_width > 0 and new_height > 0:
                    processed_image = processed_image.resize((new_width, new_height), Image.LANCZOS)
                    status_text += f" (已縮放至 {new_width}x{new_height})"

                # 3. 壓縮與準備下載
                final_img_bytes = None
                final_info_text = ""

                if compress_option:
                     st.info(f"正在努力壓縮至 {target_kb} KB 以下，請稍候...")
                     final_img_bytes, final_size_kb, final_dims = compress_png_to_target_kb(processed_image, target_kb)
                     
                     if final_size_kb <= target_kb + 10:
                         status_text += f" 且成功壓縮！"
                         final_info_text = f"最終大小: {final_size_kb:.1f} KB (尺寸: {final_dims[0]}x{final_dims[1]})"
                     else:
                         status_text += f" (壓縮已達極限)"
                         final_info_text = f"已盡力壓縮至: {final_size_kb:.1f} KB"
                else:
                    img_byte_arr = io.BytesIO()
                    processed_image.save(img_byte_arr, format='PNG')
                    final_img_bytes = img_byte_arr.getvalue()
                    final_size_kb = img_byte_arr.tell() / 1024
                    final_info_text = f"最終大小: {final_size_kb:.1f} KB"

                st.success(status_text)

                # 顯示結果
                st.subheader("處理結果")
                st.markdown(f"**{final_info_text}**")
                
                # 為了顯示，轉回 Image 物件
                if compress_option:
                     display_img = Image.open(io.BytesIO(final_img_bytes))
                else:
                     display_img = processed_image

                # 顯示圖片 (CSS 會自動置中)
                st.image(display_img, caption="最終結果 (透明背景 PNG)")

                # 下載按鈕 (置中)
                col_dl_spacer1, col_dl_btn, col_dl_spacer2 = st.columns([2, 1, 2])
                with col_dl_btn:
                    st.download_button(
                        label="📥 下載處理後的圖片 (PNG)",
                        data=final_img_bytes,
                        file_name="processed_image.png",
                        mime="image/png",
                        use_container_width=True
                    )

            except Exception as e:
                st.error(f"發生錯誤：{e}")