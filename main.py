import ollama

if __name__ == "__main__":
  resp = ollama.generate("gemma4:cloud", prompt="Pourquoi le ciel est bleu ?")
  print(resp)
