import streamlit as st
from menu import menu_with_redirect
import pandas as pd
import plotly.express as px
from utils.func import break_page, hide_header_icons
from utils.load_data import get_additional_data, get_additional_reviews, get_data, get_reviews
from utils.text_editor import generate
import plotly.graph_objects as go

menu_with_redirect()
hide_header_icons()

def count_values(val):
    if pd.isnull(val) or val.strip() == "":
        return 0
    return len(val.split(','))

def format_data(data, marketplace):
    data = data[['itemId', 'shopId', 'marketplace', 'store', 'product_name', 'star_review', 'product_list', 'amount_sold_format', 'discount_price_format', 'per_discount','total_value']]
    data['count'] = data['product_list'].apply(count_values)

    data_group = data[data['marketplace'] == marketplace]
    if data_group['per_discount'].dtype == 'object':
            data_group['per_discount'] = data_group['per_discount'].str.replace('-', '').str.replace('%', '')
            data_group['per_discount'] = pd.to_numeric(data_group['per_discount'], errors='coerce')

    data_group['per_discount'] = data_group['per_discount'].fillna(0)
    return data_group

def calucalte_data(data):
    result = data.groupby(['marketplace', 'store']).agg({
                'amount_sold_format': 'sum',        
                'count': 'sum',  
                'discount_price_format': 'mean',       
                'per_discount': 'mean'  
            }).reset_index()
    
    result['sale_value'] = result['amount_sold_format'] * result['discount_price_format']
    total_sale = result['sale_value'].sum()
    result['total_value_percent'] = (result['sale_value'] / total_sale) * 100
    result = result.sort_values(by='total_value_percent', ascending=False)
    result['total_value_percent'] = result['total_value_percent'].apply(lambda x: f"{x:.2f}%")
    return result

def display(data):
    data_display = data[['marketplace', 'store', 'count', 'per_discount', 'discount_price_format', 'sale_value', 'total_value_percent']]
    data_display['per_discount'] = data_display['per_discount'].apply(lambda x: f"{x:.2f}%")
    data_display.rename(columns={'store': 'ร้านค้า', 'count': 'จำนวนตัวเลือก', 'per_discount': '% ส่วนลดเฉลี่ย', 'discount_price_format': 'ราคาลดแล้วเฉลี่ย(฿)', 'sale_value': 'Sale value (฿)', 'total_value_percent': 'สัดส่วนยอดขาย'}, inplace=True)
    st.dataframe(data_display, hide_index=True, column_config={
         "สัดส่วนยอดขาย": st.column_config.ProgressColumn(
            "สัดส่วนยอดขาย", 
            # format="%.2f",
            # min_value=0,
            # max_value=100,
        ),
    })

st.header(":blue[การวิเคราะห์ที่ 7]", divider=True)
st.subheader("คาแร็กเตอร์ร้านขายดีมีอะไรบ้าง")

data_doh = get_data()


desc_msg1 = '''
    **1. แป้งโดว์ - Shopee:**\n
    - ร้านค้าที่ให้ส่วนลดสูง เช่น **Double EQ Plus** มียอดขายค่อนข้างดี โดยเฉพาะเมื่อเทียบกับร้านที่ไม่ได้ลดราคา
    - อย่างไรก็ตาม ร้านค้าเช่น **porjai_doh** ที่ไม่มีส่วนลดเลยแต่สามารถทำยอดขายสูงสุด แสดงให้เห็นว่าปัจจัยอื่น ๆ เช่น คุณภาพสินค้าและความน่าเชื่อถือของร้านค้าเป็นสิ่งสำคัญ
'''
desc_msg2 = '''
    **2. แป้งโดว์ - Lazada:**\n
    - ร้านค้าที่มีส่วนลดเฉลี่ยสูง เช่น **Fastmarket.me** และ **Wanna's Shop** มียอดขายสูง แสดงให้เห็นว่าการให้ส่วนลดมากอาจช่วยกระตุ้นยอดขายได้
    - ร้านที่ไม่มีการลดราคา เช่น **NARA Global** ยังสามารถทำยอดขายได้ดี ซึ่งอาจบ่งบอกว่าลูกค้าใน Lazada ไม่ได้พิจารณาเฉพาะส่วนลดเพียงอย่างเดียว
'''

summary_msg1 = '''
    **ข้อเสนอแนะ:**\n
    - การให้ส่วนลดมีผลในการกระตุ้นยอดขาย แต่ไม่ใช่ปัจจัยหลักเพียงอย่างเดียว
    - ร้านค้าที่ประสบความสำเร็จมักมีสินค้าที่ได้รับการยอมรับจากลูกค้า โดยไม่จำเป็นต้องพึ่งส่วนลด
'''

desc_msg3 = '''
    **1. ดินน้ำมัน - Lazada:**\n
    - ร้านที่ให้ส่วนลดสูง เช่น **Dedee ดีดี้ ของใช้ราคาถูก** และ **imageoutlet** มีเปอร์เซ็นต์ส่วนลดสูงถึง **73-81%** ซึ่งเป็นการลดราคาที่น่าดึงดูด
    - บางร้าน เช่น **NARA Global** แม้ไม่มีส่วนลดเลย แต่ยังมียอดขายที่สูง ซึ่งแสดงให้เห็นว่าปัจจัยอื่น เช่น ชื่อเสียงร้านค้าหรือความน่าเชื่อถือก็มีผลต่อการขาย
'''

summary_msg2 = '''
    **ข้อเสนอแนะ:**\n
    - **การให้ส่วนลดสูง** สามารถกระตุ้นยอดขายได้อย่างมีประสิทธิภาพ โดยเฉพาะร้านที่มีส่วนลดมากกว่า 50%
    - อย่างไรก็ตาม ร้านที่ไม่มีการลดราคาเลยแต่ยังคงมียอดขายสูง อาจสะท้อนถึงความน่าเชื่อถือและคุณภาพของสินค้าที่ลูกค้าเชื่อถือ
'''


st.html("<strong style='font-size: 18px; text-decoration: underline;'>แป้งโดว์ (Play Dough)</strong>")
data_doh_shopee = format_data(data_doh, "shopee")
cal_doh_shopee = calucalte_data(data_doh_shopee)
display(cal_doh_shopee)

data_doh_lazada = format_data(data_doh, "lazada")
cal_doh_lazada = calucalte_data(data_doh_lazada)
display(cal_doh_lazada)
break_page()
st.markdown(desc_msg1)
st.markdown(desc_msg2)
st.markdown(summary_msg1)

st.divider()
break_page()
st.html("<strong style='font-size: 18px; text-decoration: underline;'>ดินน้ำมัน (Clay)</strong>")
data_plastic = get_additional_data("Lazada-Data_plastic")
reviews_plastic = get_additional_reviews("Lazada-Reviews_plastic")
reviews_group = reviews_plastic.groupby(['itemId', 'shopId']).agg(
                    count=('review_product', lambda x: len(set(x))) 
                ).reset_index()

data_plastic['marketplace'] = 'lazada'

data_plastic_lazada = format_data(data_plastic, "lazada")
data_plastic_lazada = data_plastic_lazada.drop(columns=['count'])
data_plastic_lazada = pd.merge(data_plastic_lazada, reviews_group, on=['itemId', 'shopId'], how='left')

cal_plastic_lazada = calucalte_data(data_plastic_lazada)
display(cal_plastic_lazada)
st.markdown(desc_msg3)
st.markdown(summary_msg2)



