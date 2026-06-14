from ..LLMinterface import LLMInterface
from ..LLMEnums import CoHereEnums,DocumentTypeEnum
import cohere
import logging

class CohereProvider(LLMInterface):
    def __init__(self,api_key:str,
                      default_input_max_characters:int=1000,
                      default_generation_max_output_tokens: int=1000,
                      default_generation_temperature: float=0.1):
        self.api_key = api_key
        
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature     
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None # for Qdrant      
        self.enums = CoHereEnums
        self.client = cohere.Client(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)


    def set_generation_model(self,model_id:str):
        self.generation_model_id = model_id
    
    def set_embedding_model(self,model_id:str,embedding_size:int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self,text:str):
        return text[:self.default_input_max_characters]
    
    def generate_text(self,prompt:str,chat_history:list=[] ,max_output_tokens:int = None,
                            temperature:float=None):
        if not self.client:
            self.logger.error("client for open ai was not set")
            return None
        if not self.generation_model_id:
            self.logger.error("generation model for open ai was not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature


        response = self.client.chat(
            model = self.generation_model_id,
            chat_history = chat_history,
            message = self.process_text(prompt),
            temperature = temperature,
            max_tokens = max_output_tokens
          )
        
        if not response or not response.text:
            self.logger.error("Error while generating text with Cohere")

        return response.text

    def embed_text(self,text:str,document_type:str=None):
        if not self.client:
            self.logger.error("client for cohere was not set")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model for cohere was not set")
            return None

        input_type = CoHereEnums.DOCUMENT
        if document_type == DocumentTypeEnum.QUERY:
            input_type = CoHereEnums.QUERY

        response = self.client.embed(
            model = self.embedding_model_id,
            texts = [self.process_text(text)],
            input_type = input_type,
            embedding_types=['float'],
        )

        
        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with CoHere") 
            return None
        return response.embeddings.float[0]

        
    def construct_prompt(self,prompt:str,role:str):
        return{
            "role" : role,
            "text" : self.process_text(prompt)
        }



"""import cohere

# Initialize the client with V2
co = cohere.ClientV2(api_key="YOUR_API_KEY")

# Create the messages array with the chat history
messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi, how can I help you today?"},
    {"role": "user", "content": "I'm joining a new startup called Co1t today. Could you help me write a one-sentence introduction message to my teammates?"}
]

# Make the chat request
response = co.chat(
    model="command-a-03-2025",
    messages=messages,
    preamble="You respond in concise sentences."
)

# Print the response
print(response.message.content[0].text)
"""