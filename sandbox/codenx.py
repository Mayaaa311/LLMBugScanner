from llama_cpp import Llama
from transformers import BitsAndBytesConfig, AutoTokenizer, AutoModelForCausalLM
import torch
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
llm = Llama.from_pretrained(
	repo_id="bartowski/Nxcode-CQ-7B-orpo-GGUF",
	filename="Nxcode-CQ-7B-orpo-IQ1_M.gguf",
)

llm.create_chat_completion(
	messages = [
		{
			"role": "user",
			"content": "What is the capital of France?"
		}
	]
)