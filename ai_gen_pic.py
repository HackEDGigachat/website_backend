import os
import openai
import config

openai.api_key=config.open_api_key
def ai_gen_pic(prompt):
    url = openai.Image.create(
        prompt = prompt,
        n=1,
        size ="1024x1024"
    )
    return url
# print(ai_gen_pic("an anime draw of Steph curry eating curry"))

