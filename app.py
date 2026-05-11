import chainlit as cl
from mistralai import Mistral
from dotenv import load_dotenv
from github_tool import read_github_file
import os
import json

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

# ── System prompt ─────────────────────────────────────
SYSTEM_PROMPT = """You are an intelligent HR Onboarding Assistant.
You can also read Python files from the company GitHub repository
when the user asks about code.

When asked about any Python file or code, use the
read_github_file tool to fetch and read the actual file."""

# ── Tool schema ───────────────────────────────────────
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_github_file",
            "description": "Read a Python file from the GitHub repository. Use this when the user asks to read, review, explain or check any file from GitHub.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "File name or path e.g. app.py or src/utils.py"
                    }
                },
                "required": ["file_path"]
            }
        }
    }
]


# ── Tool executor ─────────────────────────────────────
def execute_tool(name: str, args: dict) -> str:
    if name == "read_github_file":
        return read_github_file(**args)
    return "Tool not found"


# ── Chat start ────────────────────────────────────────
@cl.on_chat_start
async def start():
    cl.user_session.set("messages", [
        {"role": "system", "content": SYSTEM_PROMPT}
    ])
    await cl.Message(
        content="👋 Welcome! I am your HR Onboarding Assistant.\n\nI can also read files from your GitHub repository.\n\nTry asking: **read app.py from GitHub**"
    ).send()


# ── Main message handler ──────────────────────────────
@cl.on_message
async def main(message: cl.Message):
    messages = cl.user_session.get("messages")
    messages.append({
        "role": "user",
        "content": message.content
    })

    msg = cl.Message(content="")
    await msg.send()

    # Agent loop
    while True:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        assistant_msg = response.choices[0].message

        # Add to history
        messages.append({
            "role": "assistant",
            "content": assistant_msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in (assistant_msg.tool_calls or [])
            ] or None
        })

        # No tool call → final answer
        if not assistant_msg.tool_calls:
            await msg.stream_token(assistant_msg.content or "")
            break

        # Execute tool calls
        for tc in assistant_msg.tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments)

            # Show user what tool is being called
            await msg.stream_token(
                f"\n🔧 Reading `{fn_args.get('file_path')}` from GitHub...\n\n"
            )

            result = execute_tool(fn_name, fn_args)

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            })

    cl.user_session.set("messages", messages)
    await msg.update()
