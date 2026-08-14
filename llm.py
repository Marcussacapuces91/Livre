
from ollama import Client


class LLM

  def __init__(self, model):
    self._model = model
    self._client = ollama.Client()

  def generate(self, prompt: str):
    resp = self._client.generate(self._model, self._prompt)

    self._last_response = resp
    return resp.get('response')

