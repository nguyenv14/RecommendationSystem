#!/usr/bin/env python3
# Debug recommendation logic

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load hotels
hotels_df = pd.read_csv('datasets_extracted/tbl_hotel.csv')

print("All Hotels:")
for idx, hotel in hotels_df.iterrows():
    print(f"ID: {hotel['hotel_id']}, Name: {hotel['hotel_name']}")

print("\n\nSearch for hotel ID 2:")
hotel_2 = hotels_df[hotels_df['hotel_id'] == 2].iloc[0]
print(f"Name: {hotel_2['hotel_name']}")
print(f"Description: {hotel_2['hotel_desc'][:200]}...")

