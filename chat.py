# from openai import AsyncOpenAI
import chainlit as cl
import httpx
import json

model = "meta-llama/Meta-Llama-3-8B-Instruct"
base_url = "https://klevtu99lxsowl-8000.proxy.runpod.net/"
conversation_history = []

system_prompt = f"""You are a sarcastic person, named Llama.
You are chatting with a person. All your responses should be witty, and sarcastic.
You should roast the user, but in a friendly way.
Here's the recent conversation history for your reference:
{json.dumps(conversation_history)}
"""

async def generate_completion(prompt):
    url = base_url + "v1/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt,
        "temperature": 0.6,
        "max_tokens": 100,
    }
    timeout = httpx.Timeout(30.0) 
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, headers=headers, json=data)
        return response.json()

@cl.on_message
async def on_message(message: cl.Message):

    prompt_template = lambda: f"""
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>

    {system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

    {message.content}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """
    
    response = await generate_completion(prompt_template())

    print(F"RESPONSE: {response}")

    await cl.Message(content=response['choices'][0]['text']).send()

    # await cl.Message(content=response.choices[0].message.content).send()

    conversation_history.append((message.content, response['choices'][0]['text']))
    print("HISTORY:", conversation_history)
