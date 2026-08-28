# 📚 Livre – Générateur automatique de livres avec IA

Un outil pour générer automatiquement du contenu de livre en utilisant des modèles de langage (LLM) via Ollama, ce qui permet d'utiliser un modèle local ou distant. Définissez la structure du livre, fournissez le contexte et la requête — l'IA produit un document Markdown et une page HTML.

[![Python 3.14+](https://img.shields.io/badge/Python-3.14%2B-blue?style=flat-square)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

## 🎯 Fonctionnalités principales

- Génération automatisée de documents structurés à partir d'une structure hiérarchique (sections / sous-sections).
- Contexte cumulatif (guidance des parents) et prolog spécifique par section.
- Templates Jinja2 pour titres, guidance et prolog.
- Cache intelligent des réponses LLM pour éviter les requêtes redondantes.
- Sorties : Markdown complet (`docs/index.md`) et page HTML stylisée (`doc.html`).

## 🚀 Installation rapide

### Prérequis
- Python 3.14+ (ou la version minimale requise par votre environnement)
- Serveur Ollama local ou accès via une API clé

### Installation

```bash
git clone https://github.com/Marcussacapuces91/Livre.git
cd Livre
pip install -e .
```

### Dépendances (exemple)
```toml
jinja2>=3.1.6
markdown>=3.10.3
ollama>=0.6.2
pyyaml>=6.0.3
rich>=15.0.0
```

## 📋 Configuration

Créez un fichier `config.yaml` (ou utilisez l'exemple `bib.yaml`) pour définir la structure et les variables.

Exemple minimal (`config.yaml`) :

```yaml
variables:
  model: "gpt-oss:120b-cloud"     # Modèle par défaut (extrait de bib.yaml)
  think: high                      # Niveau de réflexion (optionnel)
  docs_path: './docs'              # Chemin de sortie des documents
  substitutions:                   # Substitutions de texte (ex. bib.yaml)
    - '$\rightarrow$': '⟶'
    - '---\n': '\n'

structure:
  title: "Titre du Livre"
  guidance: "Contexte global pour l'IA"

  sections:
    - title: "Chapitre 1"
      guidance: "Guidance pour ce chapitre"
      prolog: "Demande spécifique à ce chapitre"
      sections:
        - title: "Section 1.1"
          guidance: "Analyse approfondie..."
        - title: "Section 1.2"
          ignore: true  # Ignorer cette section
```

L'exemple complet `bib.yaml` inclus dans ce dépôt montre une configuration d'analyse de business model (SWOT, friction points, roadmap MVP, modèle financier, etc.).

## 🏃 Utilisation

Générer un livre à partir d'un fichier de configuration :

```bash
python -m livre config.yaml
```

Sorties attendues :
- `docs/index.md` — document Markdown généré
- `doc.html` — page HTML stylisée (générée à partir du Markdown)
- `cache.db` — cache SQLite des réponses LLM (nom de fichier configurable)

## 🧠 Principaux comportements

1. Contexte cumulatif : chaque section reçoit la guidance de ses parents.
2. Templating : Jinja2 est supporté dans `title`, `guidance` et `prolog`.
3. Cache : identique prompt + modèle → résultat servi depuis le cache (si la génération est complète).
4. Sections ignorées : marquez `ignore: true` pour sauter une section.

## 🔧 Configuration avancée

Variables d'environnement utiles :

```bash
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_API_KEY="votre-clé-api"  # si nécessaire
export LOG_LEVEL="DEBUG"
```

Options LLM (dans la structure) :

```yaml
options:
  num_ctx: 16384
  num_predict: 5000
  temperature: 0.7
```

## 📈 Performance & améliorations recommandées

Optimisations incluses :
- Cache local pour limiter les appels LLM
- Contexte cumulatif évitant la répétition

Améliorations recommandées (à implémenter) :
- Parallélisation des sections indépendantes
- Streaming des réponses longues
- Support des images / fichiers dans les résultats
- Export PDF natif

## 🐛 Dépannage rapide

"Model not found" :
```bash
# Vérifiez le modèle dans votre YAML
grep -n "model:" config.yaml

# Ou téléchargez le modèle avec Ollama
ollama pull gemma4
```

Cache et performances :
```bash
# Supprimez le cache local si nécessaire
rm cache.db
```

Erreur de connexion à Ollama :
```bash
# Vérifiez qu'Ollama tourne en local
ollama serve

# Ou adaptez OLLAMA_URL
export OLLAMA_URL="http://your-server:11434"
```

## 🤝 Contribution

Contributions bienvenues :
- Signalez les bugs → Issues (https://github.com/Marcussacapuces91/Livre/issues)
- Proposez des améliorations → Discussions / Pull Requests

## 📄 Licence

MIT — libre d'utilisation, modification et distribution.

---

Fait avec ❤️ par [Marcussacapuces91](https://github.com/Marcussacapuces91)
