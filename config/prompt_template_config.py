map_rel_template_string = """Write a summary of the story, with focus on characteristics and relationships of {character_1} and {character_2}, of the following fandom of {original_work}. 
Write the summary based on the fandom with reference to the original book as background.
The summary should mainly contain the context from the provided fandom. The original book is only a background reference.




{text}
"""

reduce_rel_template_string = """Given the following summary of the characteristics and relationship of {character_1} and {character_2} from parts of the fandom of {original_work}, give a more accurate summary of their personalities, and their relationship.
Write the summary based on the fandom with reference to the original book as background.
Don't wasite words on phrases like 'the fandom is about', 'in summary' or 'overall' in the summary. Start straight with the descriptions of their characteristics.


------
The summaries from parts of the fandom:
{character_description}
"""

map_sum_template_string = """Write a summary of the following fandom of {original_work}, based on the fandom with reference to the original book as background.
The main characters we should focus on are {character_1} and {character_2}.
The summary should mainly contain the context from the provided fandom. The original book is only a background reference.



{text}
"""

reduce_sum_template_string = """Given the following summary from parts of the fandom about {original_work}, give an overall summary of the characteristics of {character_1} and {character_2}, and their relationship.
Write the summary based on the fandom with reference to the original book as background.
Don't wasite words on phrases like 'the fandom is about', 'in summary' or 'overall' in the summary. Start straight with the descriptions of their characteristics.


------
The summaries from parts of the fandom:
{character_description}
"""

conversation_extraction_template_string = """The user will provide parts of a fandom based on {original_work}.
Find and reformat the paragraphs including engagement between two characters, and identify who is speaking by referring to the paragraphs before and after. If it's nor written directly, try to guess it by referring to paragraphs before and after.
If there is no engagement, gives no output. Don't make up anything.

The template for reformatting is:

character_name: "what he or she says, copy and paste from original text", *other descriptions(if any), copy and pasted from original text*

The content in "..." and *...* should be exactly copy and pasted from the original text, word by word as the original text provided. Don't make up any of the conversations.

For example, given the following text:
"I want to talk to you", A walked towards B, "It's urgent!"
"What do you want to say?" B stopped and looked back.

return:
A: "I want to talk to you." *walks towards B* "It's urgent."
B: "What do you want to say?" *stopped and looked back*


"""