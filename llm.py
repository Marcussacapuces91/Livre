
from ollama import Client


class LLM:

  def __init__(self, model):
    self._model = model
    self._client = Client(
      host='https://ollama.com',
      headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
    )
    self._last_response = None

  def generate(self, prompt: str):
    resp = self._client.generate(self._model, self._prompt)

    self._last_response = resp
    return resp.get('response')
