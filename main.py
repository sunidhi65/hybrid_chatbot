from fastapi import FastAPI
import requests
import json
from sentence_transformers import SentenceTransformer, util

app = FastAPI()

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load cache
try:
    with open("cache.json", "r") as f:
        cache = json.load(f)
except:
    cache = {}

cache_embeddings = {
    q: model.encode(q, convert_to_tensor=True)
    for q in cache
}

# Build prompt
def build_prompt(messages):
    prompt = ""
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        prompt += f"{role}: {msg['content']}\n"
    prompt += "Assistant:"
    return prompt

# Call Ollama (NO retry loop)
def query_ollama(prompt, model_name):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        return response.json()["response"]
    except Exception as e:
        print(f"{model_name} failed:", e)
        return None

# Cache fallback
def get_offline_response(user_input):
    if not cache:
        return "Offline: No cached data available"

    user_embedding = model.encode(user_input, convert_to_tensor=True)

    best_match, best_score = None, 0

    for question, emb in cache_embeddings.items():
        score = util.cos_sim(user_embedding, emb).item()
        if score > best_score:
            best_score = score
            best_match = question

    if best_score > 0.7:
        return f"(Cached) {cache[best_match]}"

    return "Offline: No relevant cached response"

# Main logic
def get_response(messages):

    messages = messages[-5:]  # 🔥 reduced context for stability
    prompt = build_prompt(messages)
    user_input = messages[-1]["content"]

    # Try Mistral
    response = query_ollama(prompt, "mistral")
    if response:
        return response, "primary", user_input

    # Try Phi
    response = query_ollama(prompt, "phi")
    if response:
        return response, "fallback", user_input

    # Cache
    return get_offline_response(user_input), "cache", user_input

@app.post("/chat")
def chat(data: dict):

    messages = data["messages"]

    response, mode, user_input = get_response(messages)

    if mode in ["primary", "fallback"]:
        cache[user_input] = response
        cache_embeddings[user_input] = model.encode(user_input, convert_to_tensor=True)

        with open("cache.json", "w") as f:
            json.dump(cache, f)

    return {
        "response": response,
        "mode": mode
    }