
import sys
import os


ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ROOT, ".."))
from openai import OpenAI

from back.src.core.settings import settings

model=settings.model
api_key=settings.GAPGPT_API_KEY
base_url=settings.GAPGPT_BASE_URL
client = OpenAI(api_key=api_key, base_url=base_url)

# response = client.responses.create(
#     model=model,
#     input="hello"
# )

response = client.chat.completions.create(
            model=model,
            messages=[
    {"role": "developer", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
           
        )

print(response.choices[0].message.content)