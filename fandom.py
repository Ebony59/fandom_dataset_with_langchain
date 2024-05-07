import pandas as pd
from tqdm import tqdm
import json

from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.combine_documents.map_reduce import ReduceDocumentsChain, MapReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import create_extraction_chain

from util.load_fandom import web_loader
from config.prompt_template_config import *

global mistaken_names
mistaken_names = ['unknown','chapter','character','note','notes','she','he','it','him','her','them','overview']

class fandom:
    def __init__(self, fandom_id, original_work="", conversation_df = pd.DataFrame(), summary_df = pd.DataFrame(), docs=[]):
        self.fandom_id = fandom_id
        self.original_work = original_work
        self.conversation_df = conversation_df
        self.summary_df = summary_df
        self.docs = docs

    def get_url(self):
        return f"https://archiveofourown.org/works/{self.fandom_id}?view_full_work=true"
    
    def load_document(self, doc_format='Document'):
        docs = web_loader(fandom_id = self.fandom_id, out_format=doc_format)
        self.docs = docs
        # return docs

    def map_reduce_chain(self, docs, map_template_string, reduce_template_string, character_1, character_2):
        MAP_PROMPT = PromptTemplate(input_variables=["character_1", "character_2", "original_work", "text"], template=map_template_string)
        REDUCE_PROMPT = PromptTemplate(input_variables=["character_1", "character_2", "original_work","character_description"], template=reduce_template_string)

        # LLM to use in map and reduce stages 
        llm = OpenAI()
        map_llm_chain = LLMChain(llm=llm, prompt=MAP_PROMPT)
        reduce_llm_chain = LLMChain(llm=llm, prompt=REDUCE_PROMPT)

        # Takes a list of documents and combines them into a single string
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_llm_chain,
            document_variable_name="character_description",
        )

        # Combines and iteravely reduces the mapped documents 
        reduce_documents_chain = ReduceDocumentsChain(
                # This is final chain that is called.
                combine_documents_chain=combine_documents_chain,
                # If documents exceed context for `combine_documents_chain`
                collapse_documents_chain=combine_documents_chain,
                # The maximum number of tokens to group documents into
                token_max=3000)

        # Combining documents by mapping a chain over them, then combining results with reduce chain
        combine_documents = MapReduceDocumentsChain(
            # Map chain
            llm_chain=map_llm_chain,
            # Reduce chain
            reduce_documents_chain=reduce_documents_chain,
            # The variable name in the llm_chain to put the documents in
            document_variable_name="text",
            output_key="output_text",
        )

        return_length = 0
        iterations = 0

        while (return_length < 10) and (iterations < 10):
            map_reduce_result = combine_documents({"input_documents": docs, "character_1":character_1, "character_2":character_2, "original_work":self.original_work}, return_only_outputs=True)
            return_length = len(map_reduce_result['output_text'].replace('\n------\n','').strip())
            iterations += 1

        return map_reduce_result['output_text'].replace('\n------\n','').strip()
    
    def get_character_summary(self, character_1, character_2):
        if self.docs == []:
            docs = self.load_document(doc_format='Document')
        docs = self.docs
        summary_from_relationships = self.map_reduce_chain(docs=docs, 
                                                           map_template_string=map_rel_template_string, 
                                                           reduce_template_string=reduce_rel_template_string,
                                                           character_1 = character_1,
                                                           character_2 = character_2)
        # summary_from_story = self.map_reduce_chain(docs=docs, 
        #                                            map_template_string=map_sum_template_string, 
        #                                            reduce_template_string=reduce_sum_template_string,
        #                                            character_1 = character_1,
        #                                            character_2 = character_2)
        # final_output = summary_from_relationships + ' ' + summary_from_story

        final_output = summary_from_relationships
        return final_output

    def get_original_work_character_summary(self, character_1, character_2,model='gpt-3.5-turbo'):
        llm = llm = OpenAI(model_name=model,temperature=0)
        prompt = PromptTemplate.from_template("Write the personality of {character_1}, and the personality of {character_2}, and their relationships, based on {original_work}.")
        summary = llm.predict(prompt.format(character_1=character_1, character_2=character_2, original_work=self.original_work))
        return summary

    def stuff_chain(self, doc, system_message, model='gpt-3.5-turbo'):
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_message)
        book_message_prompt = HumanMessagePromptTemplate.from_template("{text}")
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, book_message_prompt])
        chain = LLMChain(
            llm=ChatOpenAI(model_name=model, temperature=0),
            prompt=chat_prompt,
        )
        convo = chain(doc)['text']
        return convo
    
    def extract_main_characters(self, inp, temperature=0, model='gpt-3.5-turbo'):
        schema = {
            "properties": {
                "main_character_1:": {"type": "string"},
                "main_character_2:": {"type": "string"},
            },
        }
        characters = []

        llm = ChatOpenAI(temperature=temperature, model=model)
        chain = create_extraction_chain(schema, llm)
        characters = chain.run(inp)

        return characters

    def get_conversation_df(self):
        if self.docs == []:
            docs = self.load_document()
        else:
            docs = self.docs
        docs = [doc.page_content for doc in docs]
        
        conversation_list = []
        character_1_list = []
        character_2_list = []

        for doc in tqdm(docs):
            convo = self.stuff_chain(doc=doc, system_message=conversation_extraction_template_string.format(original_work=self.original_work))

            # clean extracted convo
            convo_splited = convo.split('\n')
            good_conversation_lines = []
            for line_idx, line_convo in enumerate(convo_splited):
                if len(line_convo.split(':')[0].split(' ')) < 3 and line_convo.split(':')[0].lower().strip() not in mistaken_names:
                    good_conversation_lines.append(line_convo.replace('"','').strip())

            if len(good_conversation_lines) < 4:
                continue

            convo = '\n'.join(good_conversation_lines)
            convo = convo.strip()

            # character extraction and sanity check
            characters = self.extract_main_characters(inp=convo)

            try:
                temp_character_1, temp_character_2 = characters[0]['main_character_1'], characters[0]['main_character_2']
            except:
                continue
            if temp_character_1 == '' or temp_character_2 == '':
                continue
            if temp_character_1.split()[0].lower() in mistaken_names or temp_character_2.split()[0].lower() in mistaken_names:
                continue

            #append result
            character_1_list.append(temp_character_1)
            character_2_list.append(temp_character_2)
            conversation_list.append(convo)

        conversation_df = pd.DataFrame(data={'fandom_id':self.fandom_id, 'character_1':character_1_list,'character_2':character_2_list,'conversation':conversation_list})
        self.conversation_df = conversation_df
        
        return conversation_df

    def get_summary_df(self, character_1_list=[], character_2_list=[]):
        if len(self.conversation_df) > 0:
            character_1_list = self.conversation_df['character_1']
            character_2_list = self.conversation_df['character_2']
        
        if len(character_1_list) == 0 or len(character_2_list) == 0 or len(character_1_list) != len(character_2_list):
            return pd.DataFrame()
        
        summary_list = []
        existing_character_pairs = []
        existing_summary_list = []

        for i in tqdm(range(len(character_1_list))):
            character_1 = character_1_list[i]
            character_2 = character_2_list[i]

            character_pair = (character_1, character_2)
            character_pair_reverse = (character_2, character_1)

            if character_pair in existing_character_pairs:
                pair_index = existing_character_pairs.index(character_pair)
                summary = existing_summary_list[pair_index]
            elif character_pair_reverse in existing_character_pairs:
                pair_index = existing_character_pairs.index(character_pair_reverse)
                summary = existing_summary_list[pair_index]
            else:
                summary = self.get_character_summary(character_1 = character_1, character_2=character_2)
                existing_character_pairs.append(character_pair)
                existing_summary_list.append(summary)

            summary_list.append(summary)
        
        summary_df = pd.DataFrame(data={'fandom_id':self.fandom_id, 'character_1':character_1_list,'character_2':character_2_list,'summary':summary_list})
        self.summary_df = summary_df

        return summary_df
    
    def get_prompt(self,model='gpt-3.5-turbo'):
        existing_character_pairs = []
        existing_prompt_list = []
        llm = ChatOpenAI(model=model)
        for i in range(len(self.summary_df)):
            character_1 = self.summary_df.loc[i,'character_1']
            character_2 = self.summary_df.loc[i,'character_2']
            character_pair = (character_1, character_2)
            character_pair_reverse = (character_2, character_1)
            if character_pair in existing_character_pairs:
                pair_index = existing_character_pairs.index(character_pair)
                prompt = existing_prompt_list[pair_index]
            elif character_pair_reverse in existing_character_pairs:
                pair_index = existing_character_pairs.index(character_pair_reverse)
                prompt = existing_prompt_list[pair_index]
            else:
                prompt = llm.predict(generation_prompt.format(character_1=character_1, character_2=character_2, original_work=self.original_work,summary=self.summary_df.loc[i,'summary']),temperature=0.9)
                existing_character_pairs.append(character_pair)
                existing_prompt_list.append(prompt)

            self.summary_df.loc[i,'prompt']=prompt
        
        self.summary_df = self.summary_df.loc[:,~self.summary_df.columns.str.contains('^Unnamed')]

    def clean_conversation_df(self):
        temp_conversation_df = self.conversation_df
        for i in range(len(self.conversation_df)):
            character_1 = temp_conversation_df.loc[i,'character_1']
            character_2 = temp_conversation_df.loc[i,'character_2']
            if (character_1.split()[0].lower() in mistaken_names) or (character_2.split()[0].lower() in mistaken_names):
                temp_conversation_df = temp_conversation_df.drop(index=i)
        temp_conversation_df.reset_index(inplace=True, drop=True)
        self.conversation_df = temp_conversation_df

        return temp_conversation_df

    def write_to_csv(self, write_conversation = True, write_summary=True):
        path_f = open('./config/paths.json')
        path_dict = json.load(path_f)
        
        summary_csv_path = path_dict['summary_csv_dir'] + f'summary_{self.fandom_id}.csv'
        conversation_csv_path = path_dict['conversation_csv_dir'] + f'conversation_{self.fandom_id}.csv'

        if write_conversation:
            self.conversation_df.to_csv(conversation_csv_path)
        
        if write_summary:
            self.summary_df.to_csv(summary_csv_path)
                

class fandom_character_pair(fandom):
    def __init__(self, fandom_id, original_work, character_1, character_2, summary=""):
        super().__init__(fandom_id, original_work)
        self.character_1 = character_1
        self.character_2 = character_2
        self.summary = summary
    
    def get_character_summary(self):
        summary = super().get_character_summary(character_1 = self.character_1, character_2=self.character_2)
        self.summary = summary
        return summary
    
    def get_character_summary_dict(self):
        summary_dict = {'fandom_id':self.fandom_id, 'character_1':self.character_1,'character_2':self.character_2,'summary':self.summary}
        return summary_dict