import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from menu import menu_with_redirect
from utils.func import hide_header_icons
from utils.text_editor import generate
from utils.load_data import get_additional_data, get_additional_reviews, get_data, get_reviews

menu_with_redirect()
hide_header_icons()

def get_best_sale(data, reviews, marketplace):
    data = data[data['marketplace'] == marketplace]
    data = data.query("total_value>100")
    best_saler = data[['marketplace', 'store', 'itemId', 'shopId', 'amount_sold_format', 'discount_price_format', 'per_discount', 'total_value']]
    if best_saler['per_discount'].dtype == 'object':
            best_saler['per_discount'] = best_saler['per_discount'].str.replace('%', '').str.replace('-', '')
            best_saler['per_discount'] = pd.to_numeric(best_saler['per_discount'], errors='coerce')
    best_saler['per_discount'] = best_saler['per_discount'].fillna(0)        
    best_saler = best_saler.sort_values(by='total_value', ascending=False)
    
    reviews = reviews[reviews['marketplace'] == marketplace]
    reviews = reviews[['marketplace', 'itemId', 'shopId', 'review_product']]
    reviews = reviews.groupby(['marketplace', 'itemId', 'shopId', 'review_product']).size().reset_index(name='count')
    reviews = reviews.query("count>1")

    grouping = pd.merge(best_saler, reviews, on=['marketplace', 'itemId', 'shopId'], how='left')

    grouping = grouping.dropna(subset=['review_product', 'count'])
    grouping = grouping.sort_values(by=['itemId', 'shopId', 'count'], ascending=[True, True, False])
    top_3_df = grouping.groupby(['itemId', 'shopId']).head(3).reset_index(drop=True)

    top_3_df = top_3_df.sort_values(by=['total_value', 'count'], ascending=[False, False])
    return top_3_df

def display(data):
    data_display = data[['marketplace', 'store', 'amount_sold_format', 'discount_price_format', 'per_discount', 'total_value', 'review_product', 'count']]
    data_display['per_discount'] = data_display['per_discount'].apply(lambda x: f"{x}%")
    data_display.rename(columns={'store': 'ร้านค้า', 'amount_sold_format': 'ยอดขาย', 'per_discount': '% ส่วนลดเฉลี่ย', 'discount_price_format': 'ราคา', 'total_value': 'Sale value (฿)', 'review_product': 'สินค้า', 'count': 'จำนวน'}, inplace=True)
    st.dataframe(data_display, hide_index=True)
    return None

st.header(":blue[การวิเคราะห์ที่ 1]", divider=True)
st.subheader("คุณลักษณะแบบไหนที่มียอดขายดี")

data_doh = get_data()
reviews_doh = get_reviews()

st.html("<strong style='font-size: 18px; text-decoration: underline;'>แป้งโดว์ (Play Dough)</strong>")
st.markdown("**Shopee**")
data_doh_shopee = get_best_sale(data_doh, reviews_doh, 'shopee')
display(data_doh_shopee)

st.markdown("**Lazada**")
data_doh_lazada = get_best_sale(data_doh, reviews_doh, 'lazada')
display(data_doh_lazada)

st.divider()
st.html("<strong style='font-size: 18px; text-decoration: underline;'>ดินน้ำมัน (Clay)</strong>")
data_plastic = get_additional_data("Lazada-Data_plastic")
data_plastic['marketplace'] = 'lazada'
reviews_plastic = get_additional_reviews("Lazada-Reviews_plastic")
reviews_plastic['marketplace'] = 'lazada'
data_doh_plastic = get_best_sale(data_plastic, reviews_plastic, 'lazada')
display(data_doh_plastic)

desc_msg = '''
    **คำอธิบาย:**\n
    จากการวิเคราะห์ยอดขายรวมระหว่าง **Shopee** และ **Lazada** พบว่า Shopee มียอดขายรวมสูงกว่าอย่างมีนัยสำคัญ โดยยอดขายรวมของ Shopee อยู่ที่ประมาณ 2,865,781 บาท ในขณะที่ Lazada มียอดขายรวมประมาณ 1,951,306 บาท ความแตกต่างของยอดขายอาจเกิดจากหลายปัจจัย เช่น ฐานลูกค้าที่กว้างกว่า การส่งเสริมการขายที่เข้มแข็งกว่า หรือระบบการใช้งานแพลตฟอร์มที่ตอบโจทย์ผู้ใช้มากกว่า

    จากข้อมูลนี้ Shopee จึงเป็นแพลตฟอร์มที่มีแนวโน้มสร้างยอดขายได้สูงกว่า Lazada เนื่องจากแพลตฟอร์มมีการกระตุ้นให้เกิดการซื้อที่ดีมากกว่า และมีฐานลูกค้าที่กว้างขึ้น เหมาะสำหรับผู้ค้ารายใหม่ที่ต้องการขายสินค้าที่สามารถตั้งราคาได้สูงกว่าและเข้าถึงลูกค้าที่มีความหลากหลาย
'''
summary_msg = '''
    **สรุป:** Shopee เหมาะสมกับการเปิดร้านค้าออนไลน์มากกว่า Lazada เนื่องจากยอดขายรวมที่สูงกว่า และมีโอกาสในการสร้างกำไรที่มากกว่า
'''
# st.markdown(desc_msg)
# st.markdown(summary_msg)

