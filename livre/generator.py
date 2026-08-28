import logging
import datetime
from pathlib import Path
from typing import Sequence

import jinja2
import rich, rich.markdown, rich.table

from livre.llm import LLM

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

class Generator:
    def __init__(self, variables: dict, struct: dict):
        self._variables = variables
        self._struct = struct
        self._model = self._variables['model']
        self._think = self._variables.get('think')
        self._options = self._variables.get('options')

    @staticmethod
    def _table(title: str, response: dict) -> rich.table.Table:
        grid = rich.table.Table.grid(expand=True)
        grid.add_row("Done", "Reason", "Duration", "Prompt (tk)", "Eval (tk)", style="Bold")
        d = f'{int(response.total_duration / 1000 / 1000 / 1000 / 60)}:{int((int(response.total_duration / 1000 / 1000 / 1000) / 60 - int(response.total_duration / 1000 / 1000 / 1000 / 60)) * 60)}'
        grid.add_row(
            str(response.done),
            str(response.done_reason),
            d,
            str(response.prompt_eval_count),
            str(response.eval_count),
        )

        tbl = rich.table.Table(title)
        tbl.add_row(grid, end_section=True)
        tbl.add_row(response.thinking, end_section=True)
        tbl.add_row(response.response)
        return tbl

    @staticmethod
    def _generate(llm: LLM, struct: dict, n: int, current_path: Sequence[str], title: str, guidance: str, prolog: str, think=None, options=None,) -> str:
        prompt = "\n\n".join(current_path)  # Guidance
        if prolog:
            prompt += "\n\n" + struct['prolog']  # Prolog
        prompt += '\n\n' + "#" * n + ' ' + title  # Title

        log.debug(prompt)
        with console.status(rich.markdown.Markdown(f'Analyse : **{title}**\n\n{guidance}')):
            resp = llm.generate(
                prompt,
                think=think,
                options=options
            )
        try:
            console.print(Generator._table(title, llm.last_response))
        except Exception as e:
            log.error("Exception: Markdown parsing error in %s", str(llm.last_response['response']))
        return resp

    def run(self):

        def rec(output_file, variables: dict, struct: dict, n: int = 0, path=None) -> str:

            if struct.get('ignore', False):
                return ""

            if path is None:
                path = {}

            title = env.from_string(struct['title']).render(**variables)
            guidance = env.from_string(struct.get('guidance', '')).render(**variables)
            prolog = env.from_string(struct.get('prolog', '')).render(**variables)

            current_path = [guidance] if path is None else [*path, guidance]

            if struct.get('output_file'):
                output_file = Path(variables.get('docs_path', "."), struct['output_file']).open('wt', encoding='utf-8')

            resp = (    # llm response or "" if no need to ask for a answer.
                Generator._generate(llm, struct, n, current_path, title, guidance, prolog, think=variables.get('think'), options=variables.get('options'))
                if prolog or not struct.get('sections', False)
                else ""
            )

            for subst in variables.get('substitutions', []):
                (key, value), = subst.items()
                resp = resp.replace(key, value)

            if output_file is None:
                log.warning("Can't write in any file. User should define 'output_file' in the first structure!")
            else:
                output_file.write(resp)

            ## Resp contains
            # model = 'laguna-xs-2.1:latest'
            # created_at = '2026-08-01T09:59:33.8375072Z'
            # done = True
            # done_reason = 'stop'
            # total_duration = 285794890300
            # load_duration = 147665200
            # prompt_eval_count = 2385
            # prompt_eval_duration = 156820000
            # eval_count = 1915
            # eval_duration = 285479632000i
            # response = 'Pour gérer les applications (notamment des progiciels ou systèmes legacy) qui ne peuvent pas utiliser...'
            # thinking = "Okay, let me try to figure out how to approach this question. The user is asking about handling..."
            # context = []
            # logprobs = None
            # image = None
            # completed = None
            # total = None

            for sec in struct.get('sections', ()):
                sous_resp = rec(output_file, variables, sec, n + 1, current_path)
                if sous_resp is not None:
                    resp += '\n\n' + sous_resp
            return resp

        env = jinja2.Environment()
        env.globals['now'] = datetime.datetime.now
        env.globals['today'] = datetime.date.today
        env.globals['structure'] = Generator._mkd_struct(self._struct)

        llm = LLM(model=self._model)

        rec(output_file=None, variables=self._variables, struct=self._struct)


    @staticmethod
    def _mkd_struct(struct: dict, n: int = 0) -> str:
        """
        Produit une structure des titres (Table des Matières)
        :param struct: la structure du document.
        :param n: la profondeur de recursion
        :return: une chaine reprenant tous les titres, précédés de "#" selon n.
        """
        try:
            s = f'{"  " * n}{struct['title']}\n'
        except KeyError:
            console.log("`title` awaited in the structure!", struct)
            log.error("`title` awaited in the structure!\n%s", str(struct))
            exit(1)

        for sec in struct.get('sections', []):
            s += Generator._mkd_struct(sec, n + 1)
        return s

