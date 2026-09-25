import json
import os

from openrouter import OpenRouter
from pypdf import PdfReader

KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api.gitignore")

MODEL = "openrouter/free"

SYSTEM_PROMPT = (
    "You are a friendly, clear study helper. "
    "Explain things simply, keep answers short, "
    "and ask if the student wants more detail. "
    "When the student asks about a PDF of notes, call the read_pdf tool with the file name, "
    "then answer with a short summary in simple bullet points."
)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_pdf",
            "description": "Read a PDF file and return all text from every page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"}
                },
                "required": ["filename"]
            }
        }
    }
]


def load_api_key():
    environment_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if environment_key != "":
        return environment_key

    if not os.path.isfile(KEY_FILE):
        return ""

    try:
        with open(KEY_FILE) as key_file:
            for line in key_file:
                line = line.strip()
                if "sk-or-" in line:
                    start = line.find("sk-or-")
                    return line[start:].strip()
                if line.startswith("OPEN-ROUTER-API"):
                    parts = line.split("==")
                    if len(parts) > 1:
                        return parts[1].strip()
    except OSError:
        return ""

    return ""


def read_pdf(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, filename)

    if not os.path.isfile(path):
        return "File not found: " + filename

    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text = text + page_text
        if text.strip() == "":
            return "No text was found in the PDF (it may be scanned images)."
        return text
    except Exception as error:
        return "Error reading PDF: " + str(error)


def run_tool(name, arguments_json):
    if name == "read_pdf":
        args = json.loads(arguments_json)
        filename = args.get("filename", "")
        return read_pdf(filename)
    return "Unknown tool: " + name


def get_reply(client, messages):
    while True:
        response = client.chat.send(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            stream=False,
            max_tokens=1024,
        )

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            if message.content is None:
                return ""
            return message.content

        for call in message.tool_calls:
            result = run_tool(call.function.name, call.function.arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result
            })


def main():
    api_key = load_api_key()
    if api_key == "":
        print("Error: API key not found.")
        print("Put your key in api.gitignore, for example:")
        print("  OPEN-ROUTER-API==  sk-or-...")
        print("Or set the OPENROUTER_API_KEY environment variable.")
        return

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print("Welcome to Study Agent!")
    print("Type a message to chat, or type quit to stop.")
    print("")

    with OpenRouter(api_key=api_key) as client:
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("")
                user_input = "quit"

            if user_input.lower() == "quit":
                print("Goodbye! Good luck with your studies.")
                break

            if user_input == "":
                continue

            messages.append({"role": "user", "content": user_input})

            try:
                reply = get_reply(client, messages)
            except Exception as error:
                print("Sorry, I could not reach the model.")
                print("Details:", error)
                messages.pop()
                continue

            messages.append({"role": "assistant", "content": reply})
            print("Agent:", reply)
            print("")


if __name__ == "__main__":
    main()