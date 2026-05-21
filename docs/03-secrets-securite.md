# Exercice 3 — Secrets et sécurité de l'image

**Niveau** : Intermédiaire+
**Durée estimée** : 1 à 2 heures
**Pré-requis** : Exercices 1 et 2 validés.

---

## Scénario

Bonne nouvelle : votre client est ravi. Mauvaise nouvelle : son **responsable sécurité** vient de demander à voir votre pipeline.

> « Trois choses non négociables : vos secrets ne fuient nulle part, votre conteneur ne tourne pas en root, et votre image est scannée pour les vulnérabilités connues avant d'aller en démo. Si une CVE *critical* est détectée, le déploiement est bloqué. »

Cet exercice traite des **trois piliers défensifs** du DevOps :

1. **Gestion de secrets** — où les mettre, comment les transmettre, comment vérifier qu'ils ne fuient pas.
2. **Durcissement d'image** — un conteneur n'est PAS une VM, mais on peut quand même réduire la surface d'attaque.
3. **Scan automatique de vulnérabilités** — c'est gratuit, c'est intégrable, il n'y a pas d'excuse pour ne pas le faire.

---

## Objectifs pédagogiques

À la fin de l'exercice, vous saurez :

- Différencier *secret* et *variable d'environnement*
- Utiliser un utilisateur **non-root** dans un conteneur
- Intégrer un **scanner de vulnérabilités** (Trivy ou équivalent) dans un workflow
- Configurer un scan pour **échouer le pipeline** sur des CVE critiques
- Lire un rapport de scan et interpréter une CVE

---

## Cahier des charges

### Partie A — Secrets

1. **Aucun secret en clair**, nulle part : ni dans le `Dockerfile`, ni dans le workflow, ni dans un fichier commité, ni dans un `print`/`echo` de log.
2. Le token Ngrok est lu depuis un **secret GitHub** (déjà fait en exercice 1 — vérifiez bien).
3. Si votre app utilise une *secret key* Flask, elle est passée par **variable d'environnement**, pas codée en dur.
4. Ajouter un job ou une étape qui **vérifie l'absence de patterns sensibles** dans le dépôt (mots-clés style `API_KEY=`, `password=`, format de token). Outils possibles : `gitleaks`, `trufflehog`, ou un simple `grep` documenté.

### Partie B — Durcissement de l'image

5. Le `Dockerfile` doit créer un **utilisateur non-root** et l'utiliser via `USER`.
6. L'image de base doit être **minimale** (variantes `slim` ou `alpine` — justifiez votre choix).
7. Le `pip install` ne doit pas embarquer de cache inutile (`--no-cache-dir`).

### Partie C — Scan de vulnérabilités

8. Ajouter un **job `security`** dans le workflow qui :
   - construit (ou récupère) l'image,
   - exécute un **scanner de vulnérabilités** (recommandé : Trivy, action officielle d'Aqua Security),
   - **fait échouer le pipeline** si une vulnérabilité de sévérité **`CRITICAL`** est détectée.
9. Le job `ngrok` doit dépendre de **`quality` ET `security`** (chaîne complète : quality → security → ngrok).

---

## Critères de validation

- [ ] `grep -ri 'authtoken\|api_key\|password\|secret' .` ne révèle **aucune** valeur sensible (les noms de variables, oui ; les valeurs, non).
- [ ] Dans le `Dockerfile`, on trouve un `USER` qui n'est **pas** `root`. Vérifiable depuis le terminal de votre Codespace : `docker run --rm <image> id` doit retourner un UID **différent de 0**.
- [ ] L'image de base est **slim** ou équivalent (justification dans un commentaire du Dockerfile ou dans la PR).
- [ ] Le job de scan apparaît dans la liste des jobs de l'action.
- [ ] **Test de provocation 1** : remplacez votre image de base par une version **volontairement ancienne** (ex. `python:3.6` ou `python:3.8`). Poussez. Le scan doit révéler des CVE et **bloquer le pipeline**.
- [ ] **Test de provocation 2** : essayez d'`echo` votre token Ngrok dans une étape (`echo "$NGROK_AUTHTOKEN"`). Vérifiez que GitHub le **masque automatiquement** en `***`. (Pensez à retirer ce echo après le test !)
- [ ] La chaîne `quality → security → ngrok` est visible sur le graphe de l'action.

---

## Indices (sans solution)

<details>
<summary><strong>Indice 1 — Variables d'environnement vs secrets vs args de build</strong></summary>

Trois mécanismes différents, à ne pas confondre :

- **`ARG`** dans un Dockerfile : disponible **pendant le build**, finit dans l'historique de l'image — **pas pour un secret**.
- **`ENV`** dans un Dockerfile : disponible au runtime, visible dans `docker inspect`.
- **`docker run -e SECRET=…`** : visible dans les processus de l'hôte (`ps`), mais pas dans l'image — acceptable pour un secret runtime.
- **Docker BuildKit secrets (`--secret`)** : pour passer un secret pendant le build sans qu'il finisse dans une couche.

Pour Ngrok en CI, la voie la plus simple est `-e` au `docker run`, alimenté par `${{ secrets.NGROK_AUTHTOKEN }}`.
</details>

<details>
<summary><strong>Indice 2 — Créer un utilisateur dans le Dockerfile</strong></summary>

Sous Debian/Ubuntu : `RUN useradd -m -u 1000 appuser`. Sous Alpine : `adduser -D appuser`. Ensuite, `USER appuser`. Attention à **l'ordre** : tout ce qui suit `USER` ne pourra plus écrire dans les dossiers root. Faites les installs **avant** le switch d'user.

Pensez aussi à la propriété des fichiers : `COPY --chown=appuser:appuser …` évite les problèmes de permissions.
</details>

<details>
<summary><strong>Indice 3 — Slim vs Alpine</strong></summary>

`python:3.x-slim` est basé sur Debian, plus petit que l'image standard mais avec **glibc** (donc moins de surprises avec les wheels Python). `python:3.x-alpine` est encore plus petit mais utilise **musl** : certaines bibliothèques Python avec extensions C posent problème. Pour cette app simple, les deux marchent ; `slim` est plus sûr pour démarrer.
</details>

<details>
<summary><strong>Indice 4 — Trivy</strong></summary>

Aqua Security fournit une **action GitHub officielle** (`aquasecurity/trivy-action`). Vous lui donnez le nom de votre image (locale ou distante) et elle scanne. Les paramètres utiles : `severity`, `exit-code`, `ignore-unfixed`. Lisez le README de l'action — 3 minutes de lecture.

Comportement type :
```
exit-code: '1'
severity: 'CRITICAL'
```
…fera échouer le job dès qu'une CVE *critical* est trouvée. À vous d'élargir ou de restreindre selon votre politique.
</details>

<details>
<summary><strong>Indice 5 — Détection de secrets dans le code</strong></summary>

`gitleaks` et `trufflehog` ont des actions GitHub prêtes à l'emploi. `gitleaks-action` est probablement la plus simple à brancher. Le scan tourne sur tout l'historique : si vous avez **un jour** commité un secret, même supprimé après, il sera détecté. (Et c'est tant mieux.)
</details>

<details>
<summary><strong>Indice 6 — Si Trivy trouve trop de choses</strong></summary>

C'est normal. Une image Python standard contient des centaines de paquets, dont certains ont des CVE *low* ou *medium* permanentes. Restreignez d'abord la sévérité à `CRITICAL`. Vous pouvez aussi ignorer les CVE **sans correctif disponible** avec `ignore-unfixed: true` (sinon vous bloquez sur des choses incorrigibles).
</details>

---

## Anti-patterns à éviter

- ❌ Commiter un `.env` qui contient des vrais secrets « juste pour tester ». Une fois pushé, le secret est **définitivement compromis** — même si vous le supprimez ensuite.
- ❌ Mettre `USER root` à la fin du Dockerfile parce que « ça marche pas sinon ». Diagnostiquez la vraie cause (permissions, port < 1024, etc.).
- ❌ Désactiver Trivy parce qu'il trouve trop de CVE. C'est *le* signal que vous traitez : auditez avant de désactiver.
- ❌ Stocker l'image sur Docker Hub publiquement avec votre token Ngrok en `ENV`. Tout le monde peut le lire.
- ❌ Faire `echo "${{ secrets.X }}" > /tmp/secret.txt` puis lire le fichier ailleurs : oui, GitHub masque les logs, mais l'écrire en clair sur disque rend le secret accessible aux étapes suivantes via *log injection* dans les sorties de processus tiers.

---

## Pour aller plus loin (bonus)

- **Multi-stage build** : une étape « builder » qui compile/installe, une étape « runtime » qui ne contient que le strict nécessaire. Comparez la taille des deux images.
- **Image distroless** (Google) : `gcr.io/distroless/python3` — encore plus minimal, pas de shell. Plus dur à débugger mais bien plus sûr.
- **SBOM** : générer une *Software Bill of Materials* (liste de tous les composants de l'image) avec `syft` ou Trivy. Attachez-la comme artefact du workflow.
- **Signature d'image** : signer l'image construite avec `cosign` (Sigstore). Permet à un consommateur de vérifier qu'elle vient bien de votre pipeline.
- **Politique de sévérité** : documentez dans un fichier `SECURITY.md` votre politique — quelles sévérités bloquent, quelles sont tolérées et pourquoi.
- **Dependabot** : activez Dependabot sur le dépôt pour qu'il propose des PR de mise à jour des dépendances vulnérables.

---

## Livraison

- Branche `exo-3-securite`, PR vers `main`.
- Dans la PR : capture des deux tests de provocation (image volontairement vulnérable → bloqué, token → masqué).
- Le formateur fera lui-même un `docker run … id` sur votre image pour vérifier l'UID.

---

> Une fois cet exercice validé, passez à l'**[Exercice 4 — Publier l'image sur un registry](04-registry-images.md)**.
