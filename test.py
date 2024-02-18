from openai import OpenAI

client = OpenAI(
    api_key="sk-2NAEgdnhW963sPfpttPqpDKBqhIw3Vux",
    base_url="https://api.proxyapi.ru/openai/v1"
)

stream = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")


stream = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    messages=[{"role": "user", "content": "Say this is a test"},
              {"role": "user", "content": "What have you said?"}],
    stream=True,
)


