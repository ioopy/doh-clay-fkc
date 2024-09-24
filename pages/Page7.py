import streamlit as st
from menu import menu_with_redirect
import pandas as pd
import plotly.express as px
from utils.func import break_page, get_color_map, hide_header_icons
from utils.load_data import get_additional_data, get_data, get_reviews
from utils.text_editor import generate
import plotly.graph_objects as go
import numpy as np

menu_with_redirect()
hide_header_icons()

def get_bar_plot(data, title):
    data = data.sort_values('amount_sold_format', ascending=True)
    data.rename(columns={'amount_sold_format': 'ยอดขาย'}, inplace=True)
    fig = px.bar(
        data,
        x='ยอดขาย', 
        y='province',
        color=data["ยอดขาย"],
        orientation='h',
    )
    
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,  # Center the title
            'xanchor': 'center',  # Ensure it's anchored in the center
            'yanchor': 'top'  # Keep it at the top
        },
        yaxis_title="",
        xaxis_title="ยอดขาย",
        xaxis_tickfont_size=16,
        yaxis_tickfont_size=16,
        font=dict(
            size=18,
        ),
        legend_title_text='',
    )
    st.plotly_chart(fig, theme="streamlit")

def get_group_province(data):
    data = data.query("amount_sold_format > 0")
    data = data[['marketplace', 'province', 'amount_sold_format']]
    data['province'] = data['province'].str.replace('จังหวัด', '')
    data['province'] = data['province'].str.replace('China', 'ต่างประเทศ')
    data_group = data.groupby(['marketplace', 'province'])['amount_sold_format'].sum().reset_index()
    data_sorted = data_group.sort_values(by='amount_sold_format', ascending=False)

    data_display = data_sorted[['province', 'amount_sold_format']]
    data_display.rename(columns={'province': 'จังหวัด', 'amount_sold_format': 'ยอดขาย'}, inplace=True)
    st.dataframe(data_display, hide_index=True)

    top_provinces_data = data_sorted.head(10)
    return top_provinces_data

st.header(":blue[การวิเคราะห์ที่ 7]", divider=True)
st.subheader("สินค้าใดในแต่ละจังหวัดมียอดขายสูงสุด")

data_doh = get_data()
data_plastic = get_additional_data("Lazada-Data_plastic")
data_plastic['marketplace'] = 'lazada'


desc_msg1 = '''
    **1. แป้งโดว์ - Shopee:**\n
    - กรุงเทพมหานคร: มียอดขายสูงสุดที่ 47,944 หน่วย
    - ขอนแก่น: ยอดขายสูงสุด 35,737 หน่วย
    - สมุทรปราการ: ยอดขายสูงสุด 10,167 หน่วย
'''
desc_msg2 = '''
    **2. แป้งโดว์ - Lazada:**\n
    - กรุงเทพมหานคร: มียอดขายสูงสุดที่ 13,792 หน่วย
    - ปทุมธานี: ยอดขายสูงสุด 6,944 หน่วย
    - ราชบุรี: ยอดขายสูงสุด 6,407 หน่วย
'''

desc_msg3 = '''
    **3. ดินน้ำมัน - Lazada:**\n
    - กรุงเทพมหานคร: มียอดขายสูงสุดที่ 14,873 หน่วย
    - ปทุมธานี: ยอดขายสูงสุด 4,272 หน่วย
    - สมุทรปราการ: ยอดขายสูงสุด 3,500 หน่วย
'''

summary_msg = '''
    จากข้อมูลนี้ เราจะเห็นว่ากรุงเทพมหานครเป็นจังหวัดที่มียอดขายสูงสุดในทุกแพลตฟอร์ม
'''

st.html("<strong style='font-size: 18px; text-decoration: underline;'>แป้งโดว์ (Play Dough)</strong>")
col1, col2 = st.columns([1, 3])
data_doh_shopee = data_doh[data_doh['marketplace'] == 'shopee']
data_doh_lazada = data_doh[data_doh['marketplace'] == 'lazada']
with col1:
    top_data_doh_provinces_shopee = get_group_province(data_doh_shopee)
with col2:
    get_bar_plot(top_data_doh_provinces_shopee, 'Shopee')

st.markdown(desc_msg1)
st.write("###")
cola, colb = st.columns([1, 3])
with cola:
    top_data_doh_provinces_lazada = get_group_province(data_doh_lazada)
with colb:
    get_bar_plot(top_data_doh_provinces_lazada, 'Lazada')

st.markdown(desc_msg2)

st.divider()
break_page()
st.html("<strong style='font-size: 18px; text-decoration: underline;'>ดินน้ำมัน (Clay)</strong>")
col1, col2 = st.columns([1, 3])
with col1:
    top_data_plastic_provinces = get_group_province(data_plastic)

with col2:
    get_bar_plot(top_data_plastic_provinces, 'Lazada')

st.markdown(desc_msg3)
st.markdown(summary_msg)
