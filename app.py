import os
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel,function_tool, set_tracing_disabled
from agents.run import RunConfig
from dotenv import load_dotenv
import asyncio
import requests
import chainlit as cl

load_dotenv()
set_tracing_disabled(True)

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not present in .env file.")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model_provider=external_client,
    model=model,
    tracing_disabled=True
)

translator_agent = Agent(
    name="TranslatorAgent",
    instructions=(
        "You are a language translation assistant. "
        "Translate the user's input text into the target language specified by the user. "
        "If the user does not specify a language, ask them to clarify."
    ),
    model=model
)

async def translate_text(text: str):
    result = await Runner.run(
        starting_agent=translator_agent,
        input=text,
        run_config=config
    )
    return result.final_output

history:list = []

@cl.on_chat_start
async def chat_start():
    await cl.Message(content="I'm a Translator Agent. Enter your text to translate.").send()

@cl.on_message
async def on_message(message: cl.Message):
    user_input = message.content
    history.append({"role": "user", "text": user_input})
    
    thinking_msg = cl.Message(content="Translating...", id="thinking")
    await thinking_msg.send()
    
    result = await translate_text(user_input)
    history.append({"role": "assisstant", "text": result})
    
    await cl.Message(content=f"Translation:\n{result}").send()
    
@cl.on_chat_end
async def chat_end():
    with open("chat_history.txt", "a", encoding="utf-8") as f:
        for msg in history:
            f.write(f"{msg["role"]}: {msg["text"]}\n")
        f.write("\n---New Chat---\n")