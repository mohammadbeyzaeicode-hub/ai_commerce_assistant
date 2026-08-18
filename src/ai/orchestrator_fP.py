import json
from ai.llm_client import LLMClient
from ai.tools import TOOLS, run_tool


class LLMOrchestrator:
    """
    Orchestrator بدون state.
    session_backend از بیرون تزریق می‌شود.
    """

    def __init__(self, api_key: str, session_backend):
        self.llm = LLMClient(api_key=api_key)
        self.session = session_backend
        self.system_prompt = open(
            "src/ai/prompts/system_prompt.txt", "r", encoding="utf-8"
        ).read()

    def run(self, text: str, chat_id: str):
        # 1) دریافت تاریخچه از backend
        history = self.session.get_history(chat_id)

        # 2) اضافه کردن پیام کاربر
        self.session.append(chat_id, "user", text)

        # 3) فراخوانی مدل
        response = self.llm.chat(
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.session.get_history(chat_id),
            ],
            tools=TOOLS,
        )

        message = response["choices"][0]["message"]

        # --- اگر ToolCall داشت ---
        if "tool_calls" in message and message["tool_calls"]:

            tool_call = message["tool_calls"][0]
            tool_name = tool_call["function"]["name"]
            args = json.loads(tool_call["function"]["arguments"])

            # ثبت خروجی مدل
            self.session.append(
                chat_id,
                role="assistant",
                content=None,
                name=tool_name
            )

            result = run_tool(tool_name, args)

            # ثبت خروجی تول
            self.session.append(
                chat_id,
                role="tool",
                content=json.dumps(result, ensure_ascii=False),
                name=tool_name
            )

            # پاسخ نهایی پس از اجرای تول
            final = self.llm.chat(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self.session.get_history(chat_id),
                ]
            )

            final_msg = final["choices"][0]["message"]["content"]
            self.session.append(chat_id, "assistant", final_msg)

            return final_msg

        # --- پیام معمولی ---
        assistant_msg = message["content"]
        self.session.append(chat_id, "assistant", assistant_msg)
        return assistant_msg
