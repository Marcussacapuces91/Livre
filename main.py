from ollama import Client
import os
import markdown

if __name__ == "__main__":
  client = Client(
    host='https://ollama.com',
    headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
  )
  resp = client.generate("gpt-oss:120b", prompt="Pourquoi le ciel est bleu ?")
  print(resp)
  with open("response.html", "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
    output_file.write(markdown.markdown(resp['response']))
    
