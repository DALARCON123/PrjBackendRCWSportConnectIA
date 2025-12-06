# Projet Backend du Cours RCW: Sport Connect IA

Ce projet consiste à développer une application web et mobile qui utilise des données sur la santé et l'activité physique des utilisateurs pour leur recommander des routines d'exercices personnalisées. L'application utilise des modèles d'IA pour analyser les objectifs de santé, les préférences, les données biométriques (fréquence cardiaque, calories brûlées) et les habitudes d'exercice, afin de proposer des recommandations adaptées en temps réel.

## Problème (WHY)
Beaucoup de personnes ont du mal à trouver des programmes d'exercices adaptés à leurs besoins et capacités spécifiques. De plus, les routines d'entraînement génériques ne sont pas toujours efficaces pour atteindre les objectifs de santé individuels, tels que la perte de poids, la remise en forme, ou l'amélioration de la condition physique.

## Contexte (HOW)
L'application permet aux utilisateurs de saisir leurs objectifs de santé (perte de poids, gain de muscle, etc.), de synchroniser les données de leurs appareils de fitness (montres intelligentes, capteurs) et de suivre leur progression au fil du temps. L'IA analyse ces données et fournit des recommandations personnalisées en fonction de la condition physique actuelle de l'utilisateur, ses objectifs, et ses préférences en matière d'exercice. Le système propose des suggestions d'exercices quotidiens, des rappels pour rester actif, et des ajustements du programme en fonction des progrès. Une architecture microservices permet de gérer indépendamment la gestion des utilisateurs, l'analyse des données biométriques, et les recommandations.

## Installation

Pour installer le projet, vous devez créer l'environnement virtuel:

```bash
python3 -m venv venv
```

## Utilisation

Pour utiliser le projet, vous devez d'abord activer l'environnement virtuel:

```bash
./venv/bin/activate
```

Ensuite, vous pouvez installer les dependencies avec la commande suivante:

```bash
pip install -r requirements.txt
```

Puis, vous pouvez lancer l'application avec la commande suivante:

```bash
.\start_all_services.ps1
```

## Mock Data

Pour instancier les *mock data*, vous devez utiliser le commande suivante:

```bash
.\run_seeder.ps1
```
