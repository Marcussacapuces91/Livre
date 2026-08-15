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
    s = f'{"  " * n}{struct['title']}\n'
    if 'sections' in struct:
        for sec in struct['sections']:
            s += mkd_struct(sec, n + 1)
    return s

def analyze(variables, struct, n: int = 0, path=None) -> str | None:
    """
    Lance l'analyse récurrente sur la structure itérative proposée.
    :param struct:  Structure itérative
    :param n:       Profondeur de récurrence (non défini au départ = 0)
    :param path:    Accumulation des contextes (guidance)
    :return:        None.
    """

    # def rec(variables, struct, n: int = 0, path=None)
    if not struct.get('ignore', False):
        env = jinja2.Environment()
        env.globals['now'] = datetime.datetime.now
        env.globals['today'] = datetime.date.today
        env.globals['structure'] = mkd_struct(struct)

        title = env.from_string(struct['title']).render(**variables)
        guidance = env.from_string(struct.get('guidance', '')).render(**variables)
        prolog = env.from_string(struct.get('prolog', '')).render(**variables)

        current_path = [guidance] if path is None else [*path, guidance]

        if prolog or not struct.get('sections', False):
            prompt = "\n\n".join(current_path)  # Guidance
            if prolog:
                prompt += "\n\n" + struct['prolog']  # Prolog
            prompt += '\n\n' + "#" * n + ' ' + title  # Title

            log.debug(prompt)
            with console.status(rich.markdown.Markdown(f'Analyse : **{title}**\n\n{guidance}')):
                resp = my_llm.generate(
                    prompt,
                    options= {
                        'num_ctx': 8192,
                        # 'num_predict': -1
                    }
                )

            try:
                grid = rich.table.Table.grid("Done", "Reason", "Duration", "Prompt (tk)", "Eval (tk)", expand=True)
                d = f'{int(my_llm.last_response.total_duration / 1000 / 1000 / 1000 / 60)}:{int((int(my_llm.last_response.total_duration / 1000 / 1000 / 1000) / 60 - int(my_llm.last_response.total_duration / 1000 / 1000 / 1000 / 60)) * 60)}'
                grid.add_row(
                    str(my_llm.last_response.done),
                    str(my_llm.last_response.done_reason),
                    d,
                    str(my_llm.last_response.prompt_eval_count),
                    str(my_llm.last_response.eval_count),
                )

                table = rich.table.Table(title=title)
                table.add_row(grid, end_section=True)
                table.add_row(my_llm.last_response.thinking, end_section=True)
                table.add_row(resp)
                console.print(table)

            except Exception as e:
                raise

        else:
            resp = ""

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
            # response = 'Pour gérer les applications (notamment des progiciels ou systèmes legacy) qui ne peuvent pas utiliser directement les API du Bus d’Échange d’Entreprise (BEE), il est nécessaire de prévoir des **adaptateurs ou ponts techniques** (« *connecteurs* ») situés à l’interface entre ces applications et le BEE. Ces adaptateurs permettent de traduire les protocoles, formats ou méthodes d’échange locaux en événements standardisés via AsyncAPI, tout en maintenant la cohérence du modèle BEE. Voici une réponse structurée à votre question :\n\n---\n\n### **1. Stratégie d’intégration des applications non compatibles avec le BEE**\n#### a) **Adaptateurs comme relais technique (pas un EAI centralisé)**  \n- Les systèmes legacy ou progiciels qui ne supportent pas les API modernes peuvent être connectés au BEE via des **adaptateurs ponctuels** (« *bridge* », « *gateway* ») situés à leur périmètre. Ces adaptateurs :  \n  - Traduisent les échanges locaux (ex. SOAP, fichiers plats, appels RPC) en **événements AsyncAPI**.  \n  - Respectent le contrat du BEE pour garantir la standardisation des flux.  \n  - Ne créent **aucun lien direct** entre l’application source et les consommateurs d’événements : tout passe par le BEE, préservant ainsi son rôle de médiateur centralisé.  \n\n#### b) **Exemple concret**  \n- Un progiciel métier qui ne dispose que d’un accès FTP pour exporter des données peut utiliser un service d’orchestration (ex. script ou micro-service) pour :  \n  - Lire les fichiers CSV via FTP,  \n  - Transformer les données en JSON conforme au schéma AsyncAPI déclaré dans le BEE,  \n  - Publier l’événement sur le canal du BEE (via un client AsyncAPI).  \n\n#### c) **Rôle de l’EAI : éviter le coupling direct**  \n- Un EAI côté application (« *point-to-point* » ou middleware local) est acceptable **si** :  \n  - Il agit uniquement comme un **traducteur technique**, sans créer de dépendances dynamiques entre les applications.  \n  - Il respecte le principe du BEE : tout échange passe par le bus, même s’il y a un maillon intermédiaire.  \n\n---\n\n### **2. Risques d’un traitement EAI mal conçu**  \n#### a) **Perte de découplage si l’EAI est centralisé**  \n- Si l’EAI devient une passerelle unique entre les applications (ex. ESB central), cela peut réduire la flexibilité du BEE en introduisant un point unique de défaillance et en limitant l’évolutivité.  \n\n#### b) **Complexité technique accrue**  \n- Un EAI mal orchestré (ex. gestion manuelle des transformations, absence de standardisation) peut réduire la clarté du modèle BEE, surtout si les adaptateurs ne sont pas documentés ou gérés comme des composants du système.  \n\n#### c) **Contre-mesures pour éviter ces risques**  \n- **Standardiser les adaptateurs** : Les ponts techniques doivent respecter les mêmes principes que le BEE (contract-first, versionnage, observabilité).  \n- **Cataloguer les adaptateurs** : Tous les connecteurs doivent être répertoriés dans un catalogue technique, avec leur schéma de données et leur mode d’emploi.  \n- **Privilégier l’automatisation** : Les transformations doivent être automatisées (ex. via des outils open source comme Apache Camel ou des scripts CI/CD) pour éviter la dette technique.  \n\n---\n\n### **3. Bonnes pratiques pour préserver les bénéfices du BEE**  \n#### a) **Adopter une approche progressive et pragmatique**  \n- Les systèmes legacy ne doivent pas être ignorés : des adaptateurs temporaires (« *facades* ») permettent de les intégrer sans remettre en cause le modèle BEE.  \n\n#### b) **Éviter l’EAI comme solution de continuité**  \n- Les adaptateurs doivent être perçus comme des **intermédiaires temporaires**, avec un plan de modernisation pour migrer progressivement les systèmes legacy vers des API natives du BEE.  \n\n#### c) **Respecter la neutralité technologique**  \n- L’EAI utilisé doit être choisi en fonction de son adéquation au modèle BEE (ex. outils open source pour éviter les verrous fournisseurs), et non de sa facilité d’implémentation.  \n\n---\n\n### **4. Conclusion : Adapter sans compromettre le concept**  \nLe BEE reste un modèle conceptuel, indépendant des technologies. Les adaptateurs EAI côté application **ne nuisent pas au BEE** s’ils :  \n1. Agissent comme des ponts techniques, non comme des points de communication directe entre applications.  \n2. Respectent les principes de standardisation et de gouvernance du BEE (contrats AsyncAPI, traçabilité).  \n3. Sont temporaires et remplacés par des intégrations natives dès que possible.  \n\nCette approche permet de préserver la valeur centrale du BEE : **l’intermédiation centralisée pour une urbanisation modulaire, résiliente et standardisée** du SI.  \n\n--- \n\nCe cadre répond à vos préoccupations tout en restant aligné avec les principes du Bus d’Échange d’Entreprise.'
            # thinking = "Okay, let me try to figure out how to approach this question. The user is asking about handling applications that can't directly use the BEE APIs and whether using an EAI tool near those apps would reduce the optimization of the concept. \n\nFirst, I need to recall what a Bus d'Échange d'Entreprise (BEE) is. From the context provided earlier, it's an intermediate layer for data exchange between applications without direct communication, relying on Event-Driven Architecture (EDA) with AsyncAPI as a standard. The BEE is a concept, not a specific tool like Kafka or ESB.\n\nThe user's concern is about legacy systems or older applications that might not support modern APIs. If these apps can't integrate directly into the BEE, using an EAI (Enterprise Application Integration) middleware on their side could be necessary. But the user worries this might undermine the BEE's benefits like decoupling and standardization.\n\nI need to address two main points: \n1. How to handle such applications without direct API access.\n2. Whether introducing an EAI near them affects the BEE concept negatively.\n\nPossible solutions for point 1 include using adapters or connectors that translate between the application's interface (like SOAP, FTP, etc.) and the BEE's event-based APIs. These adapters can be part of a broader integration layer but still keep the core applications decoupled from each other via the BEE. This way, the EAI is just a bridge for legacy systems without forcing direct communication between apps.\n\nFor point 2, if the EAI is only on the periphery (like near the old app) and not creating direct links between apps, then it doesn't compromise the BEE's principles. The key is ensuring that all data exchange goes through the BEE, even if some systems need a translator to get there. However, over-reliance on EAI could lead to complexity or performance issues if not managed well. It might also introduce dependencies on specific middleware, which contradicts the BEE's neutrality.\n\nI should mention that while EAI can be a necessary tool for legacy integration, it's important to minimize its use and ensure it doesn't become a direct communication path between applications. The BEE's value lies in centralized event management, so any adapter must route through the BEE, not bypass it. Also, as systems modernize, moving away from EAI towards direct API usage will align better with BEE principles.\n\nNeed to structure this into a coherent answer, explaining the use of adapters, the role of EAI without breaking decoupling, and perhaps some recommendations on managing such scenarios effectively within the BEE framework."
            # context = []
            # logprobs = None
            # image = None
            # completed = None
            # total = None



        for sec in struct.get('sections', ()):
            sous_resp = analyze(variables, sec, n + 1, current_path)
            if sous_resp is not None:
                resp += '\n\n' + sous_resp

        return resp

    return None


if __name__ == '__main__':

    assert (sys.argv[1])

    try:

        with open(sys.argv[1], 'r', encoding='utf-8') as ymlf:
            doc = yaml.safe_load(ymlf)
            model = "gemma4"

            if doc.get('variables', {}).get('model'):
                model = doc['variables']['model']

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
