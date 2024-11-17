from groq import Groq


client = Groq(
    api_key="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"
)

conversation_history = [
    {
        "role": "system",
        "content": "You are a personal educational assisstant and is specialised in solving problems. Introduce urself as ALAS whenever u are called. Give short precise answers unless users ask for a long explanation."
    }
]

def ask(user_input):
    conversation_history.append({
        "role": "user",
        "content": user_input
    })
    
    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="llama3-70b-8192",
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )
    
    response = chat_completion.choices[0].message.content
    conversation_history.append({
        "role": "assistant",
        "content": response
    })
    return response

# while True:
#     user_input = input("You: ")
#     if user_input.lower() == 'exit':
#         print("AI: Goodbye!")
#         break
#     else:
#         response = ask(user_input)
#         print("AI:", response)
