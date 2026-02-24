from ...LLMInterface import LLMInterface
from ...LLMEnums import OpenAIEnums
from openai import OpenAI
import logging 

class OpenAIProvider(LLMInterface):
    def __init__(self, api_key:str, api_url:str=None,
                default_input_max_characters: int = 1000, 
                default_generation_max_output_tokens: int = 1000,
                default_generation_temperature: float = 0.1):
        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key=self.api_key,
            api_url = self.api_url
        )

        self.logger = logging.getLogger(__name__) # logger for this class for the log msg


    def set_generation_model(self, model_id: str): #why set it here ? so you can change the model in runtime without the need to rebuild the class
        self.generation_model_id = model_id


    def set_embedding_model(self, model_id :str, embedding_size:int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size


    def generate_text(self, prompt: str, chat_hist:list = [] ,
                      max_output_tokens: int=None, temperature: float = None) :
        #raise NotImplementedError # if i have to put a class that the interface is forcing apon me
        if not self.client: 
            self.logger.error("OpenAI Client was not set")
            return None
        
        if not self.generation_model_id : 
            self.logger.error("OpenAI generation model was not set")
            return None 
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        chat_hist.append(self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value))

        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_hist,
            max_tokens=max_output_tokens,
            temperature=temperature
        )
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message: 
            self.logger.error("Error while generating text with OpenAI")
            return None
        
        return response.choices[0].message["content"]

        

    
    def embed_text(self, text:str, documnet_type: str = None):
        if not self.client: 
            self.logger.error("OpenAI Client was not set")
            return None
        
        if not self.embedding_model_id : 
            self.logger.error("OpenAI embedding model was not set")
            return None
        
        response = self.client.embeddings.create(
            model=self.embedding_model_id,
            text = text
        )
        #validate output
        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding: 
            self.logger.error("Error while embedding text with OpenAI")
            return None
        
        return response.data[0].embedding
    
    def construct_prompt(self, prompt, role):
        return {
            "role" : role,
            "content":self.process_text(prompt)
        }
    
    #prep the input to mach the max_input_size(Naive seeka l sra7a)
    def process_text(self,text:str):
        return text[:self.default_input_max_characters].strip()
