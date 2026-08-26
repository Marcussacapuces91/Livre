import logging
import pathlib
import sys
import yaml

import rich.console
from .generator import Generator

console = rich.console.Console()

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

if __name__ == '__main__':
    assert (sys.argv[1])
    try:
        with pathlib.Path(sys.argv[1]).open('rt', encoding='utf-8') as ymlf:
            doc = yaml.safe_load(ymlf)
            generator = Generator(doc.get('variables', {}), doc['structure'] )
            generator.run()

    except KeyboardInterrupt as e:
        console.print("\nCTRL-C : Arrêt du programme par l'utilisateur", style='bold red')

    except FileNotFoundError as e:
        console.print(f"\nFile not found '{sys.argv[1]}', no YAML file to process!", style='bold red')
