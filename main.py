import streamlit as st
from rembg import remove
from PIL import Image
import io

# 1. 設定網站標題與簡介
st.set_page_config(page_title="AI 圖片去背神器", page_icon="✂️")
st.title("✂️ 超簡單圖片去背 & 縮放工具")
st.write("上傳圖片，一鍵自動去背並調整尺寸！")

# 2. 建立側邊欄：功能設定
st.sidebar.header("⚙️ 設定選項")

# 功能 A: 選擇是否要調整尺寸
resize_option = st.sidebar.checkbox("我要修改影像尺寸", value=False)
new_width = 0
new_height = 0

if resize_option:
    st.sidebar.subheader("輸入新尺寸 (像素 px)")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        new_width = st.number_input("寬度 (Width)", min_value=1, value=500)
    with col2:
        new_height = st.number_input("高度 (Height)", min_value=1, value=500)

# 3. 檔案上傳區
uploaded_file = st.file_uploader("請上傳圖片 (支援 JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 讀取圖片
    original_image = Image.open(uploaded_file)
    
    # 顯示原始圖片
    st.subheader("原始圖片")
    st.image(original_image, caption="上傳的圖片", use_container_width=True)

    # 建立一個按鈕開始處理
    if st.button("🚀 開始去背與處理"):
        with st.spinner("AI 正在努力去背中，請稍候..."):
            try:
                # 步驟 1: 執行去背 (使用 rembg)
                processed_image = remove(original_image)

                # 步驟 2: 如果有勾選縮放，執行縮放
                if resize_option and new_width > 0 and new_height > 0:
                    processed_image = processed_image.resize((new_width, new_height))
                    st.success(f"已去背並縮放至: {new_width}x{new_height}")
                else:
                    st.success("去背完成！(維持原始尺寸)")

                # 顯示結果圖片
                st.subheader("處理結果")
                
                # 建立兩欄對比
                col_a, col_b = st.columns(2)
                with col_a:
                    st.image(original_image, caption="原始圖", use_container_width=True)
                with col_b:
                    st.image(processed_image, caption="去背結果", use_container_width=True)

                # 準備下載按鈕
                # 將圖片轉為二進位格式以便下載
                img_byte_arr = io.BytesIO()
                processed_image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()

                st.download_button(
                    label="📥 下載處理後的圖片 (PNG)",
                    data=img_byte_arr,
                    file_name="removed_bg_image.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error(f"發生錯誤：{e}")