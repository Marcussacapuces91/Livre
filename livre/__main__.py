import argparse
import logging
import pathlib
import sys
import yaml

import rich.console, rich.panel
from .generator import Generator

console = rich.console.Console()

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Process YAML file and generate structure.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "yaml_file",
        type=pathlib.Path,
        help="Chemin du fichier YAML à traiter"
    )

    args = parser.parse_args()
    yaml_path = args.yaml_file

    if not yaml_path.exists():
        console.print(
            rich.panel.Panel(f"Fichier introuvable : [bold]{yaml_path}[/bold]", title="Erreur", style="bold red")
        )
        sys.exit(1)

    try:
        with yaml_path.open("rt", encoding="utf-8") as ymlf:
            doc = yaml.safe_load(ymlf)

        generator = Generator(doc.get('variables', {}), doc['structure'] )
        generator.run()

    except yaml.YAMLError as e:
        console.print(
            rich.panel.Panel(f"Erreur YAML dans {yaml_path} :\n{e}", title="Erreur YAML", style="bold red")
        )
        sys.exit(2)

    except KeyboardInterrupt as e:
        console.print(
            rich.panel.Panel("CTRL-C : Arrêt du programme par l'utilisateur", title="Keyboard Interrupt", style='bold red')
        )
        sys.exit(130)

    except FileNotFoundError as e:
        console.print(f"\nFile not found '{sys.argv[1]}', no YAML file to process!", style='bold red')

    except Exception as e:
        console.print_exception()
        console.print(
            rich.panel.Panel(f"Erreur inattendue : {e}", title="Exception", style="bold red")
        )
        sys.exit(99)