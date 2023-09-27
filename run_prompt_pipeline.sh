#! /bin/bash
while IFS="," read -r fandom_id original_work
do
    python3.9 generate_prompt.py --fandom_id $fandom_id --original_work "$original_work"
done < <(tail -n +2 fandom_list.csv)
python3.9 dataset_count.py
python3 make_dataset.py