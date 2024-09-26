import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from menu import menu_with_redirect
from utils.func import break_page, hide_header_icons
from utils.text_editor import generate
from utils.load_data import get_additional_data, get_additional_reviews, get_data, get_reviews
import plotly.express as px
from plotly.subplots import make_subplots

menu_with_redirect()
hide_header_icons()

def generate_tags(row):
    if 'แป้งโดว์คละสี' in row['type_color']:
        return "แพค"
    if 'ดินน้ำมันคละสี' in row['type_color']:
        return "แพค" 
    return "สี"

def format_data(reviews):
    reviews = reviews[['marketplace', 'type_color']]
    value_counts = reviews['type_color'].value_counts().reset_index()
    
    return value_counts

def display(data):
    data = data[['marketplace', 'type_color']]
    data = data.groupby(['marketplace', 'type_color']).size().reset_index(name='counts')
    data.rename(columns={'type_color': 'สี', 'counts': 'จำนวน'}, inplace=True)
    st.dataframe(data, hide_index=True)
    return None

def get_bar_plot(data, title):
    data = data.head(10)
    # Apply the function to create a new 'tag' column
    # data['tag'] = data.apply(generate_tags, axis=1)
    excluded_categories = ["ของเล่น + แป้งโดว์คละสี", "แป้งโดว์คละสี", "ดินน้ำมันคละสี", "ของเล่น + ดินน้ำมันคละสี"]
    sorted_df = data[~data['type_color'].isin(excluded_categories)].sort_values(by='count', ascending=True)
    sorted_df_final = pd.concat([
        data[data['type_color'].isin(excluded_categories)].sort_values(by='count', ascending=True),
        sorted_df,
    ])
    fig = px.bar(
        sorted_df_final,
        x='count', 
        y='type_color',
        orientation='h',
        text_auto='.s',
        # width=500, 
        height=500,
        
    )
    fig.update_traces(textfont_size=16, textangle=0, textposition="auto", cliponaxis=False)
    
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,  # Center the title
            'xanchor': 'center',  # Ensure it's anchored in the center
            'yanchor': 'top'  # Keep it at the top
        },
        yaxis_title="",
        xaxis_title="จำนวน",
        xaxis_tickfont_size=16,
        yaxis_tickfont_size=16,
        font=dict(
            size=18,
        ),
        legend_title_text='',
    )
    st.plotly_chart(fig, theme="streamlit")

def get_bar_plot2(data, title):
    data = data.head(12)
    data['tag'] = data.apply(generate_tags, axis=1)
    excluded_categories = ["ของเล่น + แป้งโดว์คละสี", "แป้งโดว์คละสี", "ดินน้ำมันคละสี", "ของเล่น + ดินน้ำมันคละสี"]
    sorted_df = data[~data['type_color'].isin(excluded_categories)].sort_values(by='count', ascending=True)

    sorted_df_final = pd.concat([
        sorted_df,
        data[data['type_color'].isin(excluded_categories)].sort_values(by='count', ascending=True)
    ])

    unique_tags = sorted_df_final['tag'].unique()

    fig = make_subplots(
        rows=2, 
        cols=1, 
        subplot_titles=["สี", "แพค"],   
        row_heights=[2/3, 1/3], 
        vertical_spacing=0.15   
    )

    tag_data = sorted_df_final[sorted_df_final['tag'] == 'สี']
    fig.add_trace(
        go.Bar(
            x=tag_data['count'], 
            y=tag_data['type_color'], 
            orientation='h',
            text=tag_data['count'],
            textposition='auto',
        ),
        row=1, col=1
    )

    tag_data = sorted_df_final[sorted_df_final['tag'] == 'แพค']
    fig.add_trace(
        go.Bar(
            x=tag_data['count'], 
            y=tag_data['type_color'], 
            orientation='h',  # Horizontal bar chart
            text=tag_data['count'],
            textposition='auto',
        ),
        row=2, col=1
    )

    fig.update_layout(
        height=700,  # Total height: 800px for the first subplot, 400px for the second
        title_text=title,
        title_x=0.5,  # Center the title
        xaxis_title="",
        font=dict(size=18),
        showlegend=False  # No legend needed
    )

    fig.update_traces(textfont_size=16, textangle=0, textposition="auto", cliponaxis=False)
    st.plotly_chart(fig, theme="streamlit")

st.header(":blue[การวิเคราะห์ที่ 8]", divider=True)
st.subheader("คุณลักษณะแบบไหนที่มียอดขายดี")

reviews_doh = get_reviews()


desc_msg1 = '''
    จากภาพรวมที่แสดงในกราฟ มีการแยกข้อมูลออกเป็นสองส่วน:

    **1. กราฟแท่งแสดงยอดขายตามสี:**\n
    - **สีชมพู** เป็นสีที่ขายได้มากที่สุด ด้วยจำนวน 104 หน่วย
    - ตามมาด้วย **สีเงิน** และ **สีฟ้า** โดยขายได้ 50 และ 38 หน่วยตามลำดับ
    - **สีเหลือง**, **เขียวอ่อน**, **ม่วง**, และ **เขียวเข้ม** ก็ได้รับความนิยมเช่นกัน โดยขายได้ประมาณ 20-30 หน่วย
    - สีอื่นๆ เช่น **น้ำเงิน** และ **ส้ม** มีจำนวนขายที่น้อยกว่า แต่ยังคงมียอดขายอยู่ในระดับที่น่าสนใจ
'''
desc_msg2 = '''
    **2. กราฟแท่งแสดงยอดขายของแพค:**\n
    - สินค้าชนิด **แป้งโดว์คละสี** ขายได้ 1,959 หน่วย ซึ่งเป็นแพคที่ขายดีที่สุด
    - ตามมาด้วย **ของเล่น + แป้งโดว์คละสี** ที่ขายได้ 1,663 หน่วย
'''
summary_msg1 = '''
    **สรุป:**\n 
    สีที่ขายดีมากที่สุดคือสีชมพู ในขณะที่สินค้าประเภทแพคที่คละสีขายได้ในปริมาณมากที่สุด
'''

desc_msg3 = '''
    **แป้งโดว์ - Shopee**\n

    **1. กราฟแท่งแสดงยอดขายตามสี:**\n
    - **สีชมพู** เป็นสีที่ขายดีที่สุดใน Shopee โดยมียอดขาย 42 หน่วย
    - **สีฟ้า** และ เขียวอ่อน มียอดขายตามลำดับ 22 และ 21 หน่วย
    - สีอื่น ๆ ที่ได้รับความนิยมรองลงมาคือ **ม่วง** (19 หน่วย), **น้ำเงิน** (17 หน่วย), และ **เหลือง** (15 หน่วย)
    - สีที่ขายได้น้อยที่สุดใน Shopee คือ **เขียว** (11 หน่วย) และ **ส้ม** (10 หน่วย)

    **2. กราฟแท่งแสดงยอดขายของแพค:**\n
    - สินค้าชนิด **ของเล่น + แป้งโดว์คละสี** มียอดขายสูงสุดใน Shopee โดยมียอดขาย 1,269 หน่วย
    - ตามมาด้วย **แป้งโดว์คละสี** ที่มียอดขาย 849 หน่วย
'''
summary_msg2 = '''
    **สรุป:**\n 
    ใน Shopee **สีชมพู** เป็นสีที่ขายดีที่สุด และสินค้าประเภทแพคที่มี **ของเล่น + แป้งโดว์คละสี** ขายได้ในปริมาณสูงสุด
'''

desc_msg4 = '''
    **แป้งโดว์ - Lazada**\n

    **1. กราฟแท่งแสดงยอดขายตามสี:**\n
    - **สีชมพู** เป็นสีที่ขายได้มากที่สุดใน Lazada โดยมียอดขายอยู่ที่ 62 หน่วย
    - **สีเงิน** ขายได้ในอันดับที่สอง จำนวน 50 หน่วย
    - สีอื่น ๆ ที่ได้รับความนิยมรองลงมาคือ **เขียวเข้ม** (19 หน่วย), **เหลือง** (17 หน่วย), **ฟ้า** (16 หน่วย) และ **แดง** (15 หน่วย)
    - สีที่มียอดขายน้อยที่สุดคือ **เขียวอ่อน** (9 หน่วย) และ **ขาว** (8 หน่วย)

    **2. กราฟแท่งแสดงยอดขายของแพค:**\n
    - สินค้าชนิด **แป้งโดว์คละสี** เป็นแพคที่ขายดีที่สุดใน Lazada โดยมียอดขาย 1,110 หน่วย
    - ตามมาด้วย **ของเล่น + แป้งโดว์คละสี** ที่มียอดขาย 394 หน่วย
'''
summary_msg3 = '''
    **สรุป:**\n 
    ใน Lazada สีที่ขายดีที่สุดคือ **สีชมพู** และสินค้าที่ขายดีที่สุดเป็นแบบแพคคละสี
'''

desc_msg5 = '''
    **ดินน้ำมัน - Lazada**\n

    **1. กราฟแท่งแสดงยอดขายตามสี:**\n
    - **สีขาว** เป็นสีที่ขายได้มากที่สุดใน Lazada โดยมียอดขายสูงถึง 974 หน่วย
    - **สีน้ำตาลแดง** ขายได้ 751 หน่วย และ **สีชมพู** ขายได้ 633 หน่วย ซึ่งเป็นอันดับที่สองและสามตามลำดับ
    - สีอื่น ๆ ที่ได้รับความนิยม เช่น **สีดำ** (553 หน่วย), **สีแดง** (538 หน่วย), และ **สีเหลือง** (444 หน่วย)
    - สีที่ขายได้น้อยกว่าแต่ยังคงมียอดขายคือ **น้ำเงิน** (388 หน่วย) และ **น้ำตาล** (380 หน่วย)

    **2. กราฟแท่งแสดงยอดขายของแพค:**\n
    - **ดินน้ำมันคละสี** มียอดขายสูงสุด โดยมียอดขาย 9,330 หน่วย
    - ตามมาด้วย **ของเล่น + ดินน้ำมันคละสี** ที่มียอดขาย 5,882 หน่วย
'''
summary_ms4 = '''
    **สรุป:**\n 
    สีที่ขายดีที่สุดใน Lazada คือ **สีขาว** และสินค้าประเภทแพค **ดินน้ำมันคละสี** มีการขายในปริมาณมากกว่าสินค้าประเภทอื่น
'''

st.html("<strong style='font-size: 18px; text-decoration: underline;'>แป้งโดว์ (Play Dough)</strong>")

count_all_doh = format_data(reviews_doh)
display(reviews_doh)
get_bar_plot2(count_all_doh, "แป้งโดว์ (ภาพรวม)")
st.markdown(desc_msg1)
st.markdown(desc_msg2)
st.markdown(summary_msg1)
break_page()
col1, col2 = st.columns([1,1])
with col1:
    shopee = reviews_doh[reviews_doh['marketplace'] == 'shopee']
    count_all_doh1 = format_data(shopee)
    get_bar_plot2(count_all_doh1, "แป้งโดว์ (Shopee)")
with col2:
    lazada = reviews_doh[reviews_doh['marketplace'] == 'lazada']
    count_all_doh2 = format_data(lazada)
    get_bar_plot2(count_all_doh2, "แป้งโดว์ (Lazada)")

st.markdown(desc_msg3)
break_page()
st.markdown(summary_msg2)

st.markdown(desc_msg4)
st.markdown(summary_msg3)

st.divider()
break_page()
st.html("<strong style='font-size: 18px; text-decoration: underline;'>ดินน้ำมัน (Clay)</strong>")
reviews_plastic = get_additional_reviews("Lazada-Reviews_plastic")
reviews_plastic['marketplace'] = 'lazada'
plastic = format_data(reviews_plastic)
display(reviews_plastic)
break_page()
get_bar_plot2(plastic, "ดินน้ำมัน (Lazada)")

st.markdown(desc_msg5)
break_page()
st.markdown(summary_ms4)