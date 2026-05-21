# Exercice 2 — Qualité du code et tests automatisés

**Niveau** : Intermédiaire
**Durée estimée** : 1 à 2 heures
**Pré-requis** : Exercice 1 validé (pipeline Docker + Ngrok fonctionnel).

---

## Scénario

Votre démo de l'exercice 1 a séduit. Le client veut continuer le projet, mais il pose une condition :

> « Je ne veux pas qu'un développeur puisse pousser un commit cassé et que ça déploie quand même. Avant d'exposer le site, validez-moi qu'il fonctionne au moins un minimum. »

C'est le rôle d'un **pipeline CI** : refuser un changement avant qu'il atteigne la production. On parle de **gate qualité**.

Dans cet exercice, vous allez ajouter un **étage de validation** en amont du déploiement. Si les tests ou le lint échouent, **le job Ngrok ne doit pas se lancer**.

---

## Objectifs pédagogiques

À la fin de l'exercice, vous saurez :

- Écrire des **tests unitaires** pour une application Flask
- Configurer un **linter** Python
- Faire dépendre un job d'un autre dans GitHub Actions (`needs:`)
- Forcer un échec du pipeline quand un test ou le lint échoue
- Mesurer la **couverture de code** (bonus)

---

## Cahier des charges

1. Ajouter **au moins 2 tests unitaires** sur les routes Flask (`/` et `/exercices/`).
   - Au minimum : vérifier que le code HTTP est `200`, et qu'une chaîne attendue apparaît dans la réponse.
2. Ajouter un **linter Python** au projet (au choix : `ruff`, `flake8`, ou `pylint`).
   - La configuration doit être **dans le dépôt** (fichier de config, pas juste des arguments CLI).
3. Modifier votre workflow GitHub Actions pour qu'il contienne **au moins deux jobs distincts** :
   - un job `quality` qui exécute lint + tests,
   - le job `ngrok` (de l'exercice 1) qui **dépend** de `quality`.
4. Une **erreur de lint** ou un **test cassé** doit faire **échouer le pipeline** (statut rouge sur GitHub) **et empêcher** le job Ngrok de démarrer.
5. Le `README.md` (ou un fichier dédié) doit indiquer **comment lancer les tests dans le Codespace** (ou n'importe quel environnement disposant de Python et des dépendances).

---

## Critères de validation

- [ ] Le dépôt contient un dossier de tests (`tests/`) avec au moins 2 fichiers de tests pertinents.
- [ ] Il existe un fichier de configuration de linter (`pyproject.toml`, `.flake8`, `.ruff.toml`, etc.).
- [ ] Sur la page **Actions** du repo, il y a un job `quality` (ou nommé similairement) qui s'exécute **avant** le job de déploiement Ngrok.
- [ ] **Test de provocation 1** : ajoutez volontairement un commit qui contient une faute de lint évidente (variable inutilisée, import inutile, etc.). Le pipeline doit virer **au rouge**. Le job Ngrok doit afficher `skipped`.
- [ ] **Test de provocation 2** : modifiez un test pour qu'il échoue. Même résultat.
- [ ] Sur une branche propre, le pipeline est **vert** et le tunnel Ngrok démarre.
- [ ] Le `README.md` explique en 2-3 lignes comment installer les dépendances et lancer les tests **dans un Codespace fraîchement ouvert** (commandes copiables).

---

## Indices (sans solution)

<details>
<summary><strong>Indice 1 — Tester du Flask</strong></summary>

Flask fournit un **client de test** (`app.test_client()`) qui simule des requêtes HTTP sans réseau. Cherchez « *Flask testing* » dans la doc officielle — il y a un exemple en 5 lignes.

Pour `pytest`, par convention vos fichiers s'appellent `test_*.py` ou `*_test.py` et vos fonctions `test_*`.
</details>

<details>
<summary><strong>Indice 2 — Quel linter choisir ?</strong></summary>

`ruff` est moderne, ultra-rapide, et combine plusieurs outils (linter + formateur). `flake8` est plus ancien mais ultra-répandu. `pylint` est strict (parfois trop). N'importe lequel des trois fait l'affaire. Choisissez-en **un** et documentez votre choix.

Au passage : regardez ce que dit le linter à propos de votre `__init__.py` actuel. Il y a peut-être un import qui ne sert à rien…
</details>

<details>
<summary><strong>Indice 3 — Dépendances entre jobs</strong></summary>

Dans GitHub Actions, un job déclaré avec `needs: <autre_job>` ne démarre que si l'autre s'est terminé en succès. Lisez la doc « *Using jobs* → *Defining prerequisite jobs* ».
</details>

<details>
<summary><strong>Indice 4 — Faire échouer un job</strong></summary>

Un job échoue dès qu'**une commande renvoie un code de sortie non nul**. `pytest` et `ruff` font déjà ça naturellement. Vous n'avez en général rien à ajouter pour transformer un échec de test en échec de pipeline — la magie shell s'en occupe.
</details>

<details>
<summary><strong>Indice 5 — Dépendances Python en CI</strong></summary>

Si vous n'avez pas encore de `requirements.txt`, c'est le bon moment d'en faire un. Réfléchissez : faut-il **les mêmes** dépendances pour faire tourner l'app et pour la tester ? Souvent non — `pytest`, `ruff` etc. n'ont rien à faire en production. Cherchez « *requirements-dev.txt* » ou les *extras* dans `pyproject.toml`.
</details>

<details>
<summary><strong>Indice 6 — Action GitHub officielle Python</strong></summary>

Il existe une action `actions/setup-python` qui installe la version Python de votre choix sur le runner. Évitez de réinventer l'installation manuelle.
</details>

---

## Anti-patterns à éviter

- ❌ Désactiver des règles de lint en masse pour faire passer le job — si une règle vous gêne souvent, **vous avez probablement un vrai problème**, pas un mauvais linter.
- ❌ Écrire un test qui ne teste rien (ex. : `assert True`). L'évaluateur regardera vos tests.
- ❌ Mettre les tests dans le même fichier que l'application.
- ❌ Lancer les tests dans le **même job** que le déploiement (vous perdez l'effet « gate »).
- ❌ Ignorer la couverture sans regarder : un test qui passe sur 5 % du code ne prouve rien.

---

## Pour aller plus loin (bonus)

- **Couverture** : ajouter `pytest-cov` et faire **échouer le job si la couverture descend sous 50 %** (option `--cov-fail-under`).
- **Badge** : ajouter un badge de statut CI dans le `README` (`https://github.com/<user>/<repo>/actions/workflows/<workflow>.yml/badge.svg`).
- **Cache des dépendances** : utiliser `actions/cache` pour éviter de réinstaller `pip` à chaque run. Mesurez le gain de temps.
- **Matrix build** : lancer les tests sur **plusieurs versions de Python** (3.10, 3.11, 3.12) en parallèle via `strategy.matrix`.
- **Formateur** : ajouter un check `ruff format --check` ou `black --check`. Si le code n'est pas formaté, ça échoue.
- **Pre-commit hook** : installer `pre-commit` pour faire tourner lint+tests **avant le push**.

---

## Livraison

- Branche `exo-2-tests` (ou similaire), PR vers `main`.
- Dans la description de PR : capture des 3 runs (vert, faute de lint rouge, test cassé rouge).
- Tests passants dans un Codespace fraîchement créé : `pytest` doit fonctionner sans configuration supplémentaire (après installation des dépendances documentée).

---

> Une fois cet exercice validé, passez à l'**[Exercice 3 — Secrets & sécurité de l'image](03-secrets-securite.md)**.
