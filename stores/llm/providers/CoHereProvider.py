from ..LLMInterface import LLMInterface
from ..LLMEnums import CohereEnums, DocumentTypes
import logging 
import cohere
class CoHereProvider(LLMInterface):
    def __init__(self, api_key:str,
                default_input_max_characters: int = 1000, 
                default_generation_max_output_tokens: int = 1000,
                default_generation_temperature: float = 0.1):
        self.api_key = api_key


        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None
        
        self.client = cohere.ClientV2(api_key=self.api_key)

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str): 
        self.generation_model_id = model_id


    def set_embedding_model(self, model_id :str, embedding_size:int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def generate_text(self, prompt: str, chat_hist:list = [] ,
                      max_output_tokens: int=None, temperature: float = None) :
        if not self.client: 
            self.logger.error("Cohere Client was not set")
            return None
        
        if not self.generation_model_id : 
            self.logger.error("Cohere generation model was not set")
            return None 
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        chat_hist.append(self.construct_prompt(prompt=prompt, role=CohereEnums.USER.value))

        response = self.client.chat(
            model=self.generation_model_id,
            messages=chat_hist,
            max_tokens=max_output_tokens,
            temperature=temperature
        )

        if not response or not response.message.content or len(response.message.content) == 0 or not response.message.content[0].text: 
            self.logger.error("Error while generating text with Cohere")
            return None
        
        return response.message.content[0].text
    


    def embed_text(self, text:str, documnet_type: str):
        if not self.client: 
            self.logger.error("OpenAI Client was not set")
            return None
        
        if not self.embedding_model_id : 
            self.logger.error("OpenAI embedding model was not set")
            return None

        input_type = CohereEnums.QUERY.value
        if documnet_type == DocumentTypes.DOCUMENT.value: input_type = CohereEnums.DOCUMENT.value
        
        response = self.client.embed(
            model=self.embedding_model_id,
            texts = [text],
            input_type=input_type,
            embedding_types=["float"]
        )
        #validate output
        if not response or not response.embeddings or len(response.embeddings.float) == 0 : 
            self.logger.error("Error while embedding text with OpenAI")
            return None
        
        return response.embeddings.float[0]
    
    def construct_prompt(self, prompt, role):
        return {
            "role" : role,
            "content":self.process_text(prompt)
        }

    def process_text(self,text:str):
        return text[:self.default_input_max_characters].strip()

