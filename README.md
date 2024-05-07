Script to extract conversations and character summaries from fandoms on AO3 website(https://archiveofourown.org/), using Langchain.

`fandom_list.csv` is the list for the fandoms, containing the fandom_id and original_work. 
The fandom url given fandom_id: `url = f"https://archiveofourown.org/works/{fandom_id}?view_full_work=true"`

The logic is:
 - split the fandom into slices using `TokenTextSplitter`, with `chunk_size=1000`, `overlap=100`. 
 - Loop through the splitted docs. For each doc, find paragraphs containing engagement between characters, and reformatting them into converstational format. e.g. A: I love you. *hold B's hands*. This will be one sample of conversations.
 - For each conversation, extract the two main characters.
 - For each conversation, given two main characters, use map_reduce chain to summarise their personalities and relationships by reading the whole fandom, with the original work as reference. This will be one sample of summary.
 - To generate final dataset, we can pair the summaries and conversations and put into the resired format. 

The extracted summaries and conversations are saved in `output/`. 

run `python pipeline.py --fandom_id <fandom_id> --original_work <original_work>` to perform extraction for single fandom.

For batch processing, edit `fandom_list.csv` and run `source run_pipeline.sh`. It will loop through the fandoms, and process the ones that are not already in `./output`.

### Read this notion page for detailed writeup
https://wild-chatter-b52.notion.site/Generating-dataset-with-fandoms-novels-4d258eabbdb345549d8d4e00f54ceeba
