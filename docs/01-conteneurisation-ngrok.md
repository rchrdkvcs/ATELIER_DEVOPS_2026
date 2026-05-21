# Exercice 1 — Conteneuriser Flask et exposer via Ngrok

**Niveau** : Débutant
**Durée estimée** : 2 à 3 heures
**Pré-requis** : avoir forké le dépôt, avoir lancé un **Codespace** sur votre fork (voir README), avoir un *authtoken* Ngrok personnel.

---

## Scénario

Vous reprenez le projet d'un développeur. Il vous laisse une mini-app Flask et une consigne :

> « Je voudrais qu'à chaque push sur GitHub, mon site soit reconstruit dans une image Docker, lancé automatiquement, et qu'on puisse y accéder depuis Internet pendant **2 minutes** pour que je le montre à un client. Je n'ai pas envie de payer un hébergeur juste pour faire une démo. »

C'est exactement ce que permet la combinaison **Docker + GitHub Actions + Ngrok** : un environnement éphémère, public, gratuit, déclenché par un push.

---

## Objectifs pédagogiques

À la fin de l'exercice, vous saurez :

- Écrire un `Dockerfile` pour une application Python
- Construire et lancer une image **dans votre Codespace** (avant de passer à la CI)
- Écrire un workflow GitHub Actions qui construit puis exécute un conteneur
- Exposer un port de conteneur sur Internet via Ngrok
- Gérer un secret (le token Ngrok) sans le commiter

---

## Cahier des charges

1. L'application Flask fournie doit **tourner dans un conteneur Docker** construit à partir d'un `Dockerfile` que vous écrivez.
2. Le **port HTTP** du conteneur doit être joignable depuis l'extérieur du conteneur.
3. Un **workflow GitHub Actions** (`.github/workflows/`) :
   - se déclenche sur `push` (et idéalement aussi `workflow_dispatch` pour pouvoir le relancer à la main),
   - construit l'image Docker,
   - lance le conteneur,
   - ouvre un tunnel **Ngrok** vers le port exposé,
   - **affiche l'URL publique dans les logs** de l'action,
   - laisse le tunnel ouvert pendant **environ 120 secondes**, puis s'arrête proprement.
4. L'**authtoken Ngrok** est stocké en **secret GitHub** (jamais en clair dans le code).
5. La page `/exercices/` doit afficher votre **prénom et nom** (à modifier dans `templates/exercices.html`).

---

## Critères de validation

Un évaluateur doit pouvoir, **en lisant les logs de votre workflow** :

- [ ] Voir une **URL publique** au format `https://*.ngrok-free.app/` (ou équivalent).
- [ ] Cliquer dessus pendant les ~120 s d'ouverture et obtenir la page d'accueil Flask (« Bonjour tout le monde ! »).
- [ ] Naviguer vers `/exercices/` et voir **votre prénom + nom**.
- [ ] Constater que le job s'est **terminé proprement** (pas en `timeout` après 6 h, pas resté bloqué).
- [ ] Vérifier que **votre token Ngrok n'apparaît nulle part en clair** dans les logs.

---

## Indices (sans solution)

Lisez-les seulement si vous bloquez réellement après avoir tenté.

<details>
<summary><strong>Indice 0 — Itérer dans le Codespace avant de toucher au workflow</strong></summary>

Avant d'écrire la moindre ligne de YAML, faites tourner votre Dockerfile **dans le terminal du Codespace** : `docker build -t test .` puis `docker run --rm -p 5000:5000 test`. VS Code détectera le port 5000 et vous proposera un onglet **PORTS** avec une URL `*.app.github.dev` cliquable — c'est votre app, exposée publiquement, depuis votre Codespace. Cycle de feedback : ~5 secondes. Cycle CI : ~2 minutes. Faites le calcul.

Une fois que tout marche dans le Codespace, **alors** vous écrivez le workflow.
</details>

<details>
<summary><strong>Indice 1 — Dockerfile minimal Python</strong></summary>

Un `Dockerfile` Python suit typiquement 4 grandes étapes : choisir une **image de base** (regardez les variantes `slim`), **copier** votre code, **installer** les dépendances avec `pip`, et **déclarer la commande** de démarrage. La documentation officielle Docker a une section *Best practices* — lisez-la avant d'écrire la première ligne.
</details>

<details>
<summary><strong>Indice 2 — Flask et le réseau</strong></summary>

Par défaut, Flask en mode développement n'écoute **que sur l'interface locale du conteneur**. Depuis l'hôte, ça veut dire : *connection refused*. Quelle option de `app.run()` change ce comportement ? (Indice : il existe une adresse IP magique qui veut dire « toutes les interfaces ».)
</details>

<details>
<summary><strong>Indice 3 — Mapper un port</strong></summary>

Côté `docker run`, quelle option permet de rendre un port du conteneur accessible depuis l'hôte ?
</details>

<details>
<summary><strong>Indice 4 — Lancer le conteneur en CI</strong></summary>

Dans une GitHub Action, vous pouvez exécuter n'importe quelle commande shell. Y compris `docker build` et `docker run`. Pensez au mode **détaché** (en arrière-plan) du conteneur, sinon l'étape suivante ne s'exécutera jamais.
</details>

<details>
<summary><strong>Indice 5 — Ngrok dans un workflow</strong></summary>

Ngrok fournit un binaire CLI. Pour l'installer rapidement dans un runner Ubuntu, il existe plusieurs voies : `apt`, `snap`, téléchargement du binaire, ou… une **image Docker officielle Ngrok**. Le moins de surprises ? Probablement la dernière.

Le binaire Ngrok lit son authtoken depuis une commande de configuration (`ngrok config add-authtoken …`) **ou** depuis une variable d'environnement. La seconde option est plus propre en CI.
</details>

<details>
<summary><strong>Indice 6 — Limiter la durée à ~120 secondes</strong></summary>

Aucun mystère : votre workflow doit **dormir 120 secondes** après avoir lancé le tunnel, puis tuer le tunnel. Cherchez du côté des commandes `sleep`, `timeout`, ou des options GitHub Actions de limite de durée (`timeout-minutes`).
</details>

<details>
<summary><strong>Indice 7 — Récupérer l'URL Ngrok et l'afficher</strong></summary>

Quand Ngrok démarre, il expose une **API locale** sur `http://localhost:4040/api/tunnels` qui renvoie un JSON contenant l'URL publique. Une simple requête `curl` + un peu de parsing (`jq` est ton ami) suffit à l'extraire et à la `echo` dans les logs.
</details>

<details>
<summary><strong>Indice 8 — Le secret Ngrok</strong></summary>

Dans votre dépôt GitHub : **Settings → Secrets and variables → Actions → New repository secret**. Donnez-lui un nom explicite (par convention en MAJUSCULES). Dans le workflow, vous y accédez via `${{ secrets.NOM_DU_SECRET }}`. GitHub masque automatiquement la valeur dans les logs.
</details>

---

## Anti-patterns à éviter

- ❌ Mettre votre authtoken Ngrok directement dans le `Dockerfile`, dans le workflow YAML, ou dans un fichier `.env` commité.
- ❌ Faire un `docker run` sans `-d` puis se demander pourquoi l'étape suivante ne s'exécute jamais.
- ❌ Faire un `sleep 120` **avant** de récupérer l'URL Ngrok (vous l'afficherez quand le tunnel sera fermé).
- ❌ Lancer Flask en mode debug (`debug=True`) dans le conteneur — c'est un risque de sécurité en production.
- ❌ Nommer votre workflow `CI.yml`, `CICD.yml`, `main.yml`… donnez-lui un nom **descriptif** (ex. `build-and-expose.yml`). Vous en aurez plusieurs aux exercices suivants ; chacun doit dire ce qu'il fait.

---

## Pour aller plus loin (bonus)

- **Image légère** : faire descendre votre image sous **100 Mo** (regardez `python:*-slim`, `python:*-alpine`, et l'ordre des `COPY`/`RUN` pour le cache).
- **Multi-stage build** : séparer l'étape de build (avec compilateurs) de l'étape d'exécution (juste l'app).
- **Healthcheck** : ajouter une route `/healthz` qui retourne `200 OK`, et la déclarer dans le `Dockerfile` (`HEALTHCHECK`).
- **Durée configurable** : exposer la durée du tunnel (`120` par défaut) comme une **input** du workflow (`workflow_dispatch` accepte des paramètres).
- **Badge Ngrok** : à la fin du workflow, générer un *job summary* (`$GITHUB_STEP_SUMMARY`) avec l'URL Ngrok bien visible.

---

## Livraison

- Une branche `exo-1-docker` (ou similaire), une PR ouverte vers `main`.
- Dans la PR : un screenshot des logs montrant l'URL Ngrok cliquable, et le résultat affiché dans le navigateur.
- Le formateur déclenchera votre workflow lui-même pour vérifier.

---

> Une fois cet exercice validé, passez à l'**[Exercice 2 — Qualité du code & tests automatisés](02-qualite-tests.md)**.
