from abc import ABC,abstractmethod # to design interface
# the idea of interface that we write form of class with no logic
# in provider (open AI , Ollama) the nodel resposble for generation is diif from model make the embedding 
class LLMInterface(ABC):
    
    @abstractmethod
    def set_generation_model(self,model_id:str):
        pass

    @abstractmethod
    def set_embedding_model(self,model_id:str,embedding_size:int):
        pass

    @abstractmethod     
    def generate_text(self,prompt:str,max_output_tokens:int,
    temperature:float=None):
        pass
    
    @abstractmethod
    def embed_text(self,text:str,document_type:str=None):
        pass

    @abstractmethod
    def construct_prompt(self,prompt:str,role:str): #format of prompt (came from user or system message) /// prompt template
        pass