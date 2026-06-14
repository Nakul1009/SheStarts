from langchain_nvidia_ai_endpoints import ChatNVIDIA
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
import os
load_dotenv()

client = ChatNVIDIA(
  model="meta/llama-3.3-70b-instruct",
  api_key=os.getenv("NVIDIA_API_KEY"), 
  temperature=0.2,
  top_p=0.95,
  max_completion_tokens=8000
)

for chunk in client.stream([{"role":"user","content":"prime minister of india"}]):
    print(chunk.content, end="")