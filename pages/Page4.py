import streamlit as st
from menu import menu_with_redirect
import pandas as pd
from utils.func import break_page, hide_header_icons
from wordcloud import WordCloud
import plotly.express as px
import matplotlib.pyplot as plt
from collections import Counter
from pythainlp import word_tokenize
from pythainlp.corpus import thai_stopwords 
from pythainlp.util import normalize
from utils.load_data import get_additional_data, get_data, get_reviews
from utils.text_editor import generate, get_color_template
from pythainlp import Tokenizer
import re

menu_with_redirect()
hide_header_icons()

def format_data(data):
    data = data[data['amount_sold_format'] > 0]
    data['level'] = data['amount_sold_format'].apply(classify_sold_amount)
    data = data[['marketplace', 'store', 'amount_sold_format', 'level', 'product_name']]
    data['product_name_clean'] = data['product_name'].apply(preprocess_text)
    return data

def preprocess_text(text):
    if not isinstance(text, str):
        text = ''
    tokens = word_tokenize(text, engine='newmm', keep_whitespace=False)
    stop_words = set(thai_stopwords())
    stop_words.add("สำหรับ")
    stop_words.add("ความคิด")
    stop_words.add("คละ")
    stop_words.add("ของขวัญ")
    stop_words.add("ดินน้ำมัน")
    custom_tokenizer = Tokenizer(stop_words, keep_whitespace=False)

    # text = ' '.join(normalize(word) for word in custom_tokenizer.word_tokenize(text) if word not in stop_words)
    text = ' '.join(custom_tokenizer.word_tokenize(text))
    return text

def generate_wordcloud_and_count(text):
    # text = text.replace(" ", "")
    stop_words = set(thai_stopwords())
    stop_words.add("สำหรับ")
    stop_words.add("ความคิด")
    stop_words.add("คละ")
    stop_words.add("ของขวัญ")
    stop_words.add("ดินน้ำมัน")
    custom_tokenizer = Tokenizer(stop_words, keep_whitespace=False)

    # words = word_tokenize(text, engine='newmm', keep_whitespace=False)
    words = custom_tokenizer.word_tokenize(text)
    wordcloud = WordCloud(
                      font_path='data/thsarabunnew-webfont.ttf', 
                      stopwords=thai_stopwords(),
                      relative_scaling=0.3,
                      min_font_size=1,
                      background_color = "white",
                      max_words=50, # จำนวนคำที่เราต้องการจะแสดงใน Word Cloud
                      colormap='plasma', 
                      scale=3,
                      font_step=4,
                      collocations=True,
                      regexp=r"[ก-๙a-zA-Z']+", # Regular expression to split the input text into token
                      margin=2
                      ).generate(' '.join(words))
    
    # Calculate word count
    word_count = Counter(words)
    most_common_words = word_count.most_common(20)
    return wordcloud, most_common_words

def classify_sold_amount(sold_amount):
    if sold_amount > 1000:
        return 'High ยอดขายมากกว่า 1000'
    elif sold_amount >= 500 and sold_amount <= 1000:
        return 'Normal ยอดขาย 501-1000'
    else:
        return 'Low ยอดขายน้อยกว่า 500'
    
def gen_word(data):
    text = ' '.join(data['product_name_clean'].dropna().astype(str))
    text = re.sub(r'[^ก-๙a-zA-Z\s]', '', text)
    wordcloud, word_count = generate_wordcloud_and_count(text)

    # Display word cloud using Plotly
    fig = px.imshow(wordcloud.to_array())
    fig.update_layout(xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False))
    st.plotly_chart(fig)

    # Display word count
    # st.subheader("Word Count")
    word_count_df = pd.DataFrame(word_count, columns=['Word', 'Count']).sort_values(by='Count', ascending=False)
    # st.dataframe(word_count_df, hide_index=True)
    return word_count_df

def display(data):
    data_display = data[['product_name', 'amount_sold_format']]
    data_display.rename(columns={'product_name': 'ชื่อสินค้า', 'amount_sold_format': 'จำนวนที่ขายแล้ว'}, inplace=True)
    data_display = data_display.sort_values(by='จำนวนที่ขายแล้ว', ascending=False)
    st.dataframe(data_display, hide_index=True)

st.header(":blue[การวิเคราะห์ที่ 4]", divider=True)
st.subheader("คำใดควรเป็นชื่อผลิตภัณฑ์ที่โฆษณา")

data_doh = get_data()
data_plastic = get_additional_data("Lazada-Data_plastic")
data_plastic['marketplace'] = 'lazada'


title = '''
    จากผลลัพธ์การนับจำนวนคำในชื่อสินค้าของ **แป้งโดว์** และ **ดินน้ำมัน** สามารถสรุปได้ดังนี้:
'''
desc_msg1 = '''
    **แป้งโดว์ (Play Dough):**\n
    - คำว่า **"แป้งโดว์"** ปรากฏบ่อยถึง **118 ครั้ง** ในชื่อสินค้า ซึ่งเป็นคำหลักที่ควรนำมาใช้ในการตั้งชื่อผลิตภัณฑ์และการโฆษณา
    - คำที่เกี่ยวข้องอื่น ๆ เช่น **"ของเล่น"** หรือ **"เสริมพัฒนาการ"** สามารถนำมาใช้เพื่อดึงดูดความสนใจของผู้ปกครองที่สนใจซื้อของเล่นพัฒนาทักษะสำหรับเด็ก
    - การใช้คำเหล่านี้จะช่วยเพิ่มความน่าเชื่อถือและสร้างการจดจำแบรนด์ได้มากขึ้น
'''

desc_msg2 = '''
    **ดินน้ำมัน (Clay):**\n
    - คำว่า **"ดินน้ำมัน"** เป็นคำที่ปรากฏมากที่สุดในชื่อสินค้า โดยมีความถี่ถึง **280 ครั้ง** ซึ่งแสดงถึงความนิยมในการใช้คำนี้
    - คำว่า **"ไร้สารพิษ"** ก็เป็นอีกคำที่สำคัญ ซึ่งมักปรากฏบ่อย ๆ เนื่องจากลูกค้าสนใจเรื่องความปลอดภัยของผลิตภัณฑ์ การใช้คำนี้ในการโฆษณาจะช่วยสร้างความมั่นใจให้กับผู้บริโภคได้
    - การเน้นคำว่า "ดินน้ำมัน" และ "ไร้สารพิษ" จะช่วยให้สินค้าดูมีคุณภาพและเชื่อถือได้มากขึ้นในสายตาของลูกค้า
'''
summary_msg = '''
    **ข้อเสนอแนะในการใช้คำโฆษณา:**\n
    - **แป้งโดว์**: ชื่อสินค้าควรเน้นคำว่า "แป้งโดว์" และสามารถเพิ่มคำอย่าง "ของเล่น" หรือ "เสริมพัฒนาการ" เพื่อดึงดูดความสนใจ
    - **ดินน้ำมัน**: ควรใช้คำว่า "ดินน้ำมัน" และ "ไร้สารพิษ" ในการโฆษณา เนื่องจากเป็นคำที่พบบ่อยและสื่อถึงความปลอดภัยของผลิตภัณฑ์
'''


st.html("<strong style='font-size: 18px; text-decoration: underline;'>แป้งโดว์ (Play Dough)</strong>")
data_doh = format_data(data_doh)
display(data_doh)
word_count_df = gen_word(data_doh)
col1, col2 = st.columns([1, 3])

with col1:
    st.dataframe(word_count_df, hide_index=True)

with col2:
    st.markdown(desc_msg1)

st.divider()
break_page()
st.html("<strong style='font-size: 18px; text-decoration: underline;'>ดินน้ำมัน (Clay)</strong>")
data_plastic = format_data(data_plastic)
display(data_plastic)
word_count_df = gen_word(data_plastic)
col1, col2 = st.columns([1, 3])

with col1:
    st.dataframe(word_count_df, hide_index=True)

with col2:
    st.markdown(desc_msg2)

st.markdown("##")
st.markdown(summary_msg)
