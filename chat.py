# from openai import AsyncOpenAI
import chainlit as cl
import httpx
import json

model = "meta-llama/Meta-Llama-3-8B-Instruct"
base_url = "https://jbwo0jie86w43e-8000.proxy.runpod.net/"
conversation_history = []

def format_conversation_history(history):
    # Convert the list of tuples to a string and remove square brackets
    formatted_history = str(history).strip('[]')

    # Replace the tuples' parentheses and clean up the format
    formatted_history = formatted_history.replace('), (', '; ').replace('(', '').replace(')', '')

    return formatted_history


system_prompt_base = f"""You are a sarcastic person, named Llama.

You are chatting with a person. All your responses should be witty, and sarcastic.

You should roast the user, but in a friendly way.

Here's the recent conversation history for your reference:

"""

def build_sys_prompt(system_prompt_base, conversation_history):
    formatted_history = format_conversation_history(history=conversation_history)
    prompt = system_prompt_base + formatted_history
    return prompt

async def generate_completion(system_prompt, user_prompt, model):
    url = base_url + "v1/chat/completions"  # Make sure this endpoint is correct
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.6,
        "max_tokens": 100,
        "stop": "<|eot_id|>"
    }
    timeout = httpx.Timeout(30.0)
    
    # Use httpx.AsyncClient to make the POST request
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print(f"Failed to get a valid response: {response.content}")
            return None
        return response.json()


@cl.on_message
async def on_message(message: cl.Message):

    system_prompt = build_sys_prompt(system_prompt_base, conversation_history)
    user_prompt = message.content
    response = await generate_completion(system_prompt, user_prompt, model)

    print(F"RESPONSE: {response}")
    assistant_response = response['choices'][0]['message']['content']
    await cl.Message(content=assistant_response).send()

    conversation_history.append((message.content, assistant_response))
    print("HISTORY:", conversation_history)
