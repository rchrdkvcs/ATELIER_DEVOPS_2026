# Atelier DevOps — Conteneurisation, CI/CD et exposition publique

> Atelier court (~1 journée) autour de Docker, GitHub Actions, Ngrok, et de la qualité d'un pipeline de livraison logicielle.

---

## Présentation

Vous allez prendre une petite application Flask et la faire passer **de « ça tourne sur ma machine »** à un livrable industrialisé :

- conteneurisée (Docker)
- validée automatiquement (tests + lint en CI)
- durcie (secrets, scan de vulnérabilités, utilisateur non-root)
- publiée (registry d'images)
- exposable publiquement à un évaluateur via une URL temporaire (Ngrok)

L'atelier est **progressif** : les premiers exercices sont guidés, les derniers sont ouverts façon mini-projet. **Aucune solution n'est fournie dans ce dépôt** — c'est intentionnel. Vous trouverez des objectifs, des critères de validation **observables**, et des indices ciblés. La doc officielle est votre meilleure alliée.

---

## Pré-requis

- Un **compte GitHub** (avec accès aux *Codespaces* — inclus dans l'offre gratuite)
- Un **compte Ngrok** gratuit (vous récupérerez un *authtoken*)
- Bases : ligne de commande, Git, requêtes HTTP, langage Python

> **Pas d'installation à faire sur votre poste.** Tout l'atelier se déroule dans un **GitHub Codespace** : votre éditeur (VS Code dans le navigateur), Git, Python et Docker sont déjà là, prêts à l'emploi. Voir la section *Démarrer* ci-dessous.

## Environnement de travail — GitHub Codespaces

Le dépôt contient un fichier `.devcontainer/devcontainer.json` qui décrit l'environnement attendu : Python 3.12, Docker disponible, GitHub CLI, quelques extensions VS Code utiles. Au lancement d'un Codespace, GitHub provisionne automatiquement cet environnement.

**Pourquoi Codespaces et pas votre laptop ?**

- Tout le monde a le même environnement (pas de « ça marche chez moi »).
- Pas de souci de version de Docker, de Python, ni de droits administrateur.
- Vos ports Flask sont **forwardés automatiquement** : VS Code vous donne une URL `*.app.github.dev` cliquable pour tester avant même d'écrire le workflow.
- Un Codespace s'arrête tout seul quand vous ne l'utilisez pas (économie d'heures).

**Limites à connaître** : un compte GitHub gratuit dispose de ~60 h/mois de Codespaces (au moment de cet atelier — vérifiez votre quota). Pensez à **stopper** votre Codespace quand vous prenez une pause (commande `Codespaces: Stop Current Codespace` dans VS Code).

---

## Compétences travaillées

| Domaine | Compétences |
|---|---|
| **Conteneurisation** | Dockerfile, image, conteneur, ports, multi-stage build |
| **CI/CD** | GitHub Actions, jobs, dépendances entre jobs, déclencheurs, secrets |
| **Qualité logicielle** | Tests unitaires, lint, couverture de code, gates de qualité |
| **Sécurité** | Gestion de secrets, scan de vulnérabilités, principe de moindre privilège |
| **Distribution** | Registry d'images (GHCR), stratégie de tags, versioning |
| **Exposition** | Tunnel public temporaire, port forwarding, durée de vie d'un environnement éphémère |

---

## Structure de l'atelier

| # | Exercice | Niveau | Durée |
|---|---|---|---|
| **1** | [Conteneuriser Flask & exposer via Ngrok](docs/01-conteneurisation-ngrok.md) | Débutant | 2–3 h |
| **2** | [Qualité du code & tests automatisés](docs/02-qualite-tests.md) | Intermédiaire | 1–2 h |
| **3** | [Secrets & sécurité de l'image](docs/03-secrets-securite.md) | Intermédiaire+ | 1–2 h |
| **4** | [Publier l'image sur un registry](docs/04-registry-images.md) | Avancé | 2 h |

Les exercices se font **dans l'ordre** : chacun s'appuie sur le pipeline construit au précédent.

---

## L'application fournie

Un mini-serveur Flask de quelques lignes :

- `/` — page d'accueil
- `/exercices/` — votre page personnelle (`templates/exercices.html`)

**Première chose à faire** : ouvrir `templates/exercices.html` et y mettre votre **prénom et votre nom**. Cette personnalisation permettra à l'évaluateur de vérifier qu'il visite bien VOTRE déploiement et pas celui du voisin.

> Note : le code fourni est volontairement imparfait. C'est à vous d'identifier ce qui doit changer pour qu'il fonctionne *dans un conteneur*, *en production*, *en sécurité*. Ne cherchez pas une réponse unique — cherchez la bonne pratique.

---

## Démarrer

1. **Fork** ce dépôt sur votre compte GitHub (pas un clone — un *fork*).
2. Sur la page de votre fork, cliquez sur le bouton vert **`<> Code`** → onglet **Codespaces** → **`Create codespace on main`**. Patientez 1 à 2 minutes pendant le provisionnement.
3. Une fois VS Code ouvert dans le navigateur, ouvrez un terminal (`Terminal → New Terminal`) et vérifiez que tout est OK :
   ```bash
   docker --version
   python --version
   git --version
   ```
4. Lisez ce README en entier, puis l'énoncé de l'**Exercice 1**.
5. Travaillez **chaque exercice sur une branche dédiée** (`exo-1-docker`, `exo-2-tests`, …) et ouvrez une **Pull Request** vers `main`.
6. Cochez les critères de validation au fur et à mesure dans la description de la PR.

---

## Règles de l'atelier

- **Pas de copier-coller sans avoir lu et compris.** L'évaluateur posera des questions sur votre pipeline. « Je ne sais pas pourquoi ça marche » coûte cher.
- **Aucun secret en clair**, jamais. Ni dans un commit, ni dans un log, ni dans un commentaire, ni dans un screenshot.
- **Un commit = un changement logique cohérent.** Un commit qui mélange « ajoute Docker » + « renomme une route » + « corrige un typo » est rejeté.
- **Les logs CI sont la preuve.** Si un évaluateur ne peut pas vérifier un critère en lisant vos logs ou votre dépôt, ce critère n'est **pas validé**.
- **L'IA générative est un outil, pas un binôme.** Vous avez le droit de l'utiliser, vous n'avez pas le droit de ne pas comprendre ce qu'elle produit.

---

## Grille d'évaluation (sur 20)

| Critère | Points |
|---|---|
| Exercice 1 — Docker + GitHub Action + Ngrok fonctionnels | **6** |
| Exercice 2 — Tests automatisés et lint en CI, gate qualité | **4** |
| Exercice 3 — Secrets gérés proprement, image scannée, non-root | **4** |
| Exercice 4 — Image publiée sur un registry, tags cohérents | **4** |
| Qualité globale — commits propres, README à jour, soin général | **2** |

Bonus possibles : voir la section *Pour aller plus loin* à la fin de chaque exercice.

---

## Si vous êtes bloqué

Dans cet ordre, sans en sauter :

1. **Relire l'énoncé** et les **critères de validation** de l'exercice.
2. **Reproduire dans votre Codespace AVANT de pousser.** Cycle CI ≈ 2 min, cycle Codespace ≈ 5 s. Vous itérerez 20× plus vite — un `docker build` qui échoue se diagnostique en 10 secondes dans un terminal, contre 2 minutes par run GitHub Actions.
3. **Lire les logs de l'action en entier**, pas seulement la ligne rouge — la cause est souvent 30 lignes plus haut.
4. Chercher le **message d'erreur exact** dans la **doc officielle** (pas un blog de 2018).
5. Demander à un binôme — *expliquer* le problème suffit souvent à le résoudre seul.
6. Demander au formateur, en ayant **déjà** passé les étapes 1 à 5.

---

## Qualité locale

Dans un Codespace fraîchement ouvert, installez les dépendances de développement puis lancez les vérifications :

```bash
python -m pip install -r requirements-dev.txt
ruff check .
ruff format --check .
pytest
```

`pytest` exécute les tests Flask et vérifie aussi que la couverture reste au-dessus de 50 %.

---

## Image publiée

Après un run réussi sur `main`, l'image Docker est publiée sur GitHub Container Registry :

```bash
docker pull ghcr.io/rchrdkvcs/atelier_devops_2026:latest
```

Chaque commit publié dispose aussi d'un tag immuable `sha-<commit-court>`.

---

## Ressources officielles

Pas de copier-coller, allez à la source :

- **Docker** — `docs.docker.com` (sections : *Dockerfile reference*, *Best practices*, *Build cache*)
- **GitHub Actions** — `docs.github.com/actions` (sections : *Workflow syntax*, *Encrypted secrets*, *Using jobs*)
- **Ngrok** — `ngrok.com/docs` (sections : *Getting started*, *Agent CLI*)
- **Flask** — `flask.palletsprojects.com` (sections : *Testing*, *Deploying*)
- **Trivy** (scan d'image) — `aquasecurity.github.io/trivy`
- **GHCR** — `docs.github.com` → *Working with the Container registry*

---

## Licence et contributions

Atelier pédagogique. Forkez, modifiez, partagez vos améliorations en *issue* ou en *PR* sur le dépôt d'origine. Les retours d'étudiants (passages bloquants, ambiguïtés, bugs dans les énoncés) sont les bienvenus.
