import streamlit as st
from menu import menu_with_redirect
import pandas as pd
import plotly.express as px
from utils.func import break_page, get_color_map, hide_header_icons
from utils.load_data import get_additional_data, get_data, get_reviews
from utils.text_editor import generate

menu_with_redirect()
hide_header_icons()

def format_data(data):
    data = data.query("amount_sold_format>0")
    data = data.query("discount_price_format>0")
    data['star_review'] = pd.to_numeric(data['star_review'], errors='coerce')
    data = data[data['star_review'] > 0]
    data = data[['marketplace', 'store', 'star_review', 'discount_price_format']]

    bins = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1101]
    labels = ['0-100', '101-200', '201-300', '301-400', '401-500', '501-600', '601-700', '701-800', '801-900', '901-1000', '1001-1100']
    data['price_range'] = pd.cut(data['discount_price_format'], bins=bins, labels=labels, right=False)
    return data

def get_bubble_plot(data):
    fig_bubble = px.scatter(
        data,
        x='discount_price_format',
        y='star_review',
        size='count',
        color='marketplace',
        labels={'star_review': 'Star Review', 'discount_price_format': 'Price', 'marketplace': 'Marketplace'},
        size_max=60, color_discrete_map=get_color_map()
    )
    fig_bubble.update_layout(
        xaxis_title="ช่วงราคาขาย",
        yaxis_title="คะแนนรีวิว",
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
        legend_title_text='',
    )
    st.plotly_chart(fig_bubble, theme="streamlit")

def display(data):
    data_display = data[['marketplace', 'store', 'star_review', 'discount_price_format']]
    data_display.rename(columns={'store': 'ชื่อร้านค้า', 'star_review': 'คะแนนรีวิว', 'discount_price_format': 'ราคาขาย'}, inplace=True)
    st.dataframe(data_display, hide_index=True)

def prepare(data):
    data_group = data[['marketplace', 'star_review', 'discount_price_format']]
    bubble_data = data.groupby(['marketplace','discount_price_format', 'star_review']).size().reset_index(name='count')
    # st.write(bubble_data)
    return bubble_data

st.header(":blue[การวิเคราะห์ที่ 5]", divider=True)
st.subheader("คะแนนรีวิวเฉลี่ยที่สูงสุดอยู่ในช่วงราคาสินค้าใด")

data_doh = get_data()
data_plastic = get_additional_data("Lazada-Data_plastic")
data_plastic['marketplace'] = 'lazada'


desc_msg1 = '''
    **แป้งโดว์ (Play Dough):**\n
    - **Shopee**: ช่วงราคาที่มีคะแนนรีวิวเฉลี่ยสูงสุดคือ **51-100 บาท** โดยมีคะแนนเฉลี่ยอยู่ที่ **4.78** ตามมาด้วยช่วงราคา **201-500 บาท** ที่มีคะแนนเฉลี่ย **4.75**
    - **Lazada**: ช่วงราคาที่มีคะแนนรีวิวเฉลี่ยสูงสุดคือ **101-200 บาท** โดยมีคะแนนเฉลี่ย **4.93** รองลงมาคือช่วงราคา **0-50 บาท** ที่มีคะแนนเฉลี่ย **4.93** ใกล้เคียงกัน
'''

desc_msg2 = '''
    **ดินน้ำมัน (Clay):**\n
    - **Lazada**: ช่วงราคาที่มีคะแนนรีวิวเฉลี่ยสูงสุดคือ **101-200 บาท** โดยมีคะแนนเฉลี่ย **4.97** รองลงมาคือช่วงราคา **0-50 บาท** ที่มีคะแนนเฉลี่ย **4.94**
'''
summary_msg = '''
    **สรุป:**\n
    - **Shopee** สำหรับแป้งโดว์ ช่วงราคาที่มีคะแนนรีวิวสูงสุดอยู่ที่ **51-100 บาท** ซึ่งน่าจะเป็นช่วงราคาที่ลูกค้าให้ความพึงพอใจสูงสุด
    - **Lazada** สำหรับทั้งแป้งโดว์และดินน้ำมัน ช่วงราคาที่มีคะแนนรีวิวสูงสุดคือ **101-200 บาท** ซึ่งอาจบ่งบอกถึงความสมดุลของราคากับคุณภาพที่ลูกค้าพอใจมากที่สุด
'''


st.html("<strong style='font-size: 18px; text-decoration: underline;'>แป้งโดว์ (Play Dough)</strong>")
data_doh = format_data(data_doh)
display(data_doh)
bubble_data_doh = prepare(data_doh)
get_bubble_plot(bubble_data_doh)
st.markdown(desc_msg1)

st.divider()
break_page()
st.html("<strong style='font-size: 18px; text-decoration: underline;'>ดินน้ำมัน (Clay)</strong>")
data_plastic = format_data(data_plastic)
display(data_plastic)
bubble_data_plastic = prepare(data_plastic)
get_bubble_plot(bubble_data_plastic)
st.markdown(desc_msg2)

break_page()
st.markdown(summary_msg)
