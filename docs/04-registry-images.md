# Exercice 4 — Publier l'image sur un registry

**Niveau** : Avancé
**Durée estimée** : 2 heures
**Pré-requis** : Exercices 1, 2 et 3 validés.

---

## Scénario

Le projet décolle. Vous n'êtes plus seul à travailler dessus. L'équipe d'à côté veut **réutiliser votre image** pour ses propres tests de bout-en-bout, sans avoir à cloner votre repo et à tout rebuilder.

Le commercial, lui, vous tanne pour avoir une **version stable** à montrer aux prospects, **différente** des versions « brouillon » sur lesquelles vous travaillez tous les jours.

> « Faites-moi un endroit où je peux récupérer une image qui marche, avec un nom de version clair. Et que ce soit la dernière construite par votre pipeline, automatiquement. »

C'est le rôle d'un **registry d'images** — un dépôt versionné pour vos `Dockerfile` cuits. Vous allez utiliser **GHCR** (GitHub Container Registry), gratuit et intégré au workflow.

---

## Objectifs pédagogiques

À la fin de l'exercice, vous saurez :

- Distinguer **build** et **distribution** d'une image
- Publier sur **GHCR** (`ghcr.io`)
- Définir une **stratégie de tags** (latest, sha, pr, semver)
- Authentifier un workflow auprès d'un registry sans gérer de PAT (token personnel)
- Faire **pull-then-run** au lieu de **build-and-run**

---

## Cahier des charges

1. Le workflow construit l'image puis la **publie** sur `ghcr.io/<votre-user>/<votre-repo>`.
2. **Stratégie de tags** au minimum :
   - `latest` → mis à jour à chaque push sur `main`,
   - `sha-<short>` → un tag immuable par commit (les 7 premiers caractères du SHA suffisent),
   - `pr-<numéro>` → quand un push vient d'une Pull Request.
3. Le job `ngrok` (exposition publique) **ne reconstruit plus l'image** : il fait `docker pull` depuis GHCR, puis `docker run`. Vérifiable en lisant le workflow : aucune occurrence de `docker build` dans ce job.
4. L'image publiée est **visible publiquement** sur la page *Packages* de votre dépôt GitHub.
5. Le `README.md` documente la commande de pull (« comment récupérer l'image construite par ce projet »).

---

## Critères de validation

- [ ] Sur votre dépôt GitHub, **onglet Code → section Packages** (à droite) : votre image apparaît.
- [ ] Plusieurs tags sont listés : au moins `latest` + un `sha-…`.
- [ ] Une commande `docker pull ghcr.io/<user>/<repo>:latest` depuis n'importe quelle machine connectée fonctionne (l'image est publique ou les droits sont OK).
- [ ] Le job `ngrok` du workflow contient un `docker pull` mais pas de `docker build`.
- [ ] **Test de provocation** : ouvrez une PR depuis une branche. Sur la page *Packages*, un tag `pr-<numéro>` doit apparaître. Quand la PR est fermée/mergée, ce tag peut subsister (c'est OK) mais `latest` doit pointer sur le nouveau commit de `main`.
- [ ] La chaîne complète d'exécution est : `quality → security → build-push → ngrok`. Visible sur le graphe de l'action.

---

## Indices (sans solution)

<details>
<summary><strong>Indice 1 — Authentification GHCR</strong></summary>

Bonne nouvelle : pour pousser sur GHCR **depuis un workflow du même dépôt**, vous **n'avez pas besoin** d'un Personal Access Token. Le `GITHUB_TOKEN` automatique suffit, à condition de lui donner les bonnes permissions :

```yaml
permissions:
  contents: read
  packages: write
```

Cette déclaration peut se faire au niveau du job ou du workflow. Mauvaise pratique : la mettre globalement et largement, ce qui élargit la surface d'attaque inutilement.
</details>

<details>
<summary><strong>Indice 2 — Actions Docker officielles</strong></summary>

Trois actions à connaître, toutes maintenues par Docker :

- **`docker/login-action`** : se connecter à un registry.
- **`docker/build-push-action`** : build + push en une étape, avec gestion du cache.
- **`docker/metadata-action`** : **génère automatiquement** les tags et labels selon le contexte (branche, PR, tag git). Lisez sa doc : 80 % de la stratégie de tags est gérée par cette action sans que vous écriviez la moindre logique.

Lisez **leurs README sur GitHub Marketplace** avant de chercher ailleurs.
</details>

<details>
<summary><strong>Indice 3 — Nom de l'image</strong></summary>

Sur GHCR, le format est `ghcr.io/<owner>/<image>`. `<owner>` est le user ou l'organisation propriétaire du repo, en **minuscules**. L'expression `${{ github.repository }}` vaut `owner/repo` — mais attention à la casse (GHCR refuse les majuscules).

`metadata-action` peut gérer ça pour vous (`images: ghcr.io/${{ github.repository }}` puis il normalise).
</details>

<details>
<summary><strong>Indice 4 — Cache de layers</strong></summary>

Sans cache, chaque build CI réinstalle vos dépendances Python depuis zéro. Avec un cache, le build d'incrément prend quelques secondes. `build-push-action` propose les options `cache-from` et `cache-to` qui peuvent stocker le cache dans GitHub Actions ou directement dans le registry. Mesurez le gain.
</details>

<details>
<summary><strong>Indice 5 — Image privée vs publique</strong></summary>

Par défaut sur GHCR, l'image héritée d'un repo public reste **privée** tant que vous ne l'autorisez pas. Allez sur la page de votre package → *Package settings* → *Change visibility*. Sans ça, votre évaluateur ne pourra pas faire `docker pull` sans s'authentifier.

Alternative : laisser l'image privée et fournir un token de lecture limité. Plus sûr en vrai contexte pro, mais inutile pour cet exercice.
</details>

<details>
<summary><strong>Indice 6 — Pull-then-run dans le job ngrok</strong></summary>

Une fois l'image publiée, votre job `ngrok` n'a plus besoin du code source. Il peut être déclaré avec `needs: build-push` et exécuter simplement :

```bash
docker pull ghcr.io/<user>/<repo>:<tag>
docker run -d -p ... ghcr.io/<user>/<repo>:<tag>
```

Mais **quel tag pull ?** Réfléchissez : si vous prenez `latest`, vous risquez de récupérer une version plus récente que celle que vous venez de construire (race condition). Préférez le tag `sha-` correspondant au **commit en cours**.
</details>

---

## Anti-patterns à éviter

- ❌ Utiliser un **PAT (Personal Access Token)** stocké en secret pour s'authentifier à GHCR, alors que `GITHUB_TOKEN` suffit dans le même dépôt. Plus de secrets = plus de surface d'attaque.
- ❌ Tagger toutes vos images en `latest` et basta. Sans tag immuable (sha, semver), vous ne pouvez jamais revenir en arrière proprement.
- ❌ Pousser des images sans les avoir scannées (rappel exercice 3). L'étape de scan se met **avant** le push, pas après.
- ❌ Faire `docker push` à la main depuis votre poste « parce que c'est plus rapide ». L'intérêt du registry est qu'il **trace** quel pipeline a produit quelle image.
- ❌ Pousser sur Docker Hub avec votre login perso pour un projet d'école. Utilisez GHCR — c'est intégré, c'est gratuit, et vous n'exposez pas vos identifiants Hub.

---

## Pour aller plus loin (bonus)

- **Multi-arch** : construire pour `linux/amd64` ET `linux/arm64` avec `buildx`. Votre Codespace est amd64, mais une image bien faite doit tourner aussi sur ARM (Mac Apple Silicon, Raspberry Pi, serveurs ARM cloud). Bonne occasion d'apprendre `docker buildx`.
- **Sémantique versionnée** : sur tag git `v1.2.3`, publier les tags `1.2.3`, `1.2`, `1` (et `latest`). `metadata-action` gère ça nativement.
- **Provenance & attestation** : générer une attestation **SLSA** pour l'image (preuve cryptographique que c'est bien votre pipeline qui l'a produite). Action GitHub : `actions/attest-build-provenance`.
- **Nettoyage automatique** : ajouter un workflow programmé (`schedule: cron`) qui supprime les tags `sha-` et `pr-` de plus de 30 jours. GHCR a une API REST pour ça.
- **Mode déploiement réel** : remplacer Ngrok par un déploiement automatique sur une vraie plateforme (Fly.io, Render, Railway, etc.) qui *pull* depuis GHCR à chaque push sur `main`. Là vous tenez un vrai pipeline de production.

---

## Livraison

- Branche `exo-4-registry`, PR vers `main`.
- Dans la description de PR :
  - URL publique de la page *Packages*,
  - Commande `docker pull` à essayer,
  - Capture du graphe d'action complet (`quality → security → build-push → ngrok`).
- L'évaluateur fera un `docker pull` depuis sa machine pour vérifier.

---

## Et après ?

Vous avez maintenant un **pipeline DevOps complet** :

```
push  →  lint + tests  →  scan sécurité  →  build + push image  →  exposition publique
        (qualité)        (sécurité)        (distribution)         (démo client)
```

Ce schéma est, à peu de choses près, celui de la plupart des équipes pro. Les briques supplémentaires en environnement réel :

- déploiement sur infra (Kubernetes, ECS, Fly.io…) au lieu de Ngrok,
- monitoring & alerting (Prometheus, Grafana, Sentry…),
- observabilité (logs structurés, tracing distribué),
- gestion d'environnements (dev / staging / prod),
- infrastructure as code (Terraform, Pulumi…).

Si vous voulez aller plus loin, attaquez l'une de ces briques en **mini-projet libre**. Le formateur peut vous orienter.

---

> Bravo — vous avez fini l'atelier. Mettez à jour votre `README.md` avec un résumé de ce que VOUS avez construit, et liez les preuves (badges, URL packages, URL d'un run réussi). C'est le portfolio que vous montrerez en entretien.
