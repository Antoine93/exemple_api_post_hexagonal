# Analyse Complète du Projet - Architecture Hexagonale API POST

**Date:** 2025-11-06
**Projet:** exemple_api_post_hexagonal
**Analysé par:** Claude Code

---

## 1. Vue d'Ensemble du Projet

**Type:** API REST avec architecture hexagonale (Ports & Adapters)
**Framework:** FastAPI + Hypercorn
**Base de données:** SQLite (par défaut) / MySQL / PostgreSQL (configurable via SQLAlchemy)
**Gestionnaire de paquets:** uv (moderne, ultra-rapide)
**Statut:** Projet fonctionnel avec documentation complète

---

## 2. Structure Architecturale

Le projet suit fidèlement les principes de l'**Architecture Hexagonale** avec une séparation stricte des responsabilités :

```
┌─────────────────────────────────────────────┐
│  ADAPTERS PRIMAIRES (FastAPI)              │
│  • projects_router.py                      │
│  • project_schemas.py (DTOs Pydantic)      │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  PORTS PRIMAIRES (Interfaces)              │
│  • project_use_cases.py (ABC)              │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  DOMAINE (Business Logic)                  │
│  • project.py (Entité)                     │
│  • project_service.py (Service métier)     │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  PORTS SECONDAIRES (Interfaces)            │
│  • project_repository.py (ABC)             │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  ADAPTERS SECONDAIRES (SQLAlchemy)         │
│  • sqlalchemy_project_repository.py        │
│  • ProjectModel (ORM)                      │
└─────────────────────────────────────────────┘
```

### Structure des Fichiers

```
exemple_api_post_hexagonal/
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
├── documents/                         # 📚 Documentation
├── pyproject.toml                     # Configuration du projet et dépendances
├── uv.lock                            # Fichier de verrouillage des versions
├── project_db.sqlite                  # Base de données SQLite
├── create_project.py                  # Script de test automatique
├── create_project_interactive.py      # Script de test interactif
├── .env.example                       # Exemple de configuration
└── .venv/                             # Environnement virtuel
```

---

## 3. Composants Clés et Responsabilités

### 3.1 Domaine (Cœur Métier)

#### **`domain/entities/project.py`**
- **Référence:** src/domain/entities/project.py:10
- **Type:** Entité pure Python (dataclass)
- **Responsabilités:**
  - Encapsulation des données métier
  - Validations métier dans `__post_init__` (lines 29-31)
  - Règles métier:
    - Budget > 0
    - end_date > start_date
    - Nom non vide
  - Méthodes métier: `is_active()`, `days_remaining()`
- **Dépendances:** Zéro dépendance externe ✅
- **Lignes de code:** 55

#### **`domain/services/project_service.py`**
- **Référence:** src/domain/services/project_service.py:10
- **Responsabilités:**
  - Orchestration de la logique métier complexe
  - Dépend uniquement de l'interface `ProjectRepositoryPort` (line 18)
  - Cas d'usage implémentés:
    - `create_project()` - Création avec validation d'unicité
    - `get_project()` - Récupération par ID
  - Validation d'unicité du nom (line 55)
- **Dépendances:** Port secondaire (interface uniquement)
- **Lignes de code:** 94

### 3.2 Ports (Interfaces)

#### **`ports/primary/project_use_cases.py`**
- **Référence:** src/ports/primary/project_use_cases.py:10
- **Type:** Interface ABC (Abstract Base Class)
- **Rôle:** Définit le contrat d'entrée vers le domaine
- **Implémentée par:** `ProjectService`
- **Méthodes:**
  - `create_project()` - Abstract
  - `get_project()` - Abstract

#### **`ports/secondary/project_repository.py`**
- **Référence:** src/ports/secondary/project_repository.py:11
- **Type:** Interface ABC
- **Rôle:** Définit le contrat de persistance
- **Méthodes:**
  - `save()` - Sauvegarde un projet
  - `find_by_id()` - Récupération par ID
  - `find_all()` - Liste tous les projets
  - `exists_by_name()` - Vérification d'unicité
  - `delete()` - Suppression

### 3.3 Adapters

#### **Adapter Primaire - FastAPI**

**Router (src/adapters/primary/fastapi/routers/projects_router.py:17)**
- **Responsabilités:**
  - Exposition des endpoints HTTP
  - Conversion DTO ↔ Entité
  - Gestion des codes HTTP
  - Gestion des erreurs
- **Endpoints:**
  - `POST /api/projects` - Créer un projet (lines 38-106)
  - `GET /api/projects/{id}` - Récupérer un projet (lines 109-161)
- **Injection de dépendances:** Via FastAPI Depends (line 35)
- **Lignes de code:** 162

**Schemas (src/adapters/primary/fastapi/schemas/project_schemas.py)**
- **DTOs Pydantic:**
  - `CreateProjectRequest` - Validation des données entrantes (lines 11-34)
    - Validators personnalisés pour les dates
    - Contraintes: min_length, max_length, gt
  - `ProjectResponse` - Sérialisation de la réponse (lines 37-56)
    - Inclut les champs calculés: `is_active`, `days_remaining`

#### **Adapter Secondaire - SQLAlchemy**

**Repository (src/adapters/secondary/repositories/sqlalchemy_project_repository.py:39)**
- **Responsabilités:**
  - Implémentation concrète du port secondaire
  - Accès aux données via SQLAlchemy
  - Conversion bidirectionnelle: `ProjectModel` ↔ `Project` (line 119)
- **Compatible avec:**
  - SQLite (par défaut)
  - MySQL
  - PostgreSQL
  - Oracle
  - Tout autre SGBD supporté par SQLAlchemy
- **Méthodes implémentées:**
  - `save()` - Persistance avec commit
  - `find_by_id()` - Requête par ID
  - `find_all()` - Liste complète
  - `exists_by_name()` - Count query
  - `delete()` - Suppression avec commit
  - `_to_domain()` - Conversion privée (line 119)
- **Isolation:** Le domaine ne connaît pas SQLAlchemy ✅
- **Lignes de code:** 135

### 3.4 Infrastructure

#### **`di_container.py`**
- **Référence:** src/di_container.py:26
- **Responsabilités:**
  - Configuration de la base de données (lines 29-32)
  - Création automatique des tables (line 53)
  - Injection de dépendances
- **Factories:**
  - `get_db_session()` - Session SQLAlchemy (line 57)
  - `get_project_repository()` - Repository concret (line 67)
  - `get_project_service()` - Service métier (line 82)
- **Configuration:**
  - Variable d'environnement `DATABASE_URL`
  - Valeur par défaut: `sqlite:///./project_db.sqlite`
  - Support multi-BDD via SQLAlchemy
- **Lignes de code:** 117

#### **`main.py`**
- **Référence:** src/main.py:10
- **Responsabilités:**
  - Configuration de l'application FastAPI (lines 10-14)
  - Enregistrement des routers (line 17)
  - Endpoint racine de santé (line 20)
- **Documentation auto-générée:**
  - Swagger UI: `/docs`
  - ReDoc: `/redoc`
  - OpenAPI Schema: `/openapi.json`
- **Lignes de code:** 34

---

## 4. Flux de Données (Exemple POST /api/projects)

```
1. HTTP Request (JSON)
   ↓
2. FastAPI valide avec Pydantic (CreateProjectRequest)
   • Validation des types
   • Validation des contraintes (min_length, gt, etc.)
   • Validation personnalisée des dates
   ↓
3. Router appelle use_cases.create_project()
   • Extraction des données du DTO
   • Passage au service métier via le port primaire
   ↓
4. ProjectService vérifie unicité du nom
   • Appel à repository.exists_by_name()
   • Lève ValueError si le nom existe déjà
   ↓
5. Création de l'entité Project
   • Appel du constructeur dataclass
   • Validation automatique via __post_init__
   • Vérification des règles métier
   ↓
6. Repository.save() convertit Project → ProjectModel
   • Création d'une instance ProjectModel
   • Mapping des attributs
   ↓
7. SQLAlchemy persiste dans la BDD
   • session.add(project_model)
   • session.commit()
   • session.refresh(project_model) - récupère l'ID généré
   ↓
8. Conversion ProjectModel → Project
   • Appel de _to_domain()
   • Retour de l'entité avec ID
   ↓
9. Router convertit Project → ProjectResponse
   • Mapping vers le DTO Pydantic
   • Calcul des champs: is_active(), days_remaining()
   ↓
10. HTTP Response 201 Created (JSON)
    • Sérialisation automatique par FastAPI
    • Headers + Body JSON
```

---

## 5. Règles Métier Implémentées

### Validations dans l'Entité (domain/entities/project.py:33)

**Méthode:** `_validate()`

1. **Nom non vide:**
   ```python
   if not self.name or self.name.strip() == "":
       raise ValueError("Le nom du projet ne peut pas être vide")
   ```

2. **Budget positif:**
   ```python
   if self.budget <= 0:
       raise ValueError("Le budget doit être positif")
   ```

3. **Cohérence des dates:**
   ```python
   if self.end_date <= self.start_date:
       raise ValueError("La date de fin doit être après la date de début")
   ```

### Validations dans le Service (domain/services/project_service.py:55)

**Règle d'unicité:**
```python
if self._repository.exists_by_name(name):
    raise ValueError(f"Un projet avec le nom '{name}' existe déjà")
```

### Validations HTTP (adapters/primary/fastapi/schemas/project_schemas.py:27)

**Contraintes Pydantic:**
- `name`: min_length=1, max_length=255
- `description`: min_length=1
- `budget`: gt=0 (greater than)
- `manager_id`: gt=0
- `end_date`: Validator personnalisé (comparison avec start_date)

---

## 6. Points Forts du Projet

### Architecture

✅ **Isolation parfaite du domaine**
- Aucune dépendance externe dans le domaine
- Logique métier 100% indépendante de l'infrastructure

✅ **Inversion de dépendances**
- Le domaine définit les interfaces (ports)
- Les adapters dépendent du domaine
- Respect du principe de dépendance (DIP)

✅ **Séparation des responsabilités**
- Chaque couche a un rôle précis
- Conversion explicite entre les modèles de données
- Pas de mélange domaine/infrastructure

### Testabilité

✅ **Interfaces permettent le mocking facile**
- Tous les ports sont des ABC
- Injection de dépendances via constructeur
- Tests unitaires possibles sans infrastructure

✅ **Domaine testable en isolation**
- Pas besoin de base de données pour tester le service
- Pas besoin de FastAPI pour tester les entités

### Flexibilité

✅ **Multi-base de données**
- SQLAlchemy supporte: SQLite, MySQL, PostgreSQL, Oracle, SQL Server
- Changement de BDD en modifiant simplement `DATABASE_URL`
- Aucune modification du code métier requise

✅ **Adapters interchangeables**
- Remplacement facile de FastAPI par GraphQL, gRPC, CLI
- Remplacement du repository SQL par MongoDB, Redis, etc.

### Documentation

✅ **Documentation auto-générée**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

✅ **Code bien documenté**
- Docstrings détaillées dans tous les modules
- Commentaires explicatifs pour les concepts complexes
- README.md complet de 546 lignes

### Outillage Moderne

✅ **Gestionnaire de paquets moderne**
- uv: ultra-rapide, gestion automatique de l'environnement virtuel
- Lock file pour reproductibilité
- Support des dépendances optionnelles

✅ **Scripts de test fournis**
- `create_project.py`: Test automatique avec 3 projets exemples
- `create_project_interactive.py`: Test interactif avec saisie utilisateur

✅ **Configuration pour qualité de code**
- black (formatage)
- ruff (linting)
- mypy (type checking)
- pytest (tests)

---

## 7. Points d'Amélioration Potentiels

### Critique (Court Terme)

#### 1. Tests Manquants

**Problème:**
- Aucun répertoire `tests/` détecté
- Pas de tests unitaires, intégration ou E2E

**Recommandation:**
```
tests/
├── unit/
│   ├── test_project_entity.py       # Tests de l'entité
│   └── test_project_service.py      # Tests du service avec mock
├── integration/
│   └── test_sqlalchemy_repository.py  # Tests avec BDD réelle
└── e2e/
    └── test_api_projects.py         # Tests de l'API complète
```

**Exemple de test unitaire:**
```python
def test_create_project_validates_budget():
    with pytest.raises(ValueError, match="budget doit être positif"):
        Project(
            id=None,
            name="Test",
            description="Test",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            budget=-100,  # Budget négatif
            comment=None,
            manager_id=1
        )
```

#### 2. Gestion des Sessions DB

**Problème:**
- Sessions non fermées explicitement dans `di_container.py:64`
- Risque de fuites de connexions
- Pas de gestion du cycle de vie

**Code actuel:**
```python
def get_db_session() -> Session:
    return SessionLocal()  # ❌ Jamais fermée
```

**Recommandation:**
```python
def get_db_session():
    """Dependency FastAPI avec gestion automatique."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # ✅ Fermeture garantie
```

#### 3. Gestion d'Erreurs

**Problème:**
- Capture générique `Exception` dans le router (src/adapters/primary/fastapi/routers/projects_router.py:101)
- Pas de distinction entre types d'erreurs
- Messages d'erreur techniques exposés

**Code actuel:**
```python
except Exception as e:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Erreur lors de la création du projet: {str(e)}"  # ❌ Détails techniques
    )
```

**Recommandation:**
```python
# Créer des exceptions métier
class ProjectAlreadyExistsError(Exception): pass
class ProjectNotFoundError(Exception): pass

# Dans le service
if self._repository.exists_by_name(name):
    raise ProjectAlreadyExistsError(name)

# Dans le router
except ProjectAlreadyExistsError as e:
    raise HTTPException(status_code=409, detail=str(e))
except ProjectNotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### Important (Moyen Terme)

#### 4. Migrations de Base de Données

**Problème:**
- Utilise `Base.metadata.create_all()` (di_container.py:53)
- Pas de versioning des schémas
- Pas de rollback possible

**Recommandation:**
```bash
# Installer Alembic
uv add alembic

# Initialiser
alembic init alembic

# Créer une migration
alembic revision --autogenerate -m "Create projects table"

# Appliquer
alembic upgrade head

# Rollback
alembic downgrade -1
```

#### 5. Logging Structuré

**Problème:**
- Logging minimal avec `print()` statements
- Pas de niveaux de log (DEBUG, INFO, WARNING, ERROR)
- Pas de context (request_id, user_id, etc.)

**Recommandation:**
```python
import logging
import structlog

# Configuration
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Usage
logger.info("project_created", project_id=project.id, name=project.name)
logger.error("project_creation_failed", error=str(e), name=name)
```

#### 6. Authentification/Autorisation

**Problème:**
- Aucune authentification/autorisation
- API publique accessible par tous
- Pas de gestion des permissions

**Recommandation:**
```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/api/projects")
def create_project(
    request: CreateProjectRequest,
    use_cases: ProjectUseCasesDep,
    token: str = Depends(oauth2_scheme)  # ✅ Auth requise
):
    current_user = decode_token(token)
    # Vérifier permissions
    ...
```

### Améliorations (Long Terme)

#### 7. Pagination

**Recommandation:**
```python
@router.get("/api/projects")
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    use_cases: ProjectUseCasesDep
) -> PaginatedProjectResponse:
    projects = use_cases.list_projects(
        offset=(page - 1) * page_size,
        limit=page_size
    )
    return PaginatedProjectResponse(
        items=projects,
        page=page,
        page_size=page_size,
        total=use_cases.count_projects()
    )
```

#### 8. Endpoints CRUD Complets

**Manquants:**
- `PUT /api/projects/{id}` - Mise à jour
- `DELETE /api/projects/{id}` - Suppression
- `GET /api/projects` - Liste avec filtres

#### 9. Observabilité

**Recommandations:**
- **Métriques:** Prometheus + Grafana
- **Tracing:** OpenTelemetry
- **Healthchecks:** `/health`, `/ready`
- **Monitoring:** Sentry pour les erreurs

#### 10. Containerisation

**Recommandation:**
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY src/ ./src/

EXPOSE 8000

CMD ["uv", "run", "hypercorn", "src.main:app", "--bind", "0.0.0.0:8000"]
```

---

## 8. Dépendances Principales

### Production (pyproject.toml:12)

| Package | Version | Rôle |
|---------|---------|------|
| fastapi | >= 0.104.1 | Framework web asynchrone |
| hypercorn | >= 0.16.0 | Serveur ASGI (HTTP/2, HTTP/3) |
| sqlalchemy | >= 2.0.23 | ORM multi-base de données |
| pydantic | >= 2.5.0 | Validation et sérialisation |
| pymysql | >= 1.1.0 | Driver MySQL |
| python-dotenv | >= 1.0.0 | Variables d'environnement |
| httpx | >= 0.28.1 | Client HTTP async |

### Développement (optionnelles)

| Package | Version | Rôle |
|---------|---------|------|
| pytest | >= 7.4.0 | Framework de tests |
| pytest-cov | >= 4.1.0 | Couverture de code |
| pytest-asyncio | >= 0.21.0 | Tests async |
| black | >= 23.0.0 | Formatage de code |
| ruff | >= 0.1.0 | Linting rapide |
| mypy | >= 1.7.0 | Type checking statique |

---

## 9. Configuration et Déploiement

### Base de Données

**Par défaut:** SQLite
- Fichier: `project_db.sqlite` (12 KB)
- Aucune configuration requise
- Parfait pour développement et démo

**Migration vers MySQL:**
```bash
# 1. Créer le fichier .env
cp .env.example .env

# 2. Configurer la connexion
echo "DATABASE_URL=mysql+pymysql://user:password@localhost:3306/project_db" >> .env

# 3. Créer la base de données MySQL
mysql -u root -p -e "CREATE DATABASE project_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 4. Redémarrer l'application
uv run hypercorn src.main:app --reload --bind 0.0.0.0:8000
```

**Migration vers PostgreSQL:**
```bash
# 1. Installer le driver
uv add psycopg2-binary

# 2. Configurer dans .env
echo "DATABASE_URL=postgresql://user:password@localhost:5432/project_db" >> .env

# 3. Créer la base de données
psql -U postgres -c "CREATE DATABASE project_db;"
```

### Lancement de l'Application

**Développement:**
```bash
uv run hypercorn src.main:app --reload --bind 0.0.0.0:8000
```

**Production:**
```bash
uv run hypercorn src.main:app \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Accès aux Services

- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json
- **Health Check:** http://localhost:8000/

---

## 10. Métriques du Code

### Fichiers Clés

| Fichier | Lignes | Responsabilité |
|---------|--------|----------------|
| `src/domain/entities/project.py` | 55 | Entité métier pure |
| `src/domain/services/project_service.py` | 94 | Service métier |
| `src/adapters/secondary/repositories/sqlalchemy_project_repository.py` | 135 | Repository SQLAlchemy |
| `src/adapters/primary/fastapi/routers/projects_router.py` | 162 | API REST |
| `src/adapters/primary/fastapi/schemas/project_schemas.py` | 57 | DTOs Pydantic |
| `src/ports/primary/project_use_cases.py` | 36 | Port primaire |
| `src/ports/secondary/project_repository.py` | 83 | Port secondaire |
| `src/di_container.py` | 117 | DI Container |
| `src/main.py` | 34 | Point d'entrée |
| `README.md` | 546 | Documentation |

### Statistiques Globales

- **Total fichiers Python:** 23 (incluant `__init__.py`)
- **Total lignes domaine:** ~150
- **Total lignes adapters:** ~350
- **Ratio domaine/infrastructure:** ~30% domaine, 70% infrastructure
- **Couverture de tests:** 0% (aucun test détecté)

---

## 11. Conformité Architecture Hexagonale

### Principes Respectés

| Principe | Statut | Détails |
|----------|--------|---------|
| **Domaine indépendant** | ✅ | Aucune dépendance externe dans le domaine |
| **Inversion de dépendances** | ✅ | Dépendances pointent vers le domaine |
| **Ports/Adapters séparés** | ✅ | Interfaces clairement séparées des implémentations |
| **Adapters interchangeables** | ✅ | SQLite ↔ MySQL ↔ PostgreSQL sans modification du domaine |
| **Logique métier isolée** | ✅ | Toute la logique dans le domaine |
| **Conversion explicite** | ✅ | DTOs ↔ Entités ↔ Modèles ORM bien séparés |
| **Testabilité** | ⚠️ | Architecture favorable mais pas de tests |
| **Single Responsibility** | ✅ | Chaque classe a une responsabilité unique |

### Diagramme de Dépendances

```
┌─────────────────────────────────────────────────┐
│                  main.py                        │
│              (Point d'entrée)                   │
└──────────────────┬──────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────┐
│              di_container.py                    │
│         (Injection de dépendances)              │
└─────────┬─────────────────────┬─────────────────┘
          ↓                     ↓
┌─────────────────────┐  ┌─────────────────────────┐
│  projects_router.py │  │ sqlalchemy_repository.py│
│  (Adapter Primary)  │  │ (Adapter Secondary)     │
└─────────┬───────────┘  └─────────┬───────────────┘
          ↓                        ↓
┌─────────────────────┐  ┌─────────────────────────┐
│ project_use_cases.py│  │ project_repository.py   │
│    (Port Primary)   │  │   (Port Secondary)      │
└─────────┬───────────┘  └─────────┬───────────────┘
          └──────────┬─────────────┘
                     ↓
          ┌─────────────────────┐
          │  project_service.py │
          │  project.py         │
          │     (DOMAINE)       │
          └─────────────────────┘
```

**Règle d'or respectée:** Le domaine (en bas) ne dépend de RIEN. Toutes les flèches pointent VERS lui.

---

## 12. Exemples d'Utilisation

### Créer un Projet (via API)

**Requête cURL:**
```bash
curl -X POST "http://localhost:8000/api/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Migration Cloud Azure",
    "description": "Migration de l'\''infrastructure vers Azure Cloud",
    "start_date": "2025-02-01",
    "end_date": "2025-08-31",
    "budget": 250000.00,
    "manager_id": 1,
    "comment": "Priorité haute - Q1 2025"
  }'
```

**Réponse (201 Created):**
```json
{
  "id": 1,
  "name": "Migration Cloud Azure",
  "description": "Migration de l'infrastructure vers Azure Cloud",
  "start_date": "2025-02-01",
  "end_date": "2025-08-31",
  "budget": 250000.0,
  "comment": "Priorité haute - Q1 2025",
  "manager_id": 1,
  "is_active": false,
  "days_remaining": 87
}
```

### Récupérer un Projet

**Requête:**
```bash
curl -X GET "http://localhost:8000/api/projects/1"
```

**Réponse (200 OK):**
```json
{
  "id": 1,
  "name": "Migration Cloud Azure",
  "description": "Migration de l'infrastructure vers Azure Cloud",
  "start_date": "2025-02-01",
  "end_date": "2025-08-31",
  "budget": 250000.0,
  "comment": "Priorité haute - Q1 2025",
  "manager_id": 1,
  "is_active": false,
  "days_remaining": 87
}
```

### Utiliser les Scripts de Test

**Script automatique:**
```bash
# Lance le serveur dans un terminal
uv run hypercorn src.main:app --reload --bind 0.0.0.0:8000

# Dans un autre terminal, exécute le script
uv run python create_project.py
```

**Script interactif:**
```bash
uv run python create_project_interactive.py
# Saisir les informations du projet quand demandé
```

---

## 13. Scénarios de Test Recommandés

### Tests Unitaires du Domaine

**`tests/unit/test_project_entity.py`**
```python
def test_project_validates_budget():
    """Le budget doit être strictement positif."""
    with pytest.raises(ValueError, match="budget doit être positif"):
        Project(
            id=None, name="Test", description="Test",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            budget=-100,  # Invalide
            comment=None, manager_id=1
        )

def test_project_validates_dates():
    """La date de fin doit être après la date de début."""
    with pytest.raises(ValueError, match="date de fin doit être après"):
        Project(
            id=None, name="Test", description="Test",
            start_date=date(2025, 12, 31),
            end_date=date(2025, 1, 1),  # Invalide
            budget=1000, comment=None, manager_id=1
        )

def test_project_is_active():
    """Un projet en cours doit être actif."""
    project = Project(
        id=1, name="Test", description="Test",
        start_date=date.today() - timedelta(days=10),
        end_date=date.today() + timedelta(days=10),
        budget=1000, comment=None, manager_id=1
    )
    assert project.is_active() == True
```

**`tests/unit/test_project_service.py`**
```python
def test_create_project_checks_uniqueness():
    """Ne pas créer un projet avec un nom existant."""
    # Mock du repository
    mock_repo = Mock(spec=ProjectRepositoryPort)
    mock_repo.exists_by_name.return_value = True  # Nom existe déjà

    service = ProjectService(mock_repo)

    with pytest.raises(ValueError, match="existe déjà"):
        service.create_project(
            name="Projet Existant",
            description="Test",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            budget=1000,
            comment=None,
            manager_id=1
        )
```

### Tests d'Intégration

**`tests/integration/test_repository.py`**
```python
@pytest.fixture
def db_session():
    """Fixture pour session de test avec rollback."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

def test_repository_save_and_find(db_session):
    """Sauvegarder et récupérer un projet."""
    repo = SQLAlchemyProjectRepository(db_session)

    project = Project(
        id=None, name="Test Project", description="Test",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        budget=1000, comment=None, manager_id=1
    )

    saved = repo.save(project)
    assert saved.id is not None

    found = repo.find_by_id(saved.id)
    assert found.name == "Test Project"
```

### Tests E2E de l'API

**`tests/e2e/test_api.py`**
```python
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

def test_create_project_success(client):
    """Créer un projet via l'API."""
    response = client.post("/api/projects", json={
        "name": "Test API",
        "description": "Test via API",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "budget": 1000.0,
        "comment": "Test",
        "manager_id": 1
    })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test API"
    assert data["id"] is not None

def test_create_project_duplicate_name(client):
    """Nom dupliqué doit retourner 400."""
    # Créer un projet
    client.post("/api/projects", json={
        "name": "Duplicate", "description": "Test",
        "start_date": "2025-01-01", "end_date": "2025-12-31",
        "budget": 1000.0, "comment": None, "manager_id": 1
    })

    # Tenter de créer un projet avec le même nom
    response = client.post("/api/projects", json={
        "name": "Duplicate", "description": "Test",
        "start_date": "2025-01-01", "end_date": "2025-12-31",
        "budget": 1000.0, "comment": None, "manager_id": 1
    })

    assert response.status_code == 400
    assert "existe déjà" in response.json()["detail"]
```

---

## 14. Roadmap Recommandée

### Phase 1: Stabilisation (Sprint 1-2)

- [ ] Implémenter tests unitaires (couverture > 80%)
- [ ] Corriger la gestion des sessions DB
- [ ] Créer exceptions métier personnalisées
- [ ] Ajouter logging structuré

### Phase 2: Fonctionnalités (Sprint 3-4)

- [ ] Migrer vers Alembic pour les migrations
- [ ] Implémenter PUT /api/projects/{id}
- [ ] Implémenter DELETE /api/projects/{id}
- [ ] Implémenter GET /api/projects avec pagination

### Phase 3: Sécurité (Sprint 5-6)

- [ ] Ajouter authentification JWT
- [ ] Implémenter RBAC (Role-Based Access Control)
- [ ] Ajouter rate limiting
- [ ] Implémenter CORS configuration

### Phase 4: Production (Sprint 7-8)

- [ ] Containeriser avec Docker
- [ ] Configurer CI/CD (GitHub Actions)
- [ ] Ajouter métriques Prometheus
- [ ] Implémenter healthchecks
- [ ] Documenter le déploiement

---

## 15. Ressources et Références

### Documentation du Projet

- **README principal:** README.md (546 lignes)
- **Exemple de configuration:** .env.example
- **Scripts de test:** create_project.py, create_project_interactive.py

### Références Externes

- **Architecture Hexagonale:** Alistair Cockburn (2005)
- **FastAPI:** https://fastapi.tiangolo.com/
- **SQLAlchemy:** https://www.sqlalchemy.org/
- **Pydantic:** https://docs.pydantic.dev/
- **uv:** https://docs.astral.sh/uv/

### Patterns et Principes

- **Ports & Adapters** (Hexagonal Architecture)
- **Dependency Inversion Principle** (DIP)
- **Single Responsibility Principle** (SRP)
- **Interface Segregation Principle** (ISP)
- **Repository Pattern**
- **Service Layer Pattern**

---

## 16. Conclusion

### Résumé Exécutif

Le projet **exemple_api_post_hexagonal** est une **implémentation exemplaire** d'une architecture hexagonale en Python. Il démontre une compréhension solide des principes architecturaux suivants:

1. **Séparation des préoccupations:** Domaine pur isolé de l'infrastructure
2. **Inversion de dépendances:** Adapters dépendent du domaine via des interfaces
3. **Testabilité:** Architecture favorable aux tests (bien que non implémentés)
4. **Flexibilité:** Support multi-BDD sans modification du code métier

### Points Saillants

**Forces Majeures:**
- Architecture propre et bien structurée
- Code lisible avec documentation exhaustive
- Outillage moderne (uv, FastAPI, SQLAlchemy 2.0)
- Support multi-base de données natif

**Lacunes Principales:**
- Absence totale de tests
- Gestion basique des erreurs
- Pas de migrations versionnées
- Aucune sécurité (auth/authz)

### Recommandation

**Pour un projet de démonstration/apprentissage:** ⭐⭐⭐⭐⭐ (5/5)
Le projet atteint parfaitement son objectif pédagogique.

**Pour un projet de production:** ⭐⭐⭐☆☆ (3/5)
Nécessite les améliorations critiques listées dans la section 7 avant déploiement:
1. Tests complets
2. Gestion sécurisée des sessions DB
3. Authentification/Autorisation
4. Logging et monitoring
5. Migrations avec Alembic

### Prochaines Actions Prioritaires

1. **Immédiat:** Implémenter les tests (section 13)
2. **Court terme:** Corriger la gestion des sessions DB
3. **Moyen terme:** Ajouter authentification et migrations
4. **Long terme:** Compléter le CRUD et containeriser

---

**Date de génération:** 2025-11-06
**Version du document:** 1.0
**Analysé par:** Claude Code (Sonnet 4.5)
