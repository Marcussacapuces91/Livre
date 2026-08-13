from ollama import Client
import os

if __name__ == "__main__":
  client = Client(
    host='https://ollama.com',
    headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
  )
  resp = client.generate("gemma4:cloud", prompt="Pourquoi le ciel est bleu ?")
  print(resp)
