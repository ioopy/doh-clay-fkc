import streamlit as st
from menu import menu_with_redirect
import pandas as pd
import plotly.express as px
from utils.func import break_page, get_color_map, hide_header_icons
from utils.load_data import get_additional_data, get_additional_reviews, get_data, get_reviews
from utils.text_editor import generate
import plotly.graph_objects as go

menu_with_redirect()
hide_header_icons()


def get_scatter_plot(data):
    reviews_category_order = ['ดี (Good)', 'เฉย ๆ (Neutral)', 'แย่ (Bad)']  
    fig = px.scatter(data, x="discount_range", y="reviews_category",
                    size="review_count", color="marketplace",color_discrete_map=get_color_map(),
                        hover_name="marketplace", size_max=60, category_orders={"reviews_category": reviews_category_order},
                        hover_data={
                        'review_count': ':.0f'
                    })
    fig.update_layout(
        xaxis_title="ส่วนลด (%)",
        yaxis_title="",
        xaxis_tickfont_size=16,
        yaxis_tickfont_size=16,
        # margin=dict(t=35),
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

def classify_review(rate):
    if rate in [1, 2]:
        return 'แย่ (Bad)'
    elif rate == 3:
        return 'เฉย ๆ (Neutral)'
    else:
        return 'ดี (Good)'

def display(data):
    data_display = data[['marketplace', 'store', 'per_discount', 'rating_star']]
    data_display = data_display.sort_values(by=['marketplace', 'per_discount'], ascending=True)
    data_display.rename(columns={'store': 'ชื่อร้านค้า', 'per_discount': 'ส่วนลด (%)', 'rating_star': 'คะแนน'}, inplace=True)
    st.dataframe(data_display, hide_index=True)

def clean_data(data, reviews):
    if data['per_discount'].dtype == 'object':
        data['per_discount'] = data['per_discount'].str.replace('%', '').str.replace('-', '')
    data['per_discount'] = pd.to_numeric(data['per_discount'], errors='coerce')

    transformed_reviews = reviews.groupby(['marketplace','shopId', 'itemId'])['rating_star'].apply(lambda x: ','.join(map(str, x))).reset_index()
    transformed_reviews = transformed_reviews.rename(columns={'rating_star': 'review_list'})

    data_filter = data[data['per_discount'] > 0]
    data_format = pd.merge(data_filter, transformed_reviews, on=['marketplace','shopId', 'itemId'])
    data_format = data_format[['marketplace', 'store', 'per_discount', 'review_list']]
    data_format['review_list'] = data_format['review_list'].str.split(',')
    # Use explode to create a new row for each review
    df_exploded = data_format.explode('review_list').reset_index(drop=True)
    # Convert the 'Review_List' column back to integers (optional)
    df_exploded['review_list'] = df_exploded['review_list'].astype(int)

    # Rename the column to 'Review_Rate' (optional for clarity)
    df_exploded = df_exploded.rename(columns={'review_list': 'rating_star'})
        
    df_exploded['reviews_category'] = df_exploded['rating_star'].apply(classify_review)
    return df_exploded

def prepare_data(data):
    bins = [0, 11, 21, 31, 41, 51]
    labels = ['0-10', '11-20', '21-30', '31-40', '41-50']
    data['discount_range'] = pd.cut(data['per_discount'], bins=bins, labels=labels, right=False)
    grouped_data = data.groupby(['discount_range', 'reviews_category', 'marketplace']).size().reset_index(name='review_count')
    # st.dataframe(grouped_data, hide_index=True)
    return grouped_data

st.header(":blue[การวิเคราะห์ที่ 6]", divider=True)
st.subheader("แพลตฟอร์มใดที่มีการรีวิวเชิงบวกมากที่สุดสำหรับสินค้าที่ได้รับการลดราคา")

data_doh = get_data()
reviews_doh = get_reviews()

data_plastic = get_additional_data("Lazada-Data_plastic")
data_plastic['marketplace'] = 'lazada'
reviews_plastic = get_additional_reviews("Lazada-Reviews_plastic")
reviews_plastic['marketplace'] = 'lazada'

desc_msg1 = '''
    **1. แป้งโดว์ - Shopee:**\n
    - รีวิวเชิงบวก (4-5 ดาว) มักอยู่ในช่วงส่วนลด **11-30%** โดยจำนวนรีวิวหมวดดีมีความหนาแน่นมากที่สุด
    - รีวิวเชิงลบ (1-2 ดาว) มีปรากฏน้อยในทุกช่วงส่วนลด
'''
desc_msg2 = '''
    **2. แป้งโดว์ - Lazada:**\n
    - รีวิวเชิงบวก (4-5 ดาว) ส่วนใหญ่กระจุกตัวในช่วงส่วนลด **21-30%**
    - รีวิวเชิงลบมีน้อยมาก แต่ยังคงมีการให้รีวิวหมวดดีในทุกช่วงส่วนลด
'''
desc_msg3 = '''
    **3. ดินน้ำมัน - Lazada:**\n
    - รีวิวเชิงบวก (4-5 ดาว) หนาแน่นที่สุดในช่วงส่วนลด **21-30%**
    - เช่นเดียวกับแป้งโดว์ รีวิวเชิงลบมีน้อยมาก และหมวดดีมีความเด่นชัดในช่วงส่วนลดนี้
'''
summary_msg = '''
    จากข้อมูลนี้ แสดงให้เห็นว่าช่วงส่วนลดที่มีรีวิวดีมากที่สุดสำหรับสินค้าทั้งสองแพลตฟอร์มคือช่วง **21-30%**
'''

st.html("<strong style='font-size: 18px; text-decoration: underline;'>แป้งโดว์ (Play Dough)</strong>")
data_doh_clean = clean_data(data_doh, reviews_doh)
display(data_doh_clean)
grouped_data_doh = prepare_data(data_doh_clean)
get_scatter_plot(grouped_data_doh)
st.markdown(desc_msg1)
st.markdown(desc_msg2)

st.divider()
break_page()
st.html("<strong style='font-size: 18px; text-decoration: underline;'>ดินน้ำมัน (Clay)</strong>")
data_plastic_clean = clean_data(data_plastic, reviews_plastic)
display(data_plastic_clean)
grouped_data_plastic = prepare_data(data_plastic_clean)
get_scatter_plot(grouped_data_plastic)
st.markdown(desc_msg3)
st.markdown(summary_msg)