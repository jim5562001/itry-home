import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm # 用來設定公分
import os
from datetime import date

# 1. 設定網站標題
st.title("iTRY 無人商店 - 自動報告生成器")
st.write("請輸入本期數據，系統將自動生成 Word 報告。")

# 2. 建立輸入欄位 (左邊輸入資料)
with st.sidebar:
    st.header("1. 基本資訊")
    community_name = st.text_input("社區名稱 (例如：環球市)", "環球市")
    report_start_date = st.date_input("報告開始日期", date.today())
    report_end_date = st.date_input("報告結束日期", date.today())
    
    st.header("2. 電費資訊")
    prev_date = st.date_input("上次抄表日期", date.today())
    curr_date = st.date_input("本次抄表日期", date.today())
    
    # 電費計算
    prev_meter = st.number_input("上次累計用電量 (度)", min_value=0.0, step=0.1)
    curr_meter = st.number_input("本次累計用電量 (度)", min_value=0.0, step=0.1)
    
    # 自動計算差額
    usage_kwh = round(curr_meter - prev_meter, 1)
    if usage_kwh < 0:
        st.warning("⚠️ 注意：本次讀數小於上次讀數！")
        
    elec_rate = st.number_input("每度電費 (元)", value=4.2, step=0.1)
    
    st.header("3. 銷售與分潤")
    total_sales = st.number_input("總銷售金額 (元)", min_value=0, step=1)
    total_items = st.number_input("銷售件數 (件)", min_value=0, step=1)
    profit_percent = st.number_input("分潤趴數 (%)", value=2, step=1)

    st.header("4. 上傳圖片 (可多張)")
    # accept_multiple_files=True 開啟多選功能
    meter_photos = st.file_uploader("上傳電表照片", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# 3. 計算邏輯
total_elec_cost = int(round(usage_kwh * elec_rate, 0))
rebate_amount = int(round(total_sales * (profit_percent / 100), 0))
total_transfer = total_elec_cost + rebate_amount

# 預覽區
st.subheader("📊 數據預覽")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("本期用電", f"{usage_kwh} 度")
with col2:
    st.metric("電費總計", f"${total_elec_cost:,}")
with col3:
    st.metric("回饋金", f"${rebate_amount:,}")

# 4. 生成報告
if st.button("生成 Word 報告"):
    if not os.path.exists("template.docx"):
        st.error("找不到 template.docx！")
    else:
        doc = DocxTemplate("template.docx")
        
        # 處理多張圖片
        image_list = []
        if meter_photos:
            for i, photo in enumerate(meter_photos):
                # 存成暫存檔 (檔名不重複)
                temp_filename = f"temp_image_{i}.jpg"
                with open(temp_filename, "wb") as f:
                    f.write(photo.getbuffer())
                
                # 設定圖片尺寸：寬 60mm (6cm), 高 80mm (8cm)
                img_obj = InlineImage(doc, temp_filename, width=Mm(60), height=Mm(80))
                image_list.append(img_obj)
        
        context = {
            'community_name': community_name,
            'start_date': report_start_date.strftime("%Y年%m月%d日"),
            'end_date': report_end_date.strftime("%Y年%m月%d日"),
            'prev_date': prev_date.strftime("%Y年%m月%d日"),
            'curr_date': curr_date.strftime("%Y年%m月%d日"),
            'prev_meter': prev_meter,
            'curr_meter': curr_meter,
            'usage_kwh': usage_kwh,
            'elec_rate': elec_rate,
            'total_elec_cost': f"{total_elec_cost:,}",
            'total_sales': f"{total_sales:,}",
            'total_items': total_items,
            'profit_percent': profit_percent,
            'rebate_amount': f"{rebate_amount:,}",
            'total_transfer': f"{total_transfer:,}",
            'meter_images': image_list  # 這裡傳入的是一個圖片列表
        }

        doc.render(context)
        output_filename = f"{community_name}_營運報告.docx"
        doc.save(output_filename)
        
        # 清除暫存圖片 (保持資料夾乾淨)
        for i in range(len(meter_photos)):
            try:
                os.remove(f"temp_image_{i}.jpg")
            except:
                pass
        
        with open(output_filename, "rb") as file:
            btn = st.download_button(
                label="📥 下載報告",
                data=file,
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        st.success("報告生成成功！")