from langchain.docstore.document import Document
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter


def web_loader(fandom_id, chunk_size=1000, chunk_overlap=0, out_format = 'Document'):
    #web loader
    url = f"https://archiveofourown.org/works/{fandom_id}?view_full_work=true"


    loader = WebBaseLoader(url)
    docs = loader.load()

    # text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    #     separator='.', chunk_size=1000, chunk_overlap=0
    # )
    text_splitter = TokenTextSplitter(
        encoding_name="gpt2",
        # separator='\n',
        chunk_size=1000,  # Set the desired chunk size
        chunk_overlap=100,
    )
    split_docs = text_splitter.split_documents(docs)
    contents = [split_doc.page_content for split_doc in split_docs]
    
    if out_format == 'Document':
        docs = [Document(page_content=t) for t in contents]
    elif out_format == 'text':
        docs = contents
    
    return docs