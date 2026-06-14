from .BaseController import BaseController
from .ProjectController import ProjectController
from models import ProccessingEnum
from langchain_community. document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

class ProcessController(BaseController):
  def __init__(self, project_id: str):
    super() .__init__()

    self.project_id = project_id    
    self.project_path = ProjectController().get_project_path(project_id=project_id)
    
  def get_file_extension(self,file_id:str):
    return os.path.splitext(file_id)[-1]
    
  def get_file_loader(self,file_id:str):
    file_ext = self.get_file_extension(file_id=file_id)

    file_path = os.path.join(self.project_path , file_id)# progect path(folder dir + project id) + file id (new file name)
    if not os.path.exists(file_path):
      return None
    if file_ext == ProccessingEnum.TXT.value: # here we apply enums as '.txt' is a value for a constant  
      return TextLoader(file_path, encoding="utf-8")

    if file_ext == ProccessingEnum.PDF.value:
      return PyMuPDFLoader(file_path)
    
    return None

  def get_file_content(self, file_id: str):
    loader=self.get_file_loader(file_id=file_id)
    if loader:# ensure that loader not none
      return loader.load()# return list (page content ,meta data)
    return None
  def procces_file_content(self,file_content:list,file_id: str,chunk_size:int = 100,overlap_size: int=20):
    # here i didn't use schema as it's for validate user request no need to use it between my code 
    text_splitter=RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap_size,
        length_function=len
    )

    file_content_texts =[rec.page_content for rec in file_content ]# why assigned page_content in list 
    file_content_metadata =[rec.metadata for rec in file_content ]

    chunks=text_splitter.create_documents(file_content_texts,metadatas=file_content_metadata) # i need that metadata to be with each chunk
    return chunks

"""#file_content: List[Document]

Document(
    page_content="text...",
    metadata={...}
)





file_content = [
    Document(page_content="Page 1 text", metadata={"page": 1}),
    Document(page_content="Page 2 text", metadata={"page": 2}),
]
الناتج:

chunks = [
    Document(page_content="Page 1 chunk A", metadata={"page": 1}),
    Document(page_content="Page 1 chunk B", metadata={"page": 1}),
    Document(page_content="Page 2 chunk A", metadata={"page": 2}),
]
"""