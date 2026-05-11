from mistralai import Mistral
import json
import requests

client = Mistral(api_key="ag_019e15b86b1d73fca79c4e02de3af76d")

# Tool schema
tools = [{
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Evaluate a math expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression e.g. 2*3"
                }
            },
            "required": ["expression"]
        }
    }
}]

# Call your local Flask server
def call_tool(name: str, args: dict) -> str:
    if name == "calculate":
        response = requests.post(
            "http://localhost:5000/calculate",
            json=args
        )
        return response.json()["result"]
    return "Tool not found"

# Agent loop
def run_agent(user_question: str) -> str:
    messages = [{"role": "user", "content": user_question}]

    while True:
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        msg = response.choices[0].message
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in (msg.tool_calls or [])
            ] or None
        })

        if not msg.tool_calls:
            return msg.content

        for tc in msg.tool_calls:
            fn_name = tc.function.name
            fn_args = json.loads(tc.function.arguments)

            result = call_tool(fn_name, fn_args)
            print(f"  [Tool called] {fn_name}({fn_args}) → {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result)
            })

# Dynamic input
print("Mistral Agent — type 'exit' to quit\n")

while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    if user_input.lower() == "exit":
        print("Goodbye!")
        break
    answer = run_agent(user_input)
    print(f"Agent: {answer}\n")