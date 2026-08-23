import json
from back.src.ai.llm_client import LLMClient
from back.src.ai.tools import TOOLS, run_tool
from back.src.core.settings import settings

class LLMOrchestrator:

    def __init__(self, api_key: str):
        self.llm = LLMClient(api_key=api_key,base_url=settings.GAPGPT_BASE_URL,session_backend=None)
        self.model = settings.model
        self.system_prompt = open("src/ai/prompts/system_prompt.txt", "r", encoding="utf-8").read()

    def run(self, user_message, session_messages=None):
        if session_messages is None:
            session_messages = []

        session_messages.append({"role": "user", "content": user_message})

        response = self.llm.chat(
            messages=[
                {"role": "system", "content": self.system_prompt},
                *session_messages
            ],
            tools=TOOLS
        )

        message = response["choices"][0]["message"]

        # Tool Call
        if "tool_calls" in message and message["tool_calls"]:
            tool_call = message["tool_calls"][0]
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])

            tool_result = run_tool(tool_name, tool_args)

            session_messages.append({
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(tool_result, ensure_ascii=False)
            })

            final = self.llm.chat(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *session_messages
                ]
            )

            return final["choices"][0]["message"]["content"]

        return message["content"]
