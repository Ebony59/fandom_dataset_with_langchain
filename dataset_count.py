import os
import pandas as pd

conversation_csv_list = os.listdir('./output/conversation_csv/')
processed_fandom_id_list = [file.split('_')[1].split('.')[0] for file in conversation_csv_list]

data_count = 0
for conversation_csv in conversation_csv_list:
    conversation_csv_path = './output/conversation_csv/' + conversation_csv
    df = pd.read_csv(conversation_csv_path)
    data_count += len(df)

print(f"There are {data_count} samples generated so far.")
