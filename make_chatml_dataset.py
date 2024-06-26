import pandas as pd
import numpy as np
import os
import argparse
from tqdm import tqdm

from datasets import load_dataset, Dataset, concatenate_datasets

from util.text_util import is_empty

global mistaken_names
mistaken_names = ['unknown','chapter','character','note','notes','she','he','it','him','her','them','overview']

def sample_to_dict(dict_summary, dict_conversation, bot):
    dataset_sample = []
    conversation = dict_conversation['conversation']
    dataset_sample.append({'content':dict_summary['summary'], 'role':'System'})
    characters = [dict_summary['character_1'], dict_summary['character_2']]
    for convo_line in conversation.split('\n'):
        character = convo_line.split(':')[0]
        convo = convo_line.split(':')[1]

        if character not in characters:
            continue

        if character == bot:
            convo_dict = {'content':convo, 'role':character}
        else:
            convo_dict = {'content':convo, 'role':'User'}

        dataset_sample.append(convo_dict)

    return dataset_sample

def character_count(dict_conversation):
    conversation = dict_conversation['conversation']
    characters = []
    for convo_line in conversation.split('\n'):
        character = convo_line.split(':')[0]
        if character not in characters:
            characters.append(character)
    return len(characters)

def multi_sample_to_dict(df_summary, df_conversation):
    dataset = []
    for i in range(len(df_conversation)):
        if (df_summary.loc[i,'character_1'].lower().strip() in mistaken_names) or (df_summary.loc[i,'character_2'].lower().strip() in mistaken_names):
            continue
        if is_empty(df_summary.loc[i,'summary']) or is_empty(df_conversation.loc[i,'conversation']):
            continue

        #filter out dataset with more than two characters
        if character_count(df_conversation.loc[i].to_dict()) > 2:
            continue

        try:
            sample_1 = sample_to_dict(df_summary.loc[i].to_dict(), df_conversation.loc[i].to_dict(),bot=df_summary.loc[i,'character_1'])
            if len(sample_1) > 1:
                dataset.append({'conversation':sample_1})
            sample_2 = sample_to_dict(df_summary.loc[i].to_dict(), df_conversation.loc[i].to_dict(),bot=df_summary.loc[i,'character_2'])
            if len(sample_2) > 1:
                dataset.append({'conversation':sample_2})
        except:
            continue
    return dataset

def main():
    conversation_df_list = os.listdir('./output/conversation_csv/')
    fandom_id_list = [conversation_df_name.split('.')[0].split('_')[1] for conversation_df_name in conversation_df_list]
    dataset_dict = []
    for fandom_id in tqdm(fandom_id_list):
        df_summary = pd.read_csv(f'./output/summary_csv/summary_{fandom_id}.csv')
        df_conversation = pd.read_csv(f'./output/conversation_csv/conversation_{fandom_id}.csv')
        dataset_dict = dataset_dict +  multi_sample_to_dict(df_summary, df_conversation)
    
    dataset_df = pd.DataFrame(data=dataset_dict)
    dataset = Dataset.from_pandas(dataset_df)
    dataset.push_to_hub('ebony59/AO3_fandom_chatbot_1to1')
    
    dataset.save_to_disk('./output/fandom_dataset_1to1')

main()