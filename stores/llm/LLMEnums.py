from enum import Enum

class LLMEnums(Enum): 
    OPENAI = 'OPENAI'
    COHERE = 'COHERE'


class OpenAIEnums(Enum): 
    SYSTEM = "developer"
    USER = "user"
    ASSISTANT = "assistant"

class CohereEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

    QUERY="search_query"
    DOCUMENT="search_document"


class DocumentTypes(Enum):
    QUERY="query"
    DOCUMENT="document"