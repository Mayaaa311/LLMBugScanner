from abc import ABC, abstractmethod
from langchain_core.prompts import PromptTemplate
param1 = {
    "max_new_tokens": 4000,
    "do_sample": True,
    "temperature": 0.001,
    "top_k": 50,
    "top_p": 0.95,
    "num_return_sequences": 1
}
param2 = {
    "max_new_tokens": 4000
    ,
    "do_sample": False
}
def set_template(template_path, input_var):
    with open(template_path, 'r') as file:
        template = file.read()
    return PromptTemplate(input_variables=input_var, template=template)
class BaseLLM(ABC):
    @abstractmethod
    def load_model(self):
        """Load the model with the required parameters."""
        pass

    @abstractmethod
    def invoke(self, prompt) -> str:
        """Invoke the model with a given prompt and return the response."""
        pass

    @abstractmethod
    def handle_response(self, response) -> dict:
        """Process the model's raw output and return a structured response."""
        pass


    def load_template(self, var, prompt_path=None):
        if prompt_path is not None:
            self.prompt_path = prompt_path
        self.prompt = set_template(self.prompt_path, var)
        # self.model = self.prompt | self.model