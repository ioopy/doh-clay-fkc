import streamlit as st
from menu import menu_with_redirect
import pandas as pd
import plotly.express as px
from utils.func import break_page, get_color_map, hide_header_icons
from utils.load_data import get_additional_data, get_data, get_reviews
from utils.text_editor import generate, get_color_template

menu_with_redirect()
hide_header_icons()

def classify_sold_amount(sold_amount):
    if sold_amount > 1000:
        return 'High ยอดขายมากกว่า 1000'
    elif sold_amount >= 500 and sold_amount <= 1000:
        return 'Normal ยอดขาย 501-1000'
    else:
        return 'Low ยอดขายน้อยกว่า 500'

def get_scatter_plot(data):
    scatter_fig = px.scatter(data, 
                            x='per_discount', 
                            y='amount_sold_format', 
                            color='marketplace', 
                            symbol='marketplace', 
                            color_discrete_map=get_color_map(),
                            labels={'per_discount': 'ส่วนลด (%)', 'amount_sold_format': 'ยอดขาย'},)

    scatter_fig.update_layout(
        xaxis_title="ส่วนลด (%)",
        yaxis_title="ยอดขาย",
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
    st.plotly_chart(scatter_fig, theme="streamlit")

def format_data(data):
    if data['per_discount'].dtype == 'object':
        data['per_discount'] = data['per_discount'].str.replace('%', '').str.replace('-', '')

    data['per_discount'] = pd.to_numeric(data['per_discount'], errors='coerce')
    data['per_discount'] = data['per_discount'].fillna(0)
    data['level'] = data['amount_sold_format'].apply(classify_sold_amount)
    return data

def prepare_data(data):
    data_doh_analyze = data[['marketplace', 'level', 'per_discount', 'amount_sold_format', 'discount_price_format']]
    data_doh_analyze = data_doh_analyze[data_doh_analyze['per_discount'] > 0]
    data_doh_analyze = data_doh_analyze[data_doh_analyze['amount_sold_format'] > 0]
    # st.write("raw")
    # st.write(data_doh_analyze)
    return data_doh_analyze

st.header(":blue[การวิเคราะห์ที่ 3]", divider=True)
st.subheader("ความสัมพันธ์ระหว่างเปอร์เซ็นต์ส่วนลดกับยอดขายเป็นอย่างไร")

data_doh = get_data()
data_plastic = get_additional_data("Lazada-Data_plastic")
data_plastic['marketplace'] = 'lazada'

title = '''
    จากกราฟที่แสดงความสัมพันธ์ระหว่างเปอร์เซ็นต์ส่วนลดและยอดขายแยกตามแพลตฟอร์ม สามารถวิเคราะห์ได้ดังนี้:
'''
desc_msg1 = '''
    **1. แป้งโดว์ - Shopee:**\n
    - ไม่มีความสัมพันธ์ที่ชัดเจนระหว่างเปอร์เซ็นต์ส่วนลดและยอดขาย การกระจายตัวของข้อมูลค่อนข้างไม่เป็นระเบียบ
    - มีบางกรณีที่ส่วนลดต่ำ เช่น ประมาณ 20% กลับมียอดขายสูงเกิน 10,000 หน่วย ซึ่งแสดงว่าปัจจัยอื่น ๆ อาจมีผลต่อยอดขายมากกว่าการให้ส่วนลด
'''
desc_msg2 = '''
    **2. แป้งโดว์ - Lazada:**\n
    - เช่นเดียวกับ Shopee ความสัมพันธ์ระหว่างเปอร์เซ็นต์ส่วนลดและยอดขายยังไม่ชัดเจน การให้ส่วนลดสูงไม่ได้ส่งผลให้ยอดขายเพิ่มขึ้นอย่างเห็นได้ชัด
    - มีบางรายการที่ส่วนลดต่ำ (น้อยกว่า 20%) กลับมียอดขายสูงกว่ารายการที่มีส่วนลดสูง ซึ่งแสดงว่าการลดราคามากอาจไม่ใช่ปัจจัยหลักที่ทำให้สินค้าขายดีบน Lazada
'''
desc_msg3 = '''
    **3. ดินน้ำมัน - Lazada:**\n
    - ดินน้ำมันใน Lazada แสดงให้เห็นความสัมพันธ์ที่ชัดเจนขึ้นระหว่างเปอร์เซ็นต์ส่วนลดและยอดขาย โดยเฉพาะเมื่อส่วนลดอยู่ในช่วง 60-90% ยอดขายจะเพิ่มขึ้นอย่างชัดเจน
    - การให้ส่วนลดสูงมาก เช่น 80-90% มีแนวโน้มช่วยกระตุ้นยอดขายได้อย่างมีประสิทธิภาพในกรณีของดินน้ำมัน
'''
summary_msg = '''
    **สรุป:** \n
    - **Shopee และ Lazada สำหรับแป้งโดว์**: ส่วนลดไม่ได้เป็นปัจจัยหลักที่กระตุ้นยอดขาย เนื่องจากมีหลายกรณีที่สินค้าลดราคาน้อยกลับขายได้มากกว่า
    - **Lazada สำหรับดินน้ำมัน**: ส่วนลดมีผลกระทบอย่างชัดเจนต่อยอดขาย โดยเฉพาะส่วนลดสูงสุดในช่วง 60-90% ช่วยเพิ่มยอดขายได้อย่างมาก
'''

st.html("<strong style='font-size: 18px; text-decoration: underline;'>แป้งโดว์ (Play Dough)</strong>")
data_doh = format_data(data_doh)
data_doh_analyze = prepare_data(data_doh)
get_scatter_plot(data_doh_analyze)
st.markdown(desc_msg1)
st.markdown(desc_msg2)

st.divider()
break_page()
st.html("<strong style='font-size: 18px; text-decoration: underline;'>ดินน้ำมัน (Clay)</strong>")
data_plastic = format_data(data_plastic)
data_plastic_analyze = prepare_data(data_plastic)
get_scatter_plot(data_plastic_analyze)

st.markdown(desc_msg3)
st.markdown(summary_msg)
