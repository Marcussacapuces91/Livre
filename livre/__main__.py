import datetime
import logging
import os
import sys
from pathlib import Path
from pprint import pprint

import rich.console, rich.markdown, rich.table
from . import llm
import json
import yaml
import jinja2
import markdown

console = rich.console.Console()

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def mkd_struct(struct, n: int = 0) -> str:
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
        s += mkd_struct(sec, n + 1)
    return s

def _table(title, response):
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

def _generate(struct, n, current_path, title, guidance, prolog) -> str:
    prompt = "\n\n".join(current_path)  # Guidance
    if prolog:
        prompt += "\n\n" + struct['prolog']  # Prolog
    prompt += '\n\n' + "#" * n + ' ' + title  # Title

    log.debug(prompt)
    with console.status(rich.markdown.Markdown(f'Analyse : **{title}**\n\n{guidance}')):
        resp = my_llm.generate(
            prompt,
            options={
                'num_ctx': 16384,
                'num_predict': 5000
            }
        )
    try:
        console.print( _table(title, my_llm.last_response) )
    except Exception as e:
        log.error("Exception: Markdown parsing error in %s", str(my_llm.last_response['response']))
    return resp

def analyze(variables: dict, struct: dict, n: int = 0, path=None) -> str | None:
    """
    Lance l'analyse récurrente sur la structure itérative proposée.
    :param variables:   Liste des variables
    :param struct:      Structure itérative
    :param n:           Profondeur de récurrence (non défini au départ = 0)
    :param path:        Accumulation des contextes (guidance)
    :return:            Le résultat agrégé des analyses successives de la structure.
    """

    def rec(variables: dict, struct: dict, n: int, path: list) -> str:

        if struct.get('ignore', False):
            return ""

        env = jinja2.Environment()
        env.globals['now'] = datetime.datetime.now
        env.globals['today'] = datetime.date.today
        env.globals['structure'] = mkd_struct(struct)

        title = env.from_string(struct['title']).render(**variables)
        guidance = env.from_string(struct.get('guidance', '')).render(**variables)
        prolog = env.from_string(struct.get('prolog', '')).render(**variables)

        current_path = [guidance] if path is None else [*path, guidance]

        resp = (
            _generate(struct, n, current_path, title, guidance, prolog)
            if prolog or not struct.get('sections', False)
            else ""
        )
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
            sous_resp = rec(variables, sec, n + 1, current_path)
            if sous_resp is not None:
                resp += '\n\n' + sous_resp
        return resp

    return rec(variables, struct, 0, [])


if __name__ == '__main__':

    assert (sys.argv[1])

    try:

        with open(sys.argv[1], 'r', encoding='utf-8') as ymlf:
            doc = yaml.safe_load(ymlf)

            if (doc.get('variables') or {}).get('model'):
                model = doc['variables']['model']
            else:
                console.print(f"\nModel not found in {sys.argv[1]} (variables / model)'", style='bold red')
                exit(1)

            my_llm = llm.LLM(model=model, think='high')
            resp = analyze(doc.get('variables', {}), doc.get('structure'))

            Path('docs/index.md').write_text(resp, encoding='utf-8', )

            with open('doc.html', 'wt', encoding='utf-8') as f:
                f.write("""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>Document</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
""")
                f.write(markdown.markdown(resp.replace('\n* ', '\n* '), extensions=['extra', 'tables']))
                f.write("</body></html>")

    except KeyboardInterrupt as e:
        console.print("\nCTRL-C : Arrêt du programme par l'utilisateur", style='bold red')

    except FileNotFoundError as e:
        console.print(f"\nFile not found '{sys.argv[1]}', no YAML file to process!", style='bold red')
