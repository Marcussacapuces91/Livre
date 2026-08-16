import os
from pprint import pprint

import ollama
import rich.status, rich.markdown
import hashlib
import pickle
import logging

from ollama import GenerateResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-10s:%(lineno)-5d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("app.log", encoding='utf-8')
    ]
)
log = logging.getLogger(__name__)

console = rich.console.Console()

class LLM:

    def __init__(self, model: str, think=None, keep_alive=None):
        """
        Initialize the LLM model
        :param model: Model name
        :param think: Think mode
        """
        self._model = model
        self._think = think
        self._keep_alive = keep_alive
        self._last_response = None

        self._cache = LLM._get_cache('cache.pickle')

        try:
            headers = None
            if os.environ.get('OLLAMA_API_KEY'):
                headers = {'Authorization': 'Bearer ' + os.environ['OLLAMA_API_KEY']}
            self._client = ollama.Client(
                host=os.environ.get('OLLAMA_URL'),
                headers=headers
            )
            # with rich.status.Status(f"Warming {self._model}..."):
            #     self._client.chat(self._model, keep_alive=keep_alive)  # chauffe le model
        except ollama.ResponseError as e:
            if e.status_code == 500:
                log.exception("Erreur de réponse: %s", e.error)
            raise
        except Exception as e:
            log.exception("Erreur inconnue")
            raise

    def warming(self) -> None:
        """
        Warm the model up, only necessary for local model.
        Do nothing for cloud models.
        :return: None
        """
        log.info("Warming model=%s", self._model)
        self._client.generate(self._model)

    def chat(self, messages: list) -> list:
        """
        Chat with user
        :param messages: list of message to be analyzed
        :return: List of messages append with the last answer
        """
        m = hashlib.md5(self._model.encode('utf-8'))
        m.update(str(messages).encode('utf-8'))
        digest = m.hexdigest()
        if digest in self._cache:
            log.info("Cache hit model=%s digest=%s", self._model, digest)
            self._last_response = self._cache[digest]
        else:
            log.info("Cache miss model=%s digest=%s", self._model, digest)
            with console.status(rich.markdown.Markdown(f"## Requête\n{messages[-1].get('content')}")):
                self._last_response = self._client.chat(
                    model=self._model,
                    messages=messages,
                    think=self._think,
                    options={
                        'num_ctx': 8192,
                        'num_predict': 8000
                    },
                    keep_alive=self._keep_alive
                )
            self._cache[digest] = self._last_response
            LLM._add_cache(digest, self._last_response, 'cache.pickle')

        return [ *messages, {
            'role': self._last_response['message'].get('role'),
            'content': self._last_response['message'].get('content')
        } ]

    def generate(self, prompt: str, format=None, options=None):
        m = hashlib.md5(self._model.encode('utf-8'))
        m.update(prompt.strip('\n ').encode('utf-8'))
        digest = m.hexdigest()

        if digest in self._cache and self._cache[digest].done_reason == 'stop':
            log.info("Cache hit model=%s digest=%s", self._model, digest)
            self._last_response = self._cache[digest]
        else:
            log.info("Cache miss model=%s digest=%s", self._model, digest)
            self._last_response = self._client.generate(
                model=self._model,
                prompt=prompt.strip('\n '),
                think=self._think,
                format=format,
                options=options,
                keep_alive=self._keep_alive
            )
            self._cache[digest] = self._last_response
            if self._last_response.done_reason == 'stop':       # Seulement si 'stop' : terminée sans troncature ou erreur
                LLM._add_cache(digest, self._last_response, 'cache.pickle')

        if self._last_response.done_reason != 'stop':
            log.warning("Done: %s ; Reason: %s", self._last_response.done, self._last_response.done_reason)
        else:
            log.info("Done: %s ; Reason: %s", self._last_response.done, self._last_response.done_reason)

        return self._last_response['response']

    @property
    def last_response(self):
        """
        Get last response
        :return: The last response
        """
        return self._last_response

    @staticmethod
    def _get_cache(name: str) -> dict:
        try:
            with open(name, 'rb') as f:
                cache = {}
                while True:
                    try:
                        obj = pickle.load(f)
                        try:
                            cache[obj['digest']] = obj['response']
                        except KeyError as e:
                            log.exception("Malformed cache file (%s): %r", name, obj)
                            raise
                    except EOFError:
                        break
                log.info("Cache chargé fichier=%s entrées=%d", name, len(cache))
                return cache

        except FileNotFoundError:
            log.info("Aucun fichier de cache trouvé: %s", name)
            return {}

    @staticmethod
    def _add_cache(digest, response, name: str):
        with open(name, 'ab') as f:
            pickle.dump(
            {
                    'digest': digest,
                    'response': response
                },
                f
            )
            log.info("Entrée de cache écrite fichier=%s digest=%s", name, digest)
