from langchain_community.chat_models import ChatOllama
from lens.Base import BaseLLM
from lens.utils import parse_config
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler

class ChatOllamaLLM(BaseLLM):
    def __init__(self, model_id, model_params_path = None):
        self.model_params = self.load_params(model_params_path,model_id)
        self.model = None
        self.model_id = model_id
        
    
    def load_model(self):
        # Ensure that callback_manager is a valid object
        if isinstance(self.model_params.get("callback_manager"), str) and self.model_params["callback_manager"] == "default":
            self.model_params["callback_manager"] = CallbackManager([StreamingStdOutCallbackHandler()])
        
        self.model = ChatOllama(**self.model_params)

    def load_params(self, model_params_path, model_id):
        self.model_params = parse_config(cfg_path=model_params_path, model_id=model_id)
        print("loaded parameters: ",self.model_params)
        return self.model_params 
    
    def invoke(self, prompt) -> str:
        return self.model.invoke(prompt).content

    def handle_response(self, response) -> dict:
        # Process the response as needed
        return {"response": response}
    
    def __call__(self, prompt) -> str:
        return self.invoke(prompt)

    def __or__(self, prompt):
        print("DEBUG< PIPELINED MODEL")
        return prompt | self.model 