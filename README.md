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
│   │           └── mysql_project_repository.py  # Implémentation MySQL
│   │
│   ├── di_container.py                # 💉 Injection de dépendances
│   └── main.py                        # 🚀 Point d'entrée
│
└── requirements.txt                   # Dépendances Python
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

### Étapes d'installation

1. **Créer un environnement virtuel:**

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

2. **Installer les dépendances:**

```bash
pip install -r requirements.txt
```

3. **Configurer la base de données:**

Modifier la variable `DATABASE_URL` dans `src/di_container.py`:

```python
DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/project_db"
```

4. **Créer la base de données:**

```sql
CREATE DATABASE project_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## Démarrage de l'Application

### Lancer le serveur FastAPI

```bash
cd src
python main.py
```

Ou avec uvicorn directement:

```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible sur: `http://localhost:8000`

### Documentation API

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Utilisation de l'API

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

### 5. Adapter Secondaire (adapters/secondary/repositories/mysql_project_repository.py)

- **Responsabilité:** Implémenter l'accès aux données MySQL
- **Dépendances:** SQLAlchemy, port secondaire
- **Conversion:** ProjectModel (ORM) ↔ Project (entité)

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

## Avantages de Cette Architecture

### ✅ Isolation du Domaine

Le domaine est complètement isolé de l'infrastructure:
- Aucune dépendance à FastAPI
- Aucune dépendance à SQLAlchemy
- Testable sans infrastructure

### ✅ Flexibilité

Changements faciles sans toucher au domaine:
- Remplacer MySQL par PostgreSQL, MongoDB, etc.
- Remplacer FastAPI par GraphQL, CLI, etc.
- Changer les DTOs sans affecter le métier

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

---

**Date:** 23-10-2025
**Version:** 1.0
=======
# exemple_api_post_hexagonal
>>>>>>> 3bad4a89e8e7af485d3f67ae079cbe6271bad3b1
