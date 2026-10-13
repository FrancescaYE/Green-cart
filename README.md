markdown
# 🌿 GreenCart — Azure Infrastructure Project

Projet pédagogique de déploiement d'une application e-commerce sur Microsoft Azure, 
construit dans le cadre de ma montée en compétences vers les certifications 
**AZ-900** puis **AZ-104 (Azure Administrator Associate)**.

> Ce projet n'est pas un exercice de développement : le code applicatif est volontairement 
> minimal. L'objectif est de démontrer la conception, le déploiement, la sécurisation et 
> le troubleshooting d'une infrastructure Azure réelle.

## 🎯 Contexte

GreenCart est une boutique en ligne fictive vendant des produits bio. Le projet simule 
un scénario professionnel : héberger, sécuriser et faire évoluer une infrastructure 
cloud pour une petite entreprise e-commerce.

## 🏗️ Architecture actuelle


Internet
   │
   ├── HTTP :80 (visiteurs)
   └── SSH :22 (administration, IP restreinte)
   │
  NSG (règles entrantes filtrées par IP/port)
   │
  Azure VM (Ubuntu) — rg-greencart-prod
   │
  Nginx :80 → Gunicorn :5000 → Flask
   │
   ├──→ Azure Blob Storage (images produits, accès public lecture seule)
   └──→ Azure SQL Database (catalogue, commandes — via Managed Identity)


## ☁️ Services Azure utilisés

| Service | Rôle | Décision clé |
|---|---|---|
| **Virtual Network + Subnet** | Isolation réseau | Un seul subnet, car un seul composant compute à héberger |
| **Network Security Group** | Filtrage du trafic | SSH restreint à une IP précise (`/32`), HTTP ouvert au public, tout le reste refusé |
| **Virtual Machine (Ubuntu)** | Hébergement de l'application | Gunicorn + Nginx en reverse proxy, géré par Systemd |
| **Storage Account (Blob)** | Images produits | Redondance LRS (projet non critique), accès public au niveau **objet blob** uniquement (pas de liste de fichiers exposée) |
| **Azure SQL Database** | Catalogue, commandes | Authentification **Microsoft Entra ID uniquement** — pas de mot de passe SQL. Connexion depuis l'app via **Managed Identity**, sans secret stocké dans le code |

## 🔐 Décisions de sécurité

- **Pas de mot de passe dans le code** : la VM utilise une identité managée Azure pour s'authentifier à la base de données (`Authentication=ActiveDirectoryMsi`), plutôt qu'une chaîne de connexion avec identifiants.
- **Pare-feu SQL restreint** : seules l'IP de la VM et mon IP d'administration peuvent atteindre la base — la case "Allow Azure services" a été volontairement désactivée pour réduire la surface d'exposition.
- **SAS écarté comme solution** : envisagé pour l'accès au Storage, mais jugé non pérenne (expiration, gestion de token) au profit d'un accès public en lecture pour des images non sensibles par nature.
- **Limite actuelle assumée** : les mots de passe utilisateurs ne sont pas encore hashés — correction prévue en phase Identity & Security (Microsoft Entra ID côté application, RBAC).

## 🛠️ Incidents rencontrés et résolus

| Incident | Diagnostic | Solution |
|---|---|---|
| Connexion SSH en timeout | IP publique personnelle changée (IP dynamique du FAI) | Mise à jour de la règle NSG |
| Erreur 500 "template not found" | Fichier renommé par erreur (`index.html` au lieu de `catalog.html`) | Renommage du fichier |
| Query Editor Azure inaccessible | Conflit entre le pare-feu restreint et l'outil portail (qui requiert "Allow Azure services") | Utilisation ponctuelle de l'option, puis redésactivation |
| Erreur 502 après déploiement | Fichier applicatif non synchronisé entre poste local et VM | Redéploiement du bon fichier, vérification via logs `journalctl` |

## 📍 Avancement du parcours

- [x] Architecture réseau (VNet, Subnet, NSG)
- [x] Compute (VM Linux, Nginx, Gunicorn, Systemd)
- [x] Storage (Blob Storage, images produits)
- [x] Database (Azure SQL, schéma relationnel, Managed Identity)
- [ ] Identity & Security (authentification utilisateur, hashage des mots de passe, RBAC complet)
- [ ] Monitoring (Azure Monitor, alertes)
- [ ] Automatisation (Infrastructure as Code)

## 🎓 Compétences démontrées

Conception réseau • Sécurisation NSG • Déploiement compute Linux • Stockage cloud et 
contrôle d'accès • Bases de données relationnelles Azure • Authentification sans secret 
(Managed Identity) • Méthode de troubleshooting (Observer → Hypothèses → Vérifications → 
Diagnostic → Solution → Validation)
