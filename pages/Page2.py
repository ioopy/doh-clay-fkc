import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from menu import menu_with_redirect
from utils.func import break_page, hide_header_icons
from utils.text_editor import generate
from utils.load_data import get_additional_data, get_data, get_reviews
import plotly.express as px
import numpy as np

menu_with_redirect()
hide_header_icons()

def classify_sold_amount(sold_amount):
    if sold_amount > 1000:
        return 'High ยอดขายมากกว่า 1000'
    elif sold_amount >= 500 and sold_amount <= 1000:
        return 'Normal ยอดขาย 501-1000'
    else:
        return 'Low ยอดขายน้อยกว่า 500'

def format_data(data):
    data['level'] = data['amount_sold_format'].apply(classify_sold_amount)
    data = data[['marketplace', 'level', 'amount_sold_format', 'discount_price_format']]
    data = data.query("discount_price_format>0")
    
    data['level'] = pd.Categorical(data['level'], categories=level_order, ordered=True)
    return data

def display(data):
    data_display = data[['marketplace', 'amount_sold_format', 'discount_price_format']]
    data_display.rename(columns={'amount_sold_format': 'จำนวนที่ขายแล้ว', 'discount_price_format': 'ราคาขาย'}, inplace=True)
    st.dataframe(data_display, hide_index=True)

def data_stat(data):
    descriptive_stats = data.groupby(['marketplace', 'level'])['discount_price_format'].describe().reset_index()
    descriptive_stats['level'] = pd.Categorical(descriptive_stats['level'], categories=level_order, ordered=True)
    data_display2 = descriptive_stats[['marketplace', 'count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
    st.dataframe(data_display2, hide_index=True)

def get_box_plot(data):
    fig = px.box(
        data, 
        x="marketplace",    # Separate box plots by marketplace
        y="discount_price_format",          # Show price distribution
        color="level",      # Color by level (assuming 'level' is a column in your data_doh)
        labels={"discount_price_format": "ราคาขาย", "marketplace": "Marketplace", "level": "Level"},
        category_orders={"level": level_order}
    )

    # Update layout for better visualization
    fig.update_layout(
        boxmode='group',   # Group the boxes by marketplace
        xaxis_title="",
        yaxis_title="ราคาขาย",
        showlegend=True,
        xaxis_tickfont_size=16,
        yaxis_tickfont_size=16,
        font=dict(
            size=18,
        ),
        legend=dict(
            orientation="h",        # Set the legend orientation to horizontal
            yanchor="bottom",       # Anchor the legend at the bottom
            y=1,                    # Position the legend above the graph
            xanchor="center",       # Center the legend horizontally
            x=0.5                   # Set the legend to the center of the x-axis
        ),
        legend_title_text=''
    )
    st.plotly_chart(fig)

st.header(":blue[การวิเคราะห์ที่ 2]", divider=True)
st.subheader("ตั้งราคาขายเท่าไหร่ดี")

data_doh = get_data()
data_plastic = get_additional_data("Lazada-Data_plastic")
data_doh = data_doh.query("amount_sold_format > 0")
data_plastic['marketplace'] = 'lazada'
data_plastic = data_plastic.query("amount_sold_format > 0")

level_order = ["Low ยอดขายน้อยกว่า 500", "Normal ยอดขาย 501-1000", "High ยอดขายมากกว่า 1000"]

desc_msg1 = '''
    **1. แป้งโดว์ Shopee:**\n
    - สินค้าราคาย่อมเยาในช่วง 200-300 บาท เป็นสินค้าที่มียอดขายสูงสุดใน Shopee โดยเฉพาะในกลุ่มสินค้าที่มียอดขายต่ำกว่า 500 หน่วย
    - แม้ว่าจะมีบางสินค้าที่ราคาสูงกว่า 1000 บาทขายได้ แต่จำนวนสินค้ากลุ่มนี้มีไม่มากนัก สะท้อนถึงแนวโน้มที่ลูกค้า Shopee มักให้ความสำคัญกับสินค้าราคาประหยัด
    - หากต้องการเพิ่มยอดขายใน Shopee การตั้งราคาสินค้าในช่วงต่ำกว่า 300 บาทจะเป็นกลยุทธ์ที่ตอบโจทย์ความต้องการของลูกค้า
'''
desc_msg2 = '''
    **2. แป้งโดว์ Lazada:**\n
    - สินค้าราคาย่อมเยาในช่วง 200-300 บาท ยังคงขายดีใน Lazada แต่มีแนวโน้มที่สินค้าที่มีราคาสูงขึ้น (400-600 บาท) จะได้รับความสนใจมากกว่าบนแพลตฟอร์มนี้ เมื่อเทียบกับ Shopee
    - ในกลุ่มสินค้าที่มียอดขายระดับปกติและสูง (501-1000 หน่วย) ลูกค้าใน Lazada มีแนวโน้มที่จะมีกำลังซื้อสูงกว่า สามารถยอมจ่ายเพื่อสินค้าที่มีราคาสูงขึ้นได้
    - การวางแผนการขายบน Lazada ควรคำนึงถึงการเพิ่มผลิตภัณฑ์ที่มีราคาสูงขึ้น เพื่อดึงดูดลูกค้ากลุ่มที่มีกำลังซื้อสูง
'''
desc_msg3 = '''
    **3. ดินน้ำมัน Lazada:**\n
    - สินค้าในช่วงราคาประหยัด 200-300 บาท มียอดขายสูงที่สุดใน Lazada แต่ก็มีสินค้าบางรายการที่ราคาสูงถึง 1600 บาทและยังสามารถขายได้ดี ซึ่งบ่งบอกว่ามีกลุ่มลูกค้าบางส่วนที่ยอมจ่ายเงินซื้อสินค้าราคาสูง
    - สินค้าในกลุ่มปกติ (501-1000 หน่วย) มักจะขายได้ดีในช่วงราคาประมาณ 200-400 บาท ซึ่งเป็นช่วงราคาที่มีความเสถียร
    - การเพิ่มการโปรโมตสินค้าที่มีราคาสูงขึ้น อาจช่วยเพิ่มยอดขายได้ เนื่องจากมีลูกค้าบางกลุ่มที่มีกำลังซื้อสูงและพร้อมที่จะจ่ายในราคาที่แพงขึ้น
'''
summary_msg = '''
    **ข้อเสนอแนะ:** 
    1. Shopee: ควรเน้นการตั้งราคาสินค้าที่คุ้มค่าและเข้าถึงง่าย การตั้งราคาต่ำกว่า 300 บาทจะช่วยดึงดูดลูกค้าและเพิ่มยอดขายได้อย่างมีประสิทธิภาพ
    2. Lazada (แป้งโดว์และดินน้ำมัน): มีความยืดหยุ่นในการตั้งราคามากกว่า Shopee สามารถเพิ่มสินค้าที่มีราคาในช่วงต่าง ๆ เพื่อเข้าถึงกลุ่มลูกค้าที่หลากหลาย ทั้งผู้ที่มีกำลังซื้อต่ำและสูง
    3. ดินน้ำมัน: การโปรโมตสินค้าที่มีราคาสูงจะช่วยให้สามารถขยายฐานลูกค้าและเพิ่มยอดขายได้ เนื่องจากมีบางกลุ่มที่พร้อมจ่ายเพื่อสินค้าที่มีคุณภาพและราคาสูง
'''

st.html("<strong style='font-size: 18px; text-decoration: underline;'>แป้งโดว์ (Play Dough)</strong>")
data_doh = format_data(data_doh)
display(data_doh)
data_stat(data_doh)
break_page()
get_box_plot(data_doh)
st.markdown(desc_msg1)
st.markdown(desc_msg2)

st.divider()
break_page()
st.html("<strong style='font-size: 18px; text-decoration: underline;'>ดินน้ำมัน (Clay)</strong>")
data_plastic = format_data(data_plastic)
display(data_plastic)
data_stat(data_plastic)
get_box_plot(data_plastic)


st.markdown(desc_msg3)
st.markdown(summary_msg)

