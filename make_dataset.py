import pandas as pd
import numpy as np
import os
import argparse
from tqdm import tqdm

from datasets import load_dataset, Dataset, concatenate_datasets

from util.text_util import is_empty

global mistaken_names
mistaken_names = ['unknown','chapter','character','note','notes','she','he','it','him','her','them','overview']

def sample_to_dict(dict_summary, dict_conversation):
    dataset_sample = []
    conversation = dict_conversation['conversation']
    dataset_sample.append({'content':dict_summary['summary'], 'do_train':False, 'role':'System'})
    characters = [dict_summary['character_1'], dict_summary['character_2']]
    for convo_line in conversation.split('\n'):
        character = convo_line.split(':')[0]
        convo = convo_line.split(':')[1]

        do_train = (character in characters)

        convo_dict = {'content':convo, 'do_train':do_train, "role":character}
        dataset_sample.append(convo_dict)

    return dataset_sample

def multi_sample_to_dict(df_summary, df_conversation):
    dataset = []
    for i in range(len(df_conversation)):
        if (df_summary.loc[i,'character_1'].lower().strip() in mistaken_names) or (df_summary.loc[i,'character_2'].lower().strip() in mistaken_names):
            continue
        if is_empty(df_summary.loc[i,'summary']) or is_empty(df_conversation.loc[i,'conversation']):
            continue
        try:
            sample_i = sample_to_dict(df_summary.loc[i].to_dict(), df_conversation.loc[i].to_dict())
        except:
            continue
        dataset.append({'conversation':sample_i})
    return dataset

def main():
    conversation_df_list = os.listdir('./output/conversation_csv/')
    fandom_id_list = [conversation_df_name.split('.')[0].split('_')[1] for conversation_df_name in conversation_df_list]
    dataset_dict = []
    for fandom_id in tqdm(fandom_id_list):
        df_summary = pd.read_csv(f'./output/summary_csv/summary_{fandom_id}.csv')
        df_conversation = pd.read_csv(f'./output/conversation_csv/conversation_{fandom_id}.csv')
        dataset_dict = dataset_dict +  multi_sample_to_dict(df_summary, df_conversation)
    
    dataset = Dataset.from_list(dataset_dict)
    
    dataset.save_to_disk('./output/fandom_dataset')

main()