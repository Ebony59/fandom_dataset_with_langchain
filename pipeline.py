from fandom import *
import argparse
import os

parser = argparse.ArgumentParser(description='Pipeline to generate conversations and summaries.')
parser.add_argument('--fandom_id',required=True,help='The id included in the fandom url')
parser.add_argument('--original_work',help='The original work of the fandom',default='')
parser.add_argument('--rewrite', help='wether or not rewrite existing data', type=bool, default=False)

args = parser.parse_args()


def main():
    fandom_id = args.fandom_id
    original_work = args.original_work
    
    if args.rewrite == False:
        processed_fandom_list = os.listdir('./output/summary_csv/')
        processed_fandom_id_list = [file.split('_')[1].split('.')[0] for file in processed_fandom_list]
        if fandom_id in processed_fandom_id_list:
            print(f'{fandom_id} already processed')
            return

    print(f'Processing {fandom_id}...')
    
    fd = fandom(fandom_id=fandom_id,original_work=original_work)
    fd.load_document()
    fd.get_conversation_df()
    fd.clean_conversation_df()
    fd.get_summary_df()
    fd.write_to_csv()

    print(f'Finished processing {fandom_id}, produced {len(fd.summary_df)} data.')

main()