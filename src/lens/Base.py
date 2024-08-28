from abc import ABC, abstractmethod

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
