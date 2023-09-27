from fandom import *
import argparse
import os

parser = argparse.ArgumentParser(description='Pipeline to generate prompt(sample conversations) given summaries.')
parser.add_argument('--fandom_id',required=True,help='The id included in the fandom url')
parser.add_argument('--original_work',help='The original work of the fandom',default='')
parser.add_argument('--rewrite', help='wether or not rewrite existing data', type=bool, default=False)

args = parser.parse_args()

def main():
    fandom_id = args.fandom_id
    original_work = args.original_work

    if args.rewrite == False:
        summary_csv = pd.read_csv(f'./output/summary_csv/summary_{fandom_id}.csv')
        if 'prompt' in summary_csv.columns:
            print(f'prompt already generated for {fandom_id}.')

    print(f'Processing {fandom_id}...')

    fd = fandom(fandom_id=fandom_id,original_work=original_work)
    fd.get_prompt()
    fd.write_to_csv(write_conversation=False,write_summary=True)

    print(f'Finished processing {fandom_id}, produced {len(fd.summary_df)} data.')

main()