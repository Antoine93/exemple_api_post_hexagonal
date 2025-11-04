# Exemple POST /api/projects - Architecture Hexagonale

Implémentation complète d'un endpoint POST avec architecture hexagonale (Ports & Adapters) en Python avec FastAPI.

## Structure du Projet

```
exemple_post/
├── src/
│   ├── domain/                        # 🔷 DOMAINE (Business Logic)
│   │   ├── entities/
│   │   │   └── project.py             # Entité Project (logique métier pure)
│   │   └── services/
│   │       └── project_service.py     # Service métier
│   │
│   ├── ports/                         # 🔌 PORTS (Interfaces)
│   │   ├── primary/
│   │   │   └── project_use_cases.py  # Interface des cas d'usage
│   │   └── secondary/
│   │       └── project_repository.py  # Interface du repository
│   │
│   ├── adapters/                      # 🔌 ADAPTERS (Implémentations)
│   │   ├── primary/
│   │   │   └── fastapi/
│   │   │       ├── routers/
│   │   │       │   └── projects_router.py  # Routes FastAPI
│   │   │       └── schemas/
│   │   │           └── project_schemas.py  # DTOs Pydantic
│   │   └── secondary/
│   │       └── repositories/
│   │           └── sqlalchemy_project_repository.py  # Implémentation SQLAlchemy
│   │
│   ├── di_container.py                # 💉 Injection de dépendances
│   └── main.py                        # 🚀 Point d'entrée
│
├── pyproject.toml                     # Configuration du projet et dépendances
├── uv.lock                            # Fichier de verrouillage des versions (généré)
└── .venv/                             # Environnement virtuel (généré)
```

## Principe de l'Architecture Hexagonale

### Flux des Dépendances

```
┌─────────────────────────────────────────────┐
│         ADAPTERS PRIMAIRES (FastAPI)        │
│                     ↓                        │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│         PORTS PRIMAIRES (Interfaces)        │
│                     ↓                        │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│              DOMAINE (Métier)               │
│          Business Rules Only                │
│                     ↓                        │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│        PORTS SECONDAIRES (Interfaces)       │
│                     ↓                        │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│         ADAPTERS SECONDAIRES (MySQL)        │
└─────────────────────────────────────────────┘
```

**Règle fondamentale:** Le domaine ne dépend de RIEN - Toutes les dépendances pointent VERS le domaine.

## Installation

### Prérequis

- Python 3.10+
- MySQL 8.0+
- [uv](https://docs.astral.sh/uv/) - Gestionnaire de paquets Python ultra-rapide

### Installer uv

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Étapes d'installation

1. **Synchroniser les dépendances:**

```bash
uv sync
```

Cette commande va automatiquement :
- Créer un environnement virtuel `.venv`
- Installer toutes les dépendances du projet
- Verrouiller les versions dans `uv.lock`

2. **Installer aussi les dépendances de développement:**

```bash
uv sync --all-extras
```

3. **Configuration de la base de données (optionnel):**

Par défaut, le projet utilise **SQLite** (aucune configuration nécessaire).

**Pour utiliser SQLite (par défaut) :**
Rien à faire ! Un fichier `project_db.sqlite` sera créé automatiquement au démarrage.

**Pour utiliser MySQL :**
1. Créer un fichier `.env` à la racine du projet (copier `.env.example`)
2. Définir la variable `DATABASE_URL` :
   ```bash
   DATABASE_URL=mysql+pymysql://user:password@localhost:3306/project_db
   ```
3. Créer la base de données MySQL :
   ```sql
   CREATE DATABASE project_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

**Pour utiliser PostgreSQL :**
1. Dans le fichier `.env` :
   ```bash
   DATABASE_URL=postgresql://user:password@localhost:5432/project_db
   ```
2. Ajouter la dépendance :
   ```bash
   uv add psycopg2-binary
   ```

## Démarrage de l'Application

### Lancer le serveur FastAPI avec Hypercorn

```bash
# Méthode recommandée : utiliser uv run
uv run hypercorn src.main:app --reload --bind 0.0.0.0:8000
```

Pas besoin d'activer manuellement l'environnement virtuel ! `uv run` s'en charge automatiquement.

**Pourquoi Hypercorn ?**
- Support HTTP/2 et HTTP/3
- Compatible ASGI (comme Uvicorn)
- Meilleure gestion des connexions WebSocket
- Support de plusieurs workers

L'API sera accessible sur: `http://localhost:8000`

### Documentation API

FastAPI génère **automatiquement** une documentation interactive pour votre API. Vous n'avez rien à configurer !

- **Swagger UI:** http://localhost:8000/docs
  - Interface interactive pour tester vos endpoints
  - Permet d'exécuter des requêtes directement depuis le navigateur
  - Générée automatiquement à partir de vos routes et schémas Pydantic

- **ReDoc:** http://localhost:8000/redoc
  - Documentation alternative avec un design épuré
  - Idéale pour lire et comprendre l'API

- **OpenAPI Schema:** http://localhost:8000/openapi.json
  - Schéma OpenAPI brut au format JSON
  - Utilisable avec des outils tiers (Postman, Insomnia, etc.)

#### Comment ça fonctionne ?

Dans `src/main.py`, la simple déclaration de l'application FastAPI active ces endpoints :

```python
app = FastAPI(
    title="Project Management API",
    description="API de gestion de projets avec architecture hexagonale",
    version="1.0.0"
)
```

**Aucune configuration supplémentaire nécessaire !** FastAPI analyse automatiquement :
- Vos routes (decorators `@router.post`, `@router.get`, etc.)
- Vos schémas Pydantic (`CreateProjectRequest`, `ProjectResponse`)
- Vos types de retour et paramètres
- Votre documentation dans les docstrings

#### Désactiver la documentation (production)

Si vous souhaitez désactiver ces endpoints en production :

```python
app = FastAPI(
    title="Project Management API",
    docs_url=None,      # Désactive /docs
    redoc_url=None,     # Désactive /redoc
    openapi_url=None    # Désactive /openapi.json
)
```

## Utilisation de l'API

### Scripts de test rapide

Deux scripts sont fournis pour tester rapidement l'API :

**1. Script automatique (3 projets d'exemple) :**
```bash
uv run python create_project.py
```

**2. Script interactif (vous saisissez les données) :**
```bash
uv run python create_project_interactive.py
```

### POST /api/projects - Créer un projet

**Requête:**

```bash
curl -X POST "http://localhost:8000/api/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Projet Alpha",
    "description": "Description du projet Alpha",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "budget": 100000.50,
    "comment": "Commentaire optionnel",
    "manager_id": 1
  }'
```

**Réponse (201 Created):**

```json
{
  "id": 1,
  "name": "Projet Alpha",
  "description": "Description du projet Alpha",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "budget": 100000.5,
  "comment": "Commentaire optionnel",
  "manager_id": 1,
  "is_active": true,
  "days_remaining": 252
}
```

### GET /api/projects/{project_id} - Récupérer un projet

**Requête:**

```bash
curl -X GET "http://localhost:8000/api/projects/1"
```

**Réponse (200 OK):**

```json
{
  "id": 1,
  "name": "Projet Alpha",
  "description": "Description du projet Alpha",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "budget": 100000.5,
  "comment": "Commentaire optionnel",
  "manager_id": 1,
  "is_active": true,
  "days_remaining": 252
}
```

## Règles Métier Implémentées

### Validation dans l'Entité (domain/entities/project.py)

1. **Nom du projet:** Ne peut pas être vide
2. **Budget:** Doit être strictement positif (> 0)
3. **Dates:** La date de fin doit être après la date de début

### Validation dans le Service (domain/services/project_service.py)

1. **Unicité du nom:** Un projet avec le même nom ne peut pas déjà exister

### Validation HTTP (adapters/primary/fastapi/schemas/project_schemas.py)

1. **Format des données:** Validation Pydantic des types et formats
2. **Contraintes:** min_length, max_length, gt (greater than)

## Composants Clés

### 1. Entité du Domaine (domain/entities/project.py)

- **Responsabilité:** Contenir la logique métier liée à l'entité
- **Dépendances:** Aucune (Python pur)
- **Méthodes métier:** `is_active()`, `days_remaining()`

### 2. Port Secondaire (ports/secondary/project_repository.py)

- **Responsabilité:** Définir le contrat de persistance
- **Type:** Interface abstraite (ABC)
- **Méthodes:** save, find_by_id, find_all, exists_by_name, delete

### 3. Service du Domaine (domain/services/project_service.py)

- **Responsabilité:** Orchestrer la logique métier complexe
- **Dépendances:** Port secondaire (interface uniquement)
- **Cas d'usage:** create_project, get_project

### 4. Port Primaire (ports/primary/project_use_cases.py)

- **Responsabilité:** Définir le contrat d'entrée vers le domaine
- **Type:** Interface abstraite (ABC)
- **Implémenté par:** ProjectService

### 5. Adapter Secondaire (adapters/secondary/repositories/sqlalchemy_project_repository.py)

- **Responsabilité:** Implémenter l'accès aux données avec SQLAlchemy
- **Dépendances:** SQLAlchemy, port secondaire
- **Conversion:** ProjectModel (ORM) ↔ Project (entité)
- **Compatible avec:** SQLite, MySQL, PostgreSQL, Oracle, etc.

### 6. Schemas Pydantic (adapters/primary/fastapi/schemas/project_schemas.py)

- **Responsabilité:** Définir les DTOs HTTP
- **DTOs:** CreateProjectRequest, ProjectResponse
- **Validation:** Format HTTP et contraintes de base

### 7. Router FastAPI (adapters/primary/fastapi/routers/projects_router.py)

- **Responsabilité:** Exposer les endpoints HTTP
- **Dépendances:** Port primaire (interface)
- **Gestion:** Conversion DTO ↔ Entité, codes HTTP

### 8. DI Container (di_container.py)

- **Responsabilité:** Câbler les dépendances
- **Factories:** get_db_session, get_project_repository, get_project_service
- **Injection:** Repository dans Service

### 9. Point d'Entrée (main.py)

- **Responsabilité:** Configurer et démarrer FastAPI
- **Configuration:** Enregistrement des routers

## SQLAlchemy : ORM Multi-Base de Données

### Pourquoi SQLAlchemy ?

**SQLAlchemy** est un ORM (Object-Relational Mapping) qui fait le pont entre Python et SQL.

**Avantage clé : Multi-base de données**
- Un seul code Python
- Compatible avec SQLite, MySQL, PostgreSQL, Oracle, etc.
- Changez de BDD en modifiant simplement `DATABASE_URL`

### Configuration actuelle

**Par défaut : SQLite** (aucune installation requise)
```python
DATABASE_URL = "sqlite:///./project_db.sqlite"
```

**Passer à MySQL :**
```bash
# Dans le fichier .env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/project_db
```

**Passer à PostgreSQL :**
```bash
# Dans le fichier .env
DATABASE_URL=postgresql://user:password@localhost:5432/project_db
```

### Architecture & SQLAlchemy

```
┌─────────────────────────────┐
│  DOMAINE                    │
│  class Project              │  ← Entité métier pure (Python pur)
│    - days_remaining()       │
└─────────────────────────────┘
            ↕ (conversion)
┌─────────────────────────────┐
│  ADAPTER (SQLAlchemy)       │
│  class ProjectModel(Base)   │  ← Modèle technique (table SQL)
│  class SQLAlchemyRepository │  ← Convertit Project ↔ ProjectModel
└─────────────────────────────┘
            ↕
┌─────────────────────────────┐
│  BASE DE DONNÉES            │
│  SQLite / MySQL / Postgres  │  ← SQLAlchemy traduit en SQL
└─────────────────────────────┘
```

**Le domaine ne sait pas quelle BDD est utilisée !** C'est l'essence de l'architecture hexagonale.

## Avantages de Cette Architecture

### ✅ Isolation du Domaine

Le domaine est complètement isolé de l'infrastructure:
- Aucune dépendance à FastAPI
- Aucune dépendance à SQLAlchemy
- Testable sans infrastructure

### ✅ Flexibilité

Changements faciles sans toucher au domaine:
- Changer de base de données (SQLite → MySQL → PostgreSQL) en modifiant simplement DATABASE_URL
- Remplacer FastAPI par GraphQL, CLI, etc.
- Changer les DTOs sans affecter le métier
- Utiliser MongoDB en créant un nouvel adapter qui implémente ProjectRepositoryPort

### ✅ Testabilité

Tests unitaires du domaine sans infrastructure:
- Mock du repository (port secondaire)
- Tests de la logique métier pure
- Pas besoin de base de données pour tester

### ✅ Maintenabilité

Séparation claire des responsabilités:
- Chaque couche a un rôle précis
- Modifications localisées
- Code facile à comprendre

## Points d'Attention

### ❌ Anti-Patterns à Éviter

1. **Service dépend de l'adapter:** Le service doit dépendre de l'INTERFACE, pas de l'implémentation
2. **Logique métier dans le router:** Toute logique métier doit être dans le domaine
3. **Entité = Modèle ORM:** Séparer l'entité domaine du modèle technique
4. **Pas de conversion DTO → Entité:** Ne jamais passer un DTO Pydantic au domaine
5. **Validation uniquement dans DTO:** Dupliquer les validations métier dans l'entité

## Prochaines Étapes

Pour aller plus loin avec cet exemple:

1. **Ajouter des tests:**
   - Tests unitaires du domaine
   - Tests d'intégration des adapters
   - Tests E2E de l'API

2. **Ajouter d'autres endpoints:**
   - PUT /api/projects/{id} (mise à jour)
   - DELETE /api/projects/{id} (suppression)
   - GET /api/projects (liste paginée)

3. **Améliorer le DI Container:**
   - Utiliser dependency-injector
   - Gérer le cycle de vie des sessions DB
   - Ajouter des scopes (singleton, request, etc.)

4. **Ajouter des fonctionnalités:**
   - Authentification et autorisation
   - Logging structuré
   - Gestion d'erreurs avancée
   - Migrations avec Alembic

## Références

- **Document source:** `documents/implementation_architecture_hexagonale.md`
- **Architecture Hexagonale:** Alistair Cockburn
- **FastAPI:** https://fastapi.tiangolo.com/
- **SQLAlchemy:** https://www.sqlalchemy.org/
- **Pydantic:** https://docs.pydantic.dev/

## Gestion des Dépendances avec uv

### Ajouter une nouvelle dépendance

```bash
# Ajouter une dépendance de production
uv add requests

# Ajouter une dépendance de développement
uv add --dev pytest-mock

# Ajouter une dépendance optionnelle dans un groupe
uv add --optional dev black
```

### Mettre à jour les dépendances

```bash
# Mettre à jour toutes les dépendances
uv lock --upgrade

# Mettre à jour une dépendance spécifique
uv lock --upgrade-package fastapi
```

### Supprimer une dépendance

```bash
uv remove nom-du-package
```

### Exécuter des commandes sans activer le venv

```bash
# Lancer le serveur
uv run hypercorn src.main:app --reload --bind 0.0.0.0:8000

# Exécuter Python
uv run python script.py

# Exécuter pytest
uv run pytest

# Exécuter black
uv run black src/

# Exécuter ruff
uv run ruff check src/
```

### Utiliser des outils one-off avec uvx

```bash
# Exécuter un outil sans l'installer dans le projet
uvx ruff check .
uvx black --check .
uvx mypy src/
```

---

**Date:** 23-10-2025
**Version:** 2.0 - Migration vers uv
