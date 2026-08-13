import ollama

if __name__ == "__main__":
  client = ollama.client("https://ollama.com")
  resp = client.generate("gemma4:cloud", prompt="Pourquoi le ciel est bleu ?")
  print(resp)
