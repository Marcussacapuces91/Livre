# 📚 Livre – Générateur Automatique de Livres avec IA

Un outil puissant pour **générer automatiquement du contenu de livre** en utilisant des modèles de langage (LLM) au moyen du service Ollama. Vous pouvez ainsi
utiliser une IA locale. Définissez votre structure, laissez l'IA faire le travail, et récupérez un document HTML et Markdown complet.

[![Python 3.14+](https://img.shields.io/badge/Python-3.14%2B-blue?style=flat-square)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

## 🎯 Ce que vous pouvez faire

✨ **Générez automatiquement des documents structurés** en fournissant :
- Une **structure hiérarchique** (sections, sous-sections, etc.)
- Un **contexte** (prolog, guidance, variables)
- Une **requête** (ce que vous voulez analyser)

📖 **Résultats** :
- Document Markdown complet (`docs/index.md`)
- Page HTML stylisée (`doc.html`)
- Cache intelligent pour les appels LLM (pas de duplication des requettes)

## 🚀 Installation rapide

### Prérequis
- Python 3.14+
- Un serveur Ollama local ou une clé API.

### Installation

```bash
# Cloner le repo
git clone https://github.com/Marcussacapuces91/Livre.git
cd Livre

# Installer les dépendances
pip install -e .
```

### Dépendances

```toml
jinja2>=3.1.6          # Templating (variables dans les titres)
markdown>=3.10.3       # Conversion Markdown → HTML
ollama>=0.6.2          # Client pour modèles locaux (ou API distante)
pyyaml>=6.0.3          # Lecture des fichiers de config
rich>=15.0.0           # Affichage coloré et tableaux
```

## 📋 Configuration

### Fichier de configuration (YAML)

Créez un fichier `config.yaml` pour définir votre livre :

```yaml
variables:
  model: "gemma4:cloud"        # Modèle LLM à utiliser
  docs_path: "./docs"           # Où sauvegarder les résultats
  your_var: "votre valeur"      # Variables personnalisées (utilisables dans les templates)

structure:
  title: "Titre du Livre"
  guidance: "Contexte initial pour l'IA"
  
  sections:
    - title: "Chapitre 1"
      guidance: "Guidance pour ce chapitre"
      prolog: "Demande spécifique à ce chapitre"
      sections:
        - title: "Section 1.1"
          guidance: "Analyse approfondie..."
        - title: "Section 1.2"
          ignore: true  # Sauter cette section
    
    - title: "Chapitre 2"
      guidance: "..."
```

### Exemple : Analyse d'un Business Model

Voir `bib.yaml` pour un exemple complet d'analyse de business model avec :
- Modèle de SWOT
- Points de friction
- Feuille de route MVP
- Modélisation financière
- Risques juridiques

## 🏃 Utilisation

### Générer un livre

```bash
python -m livre config.yaml
```

### Résultat

- `docs/index.md` – Markdown brut
- `doc.html` – Page HTML complète
- `cache.db` – Cache SQLite des réponses LLM

## 📊 Exemple de structure

```yaml
structure:
  title: "La plus Grande Bibliothèque du Monde"
  guidance: "Système d'échange de livres sur abonnement"
  prolog: "Analysez ce business model"
  
  sections:
    - title: "1. Analyse du Business Model"
      sections:
        - title: "1.1. SWOT du business model"
          guidance: "Présenter en matrice 2x2"
        
        - title: "1.2. Business Model CANVAS"
          guidance: "Analyser les 9 blocs"
        
        - title: "1.3. Points de frictions"
          guidance: "Lister et proposer des solutions"
```

Chaque section génère un appel LLM avec :
1. Le **contexte cumulé** (guidance des sections parents)
2. Le **prolog** spécifique
3. Le titre et la profondeur

## 🧠 Fonctionnalités clés

### 1️⃣ **Templating Jinja2**

Les titres, guidance et prolog supportent les templates Jinja2 :

```yaml
structure:
  title: "Rapport pour {{ client_name }}"
  guidance: "Préparé le {{ now().strftime('%d/%m/%Y') }}"
  
variables:
  client_name: "Acme Corp"
```

### 2️⃣ **Cache intelligent**

Les réponses LLM sont cachées pour éviter les appels redondants :

```python
# Même prompt + même modèle = résultat instant du cache
# Seulement si done_reason == 'stop' (complet, pas tronqué)
```

### 3️⃣ **Affichage détaillé**

Chaque génération affiche un tableau avec :
- ✅ État de complétion
- ⏱️ Durée totale
- 📊 Nombre de tokens (prompt + évaluation)
- 💭 Thinking mode (si activé)

### 4️⃣ **Sections ignorées**

```yaml
- title: "À passer"
  ignore: true          # Cette section sera ignorée
  sections: [...]
```

## 🔧 Configuration avancée

### Variables d'environnement

```bash
# Serveur Ollama
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_API_KEY="votre-clé-api"  # Si utilisé

# Logging
export LOG_LEVEL="DEBUG"
```

### Options LLM

```yaml
structure:
  title: "..."
  options:
    num_ctx: 16384      # Taille du contexte
    num_predict: 5000   # Max tokens générés
    temperature: 0.7    # Créativité
```

## 📈 Performance

### Optimisations incluses

- **Cache** : Chargement des analyses précédentes
- **Contexte cumulatif** : Chaque section reçoit le contexte de ses parents
- **Thinking mode** : Activation optionnelle pour plus de réflexion

### Améliorations recommandées

```python
# À implémenter :
# 1. Parallélisation des sections indépendantes
# 2. Streaming des réponses longues
# 3. Support des images/fichiers dans les réponses
```

## 📝 Format de sortie

### Markdown (`docs/index.md`)

```markdown
# Titre du Livre

## Chapitre 1

Contenu généré par l'IA...

### Section 1.1

Plus de contenu...
```

### HTML (`doc.html`)

Page HTML complète avec :
- Structure markdown convertie
- Styles par défaut
- Tables supportées

## 🐛 Troubleshooting

### "Model not found"
```bash
# Vérifiez le fichier YAML
cat config.yaml | grep "model:"

# Ou téléchargez un modèle
ollama pull gemma4
```

### Cache rempli / Performances dégradées
```python
# Videz le cache
rm cache.pickle
```

### Erreur de connexion Ollama
```bash
# Vérifiez que Ollama tourne
ollama serve

# Ou modifiez OLLAMA_URL
export OLLAMA_URL="http://your-server:11434"
```

## 🤝 Contribution

Les contributions sont bienvenues ! 

- 🐛 Bugs et problèmes → [Issues](https://github.com/Marcussacapuces91/Livre/issues)
- 💡 Suggestions → Créez une discussion
- 🔧 Pull requests → Bienvenue !

## 📄 Licence

MIT License – Libre d'utilisation, modification et distribution.

## 🎓 Use Cases

✅ **Business** : Analyse de business models, plans stratégiques  
✅ **Académique** : Génération de synthèses, analyses comparatives  
✅ **Création** : Scénarios, contenu créatif structuré  
✅ **Documentation** : Guides techniques, manuels utilisateur  

## 🚀 Feuille de route

- [ ] Chargement tardif du cache (lazy loading)
- [ ] Support du streaming pour réponses longues
- [ ] Parallélisation des sections indépendantes
- [ ] Support images/fichiers
- [ ] Dashboard de monitoring
- [ ] Export PDF natif
- [ ] Support multi-langue
- [ ] API REST

## 📞 Support

Questions ? Consultez :
- [Documentation](https://marcussacapuces91.github.io/Livre/)
- [Issues GitHub](https://github.com/Marcussacapuces91/Livre/issues)

---

**Fait avec ❤️ par [Marcussacapuces91](https://github.com/Marcussacapuces91)**
