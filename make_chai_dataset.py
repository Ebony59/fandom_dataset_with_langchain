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
    dataset_sample = {}
    conversation = dict_conversation['conversation']
    dataset_sample['personalities'] = dict_summary['summary']
    dataset_sample['prompt'] = dict_summary['prompt']
    dataset_sample['character_1'] = dict_summary['character_1']
    dataset_sample['character_2'] = dict_summary['character_2']
    characters = [dict_summary['character_1'], dict_summary['character_2']]
    convo_list = []
    for convo_line in conversation.split('\n'):
        character = convo_line.split(':')[0]
        convo = convo_line.split(':')[1]

        do_train = (character in characters)

        convo_dict = {'content':convo, 'do_train':do_train, "role":character}
        convo_list.append(convo_dict)

    dataset_sample['conversations'] = convo_list

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
        dataset.append(sample_i)
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
    dataset.push_to_hub('ebony59/AO3_fandom_chai')
    
    dataset.save_to_disk('./output/fandom_dataset_chai')

main()