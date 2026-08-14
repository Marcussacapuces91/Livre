from ollama import Client
import os
import markdown

if __name__ == "__main__":
  client = Client(
    host='https://ollama.com',
    headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
  )

  prompt = """Tu es un expert en génie des procédés, ingénierie thermodynamique, capture du carbone (CCS/CCU) et économie circulaire.

Je souhaite développer un module industriel conteneurisé (format conteneur maritime 40 pieds) d'inertage et de valorisation des cendres d'incinérateur (REFIOM/mâchefers) par capture de CO2 directement sur les fumées de cheminée.

Réalise une étude de faisabilité complète et rigoureuse du projet en suivant l'architecture et les contraintes ci-dessous :

# 1. CONTEXTE ET NIVEAUX DE SÉPARATION (L'ARCHITECTURE)
Le système traite les fumées brutes d'une Unité d'Incinération d'Ordures Ménagères (UIOM) :
- Étage 0 (Prétraitement) : Cyclone dépoussiéreur + filtration mécanique HEPA pour éliminer les micro-particules (PM2.5/PM10) et suies sans perte de charge excessive, afin de protéger les tuyères.
- Étage 1 (Déshydratation par tuyère subsonique / Mach 0.8) : Refroidissement adiabatique vers -30°C pour cristalliser et éjecter l'eau (H2O) par force centrifuge sous forme de glace purifiée (eau distillée).
- Étage 2 (Séparation du CO2 par tuyère supersonique / Mach 1.5 - 2.0) : Détente poussée vers -60°C à -80°C (ajustée selon la pression partielle du CO2 dans la fumée à 10-12%) pour forcer la désublimation du CO2 en neige carbonique, éjectée par vortex sur les parois.
- Étage 3 (Optionnel - Séparation N2/O2) : Évaluation d'une détente à Mach 2.5+ (-185°C à -195°C) pour liquéfier l'Oxygène et l'Azote et produire des gaz industriels à haute valeur ajoutée.

# 2. SÉQUESTRATION DÉFINITIVE ET MINÉRALISATION
Le CO2 purifié capté n'est pas revu sous forme de carburant (pour éviter de le réémettre), mais minéralisé :
- Explique la réaction de carbonatation accélérée ex-situ entre le CO2 purifié et les résidus alcalins de l'usine (REFIOM, ciment, mâchefers).
- Montre comment cette réaction transforme les cendres toxiques en carbonates de calcium/magnésium stables (CaCO3 / MgCO3), leur faisant perdre leur statut de déchet dangereux pour les réutiliser dans le BTP (granulats, sous-couches routières).

# 3. DIMENSIONNEMENT ET BATTEMENT ÉNERGÉTIQUE
Considère une unité cible capable d'extraire et de fixer 1 tonne de CO2 purifié par jour.
- Calcule le volume de fumées industrielles à brasser (à 10-12% de CO2) vs de l'air ambiant (426 ppm).
- Évalue la puissance électrique continue requise pour les compresseurs/surpresseurs et automatismes.
- Propose une stratégie de mix énergétique local : combinaison de l'électricité produite en co-génération par le turbo-alternateur de l'incinérateur et d'un champ solaire photovoltaïque dédié à proximité (avec gestion de la charge variable jour/nuit et stockage tampon des cendres).

# 4. MODÈLE ÉCONOMIQUE ET CIBLAGE
Analyse la viabilité financière auprès des syndicats intercommunaux de gestion des déchets (UIOM) :
- Évite la dépendance au marché du carbone EU ETS (~60-80 €/t) ou au DAC coûteux.
- Démontre la rentabilité via le triple levier : 
  1. Économies sur les coûts d'enfouissement/Inertage spécialisé des REFIOM dangereux (150-250 €/t évités).
  2. Évitement de la TGAP et anticipation des quotas CO2 sur les cheminées.
  3. Vente des coproduits (eau déminéralisée, granulats BTP stabilisés).

# 5. ANNEXES
## 5.1. Schémas
Décris / dessine le 1er étage, avec le cyclone de dépoussiération ;
De même, pour l'étape 1, l'extraction de l'humidité. Sur la base de 20 cyclones, indique forme et dimenssions ainsi que les pression et le débits mis en oeuvre à cette étape.

Fournis des calculs clairs, des schémas d'écoulement textuels (block flow diagrams) et valide la cohérence thermodynamique globale du système.
"""
  
  resp = client.generate("gpt-oss:120b", prompt=prompt, think=True)
  print(resp.get('thinking'))
  print(resp.get('response'))
  with open("docs/response.md", "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
    output_file.write(resp['response'])
    # output_file.write(markdown.markdown(resp['response']))
    
