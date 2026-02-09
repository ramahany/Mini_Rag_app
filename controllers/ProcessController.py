# Controllers 
from .BaseController import BaseController
from .ProjectController import ProjectController
# Enums 
from models import ProcessingEnum
# Loaders
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
#ext
import os 


class ProcessController(BaseController): 
    def __init__(self, project_id: str):
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectController().get_project_dir(project_id = self.project_id)

    
    # get the file extension 
    def get_file_extension(self, file_id:str): 

        return os.path.splitext(file_id)[-1]
    

    #get the file loader
    def get_file_loader(self, file_id:str): 
        file_ext =  self.get_file_extension(file_id=file_id)
        file_path = os.path.join(
            self.project_path, 
            file_id
        )
        if not os.path.exists(file_path) : return None
        if file_ext == ProcessingEnum.TXT.value : return TextLoader(file_path=file_path, encoding="utf-8")
        if file_ext == ProcessingEnum.PDF.value : return PyMuPDFLoader(file_path=file_path)
        return None 
    
    #load the file content 
    def get_file_content(self, file_id:str): 
        file_loader = self.get_file_loader(file_id=file_id)
        if file_loader:
            return file_loader.load()
        return None
    
    # Process file content (chunking)
    def process_file_content(self, file_id : str, chunk_size: int = 100, overlap_size: int = 100): 
        file_content = self.get_file_content(file_id=file_id)

        if file_content is None : return None
        
        text_spliter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size, 
            chunk_overlap = overlap_size,
        )

        document_content = [
            doc.page_content
            for doc in file_content
        ]

        document_metadata = [
            doc.metadata 
            for doc in file_content
        ]
        chunks = text_spliter.create_documents(
            document_content, 
            metadatas=document_metadata
        )

        return chunks

    


    