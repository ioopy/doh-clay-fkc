import pandas as pd
from utils.func import convert_amount_sold

def rename_columns(data):
    return data.rename(columns={'itemid': 'itemId', 'shopid': 'shopId'})

def format_sales_data(data):
    data['amount_sold_format'] = data['amount_sold'].apply(convert_amount_sold)
    data['discount_price_format'] = data['discount_price'].fillna(0)
    data['total_value'] = data['amount_sold_format'] * data['discount_price_format']
    return data

def format_star_review(data):
    data['star_review'].fillna(0, inplace=True)
    data['star_review'] = data['star_review'].apply(lambda x: f"{x:.1f}")
    return data

def format_reviews_date_data(data):
    data['date_column'] = pd.to_datetime(data['review_date'])
    data['year'] = data['date_column'].dt.year
    data['month'] = data['date_column'].dt.month
    data['day'] = data['date_column'].dt.day
    return data

def get_data():
    shopee_data = pd.read_csv('data/Shopee-Data.csv')
    lazada_data = pd.read_csv('data/Lazada-Data.csv')

    # Rename columns
    shopee_data = rename_columns(shopee_data)
    lazada_data = rename_columns(lazada_data)

    # Format sales and discount data
    shopee_data = format_sales_data(shopee_data)
    lazada_data = format_sales_data(lazada_data)

    # Format star reviews
    shopee_data = format_star_review(shopee_data)
    lazada_data = format_star_review(lazada_data)

    return pd.concat([shopee_data, lazada_data])

def get_reviews():
    shopee_reviews = pd.read_csv('data/Shopee-Reviews.csv')
    lazada_reviews = pd.read_csv('data/Lazada-Reviews.csv')
    combined_reviews = pd.concat([shopee_reviews, lazada_reviews])

    format_reviews_date_data(combined_reviews)
    # combined_reviews['date_column'] = combined_reviews['date_column'].dt.strftime('%Y-%m-%d')

    return combined_reviews

def get_additional_data(filename):
    data = pd.read_csv(f'data/{filename}.csv')
    data = rename_columns(data)
    data = format_sales_data(data)
    data = format_star_review(data)

    return pd.concat([data])

def get_additional_reviews(filename):
    data = pd.read_csv(f'data/{filename}.csv')
    format_reviews_date_data(data)

    return data