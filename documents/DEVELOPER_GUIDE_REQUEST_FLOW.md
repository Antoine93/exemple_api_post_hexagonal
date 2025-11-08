# Guide Développeur : Implémenter un Request Flow Complet

**Guide de référence pour implémenter une nouvelle fonctionnalité de A à Z**

**Date:** 2025-11-07
**Version:** 1.1
**Architecture:** Hexagonale (Ports & Adapters)
**Public:** Développeurs rejoignant le projet

---

## Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Conventions de Nommage](#conventions-de-nommage)
3. [Checklist Rapide](#checklist-rapide)
4. [Étape 1: Définir l'Entité du Domaine](#étape-1-définir-lentité-du-domaine)
5. [Étape 2: Créer les Ports (Interfaces)](#étape-2-créer-les-ports-interfaces)
6. [Étape 3: Implémenter le Service Métier](#étape-3-implémenter-le-service-métier)
7. [Étape 4: Créer l'Adapter Repository](#étape-4-créer-ladapter-repository)
8. [Étape 5: Créer les DTOs (Schemas)](#étape-5-créer-les-dtos-schemas)
9. [Étape 6: Implémenter le Router FastAPI](#étape-6-implémenter-le-router-fastapi)
10. [Étape 7: Tests (TDD)](#étape-7-tests-tdd)
11. [Règles Strictes par Couche](#règles-strictes-par-couche)
12. [Anti-Patterns à Éviter](#anti-patterns-à-éviter)
13. [Exemple Complet: Feature "Tasks"](#exemple-complet-feature-tasks)
14. [Checklist de Validation](#checklist-de-validation)

---

## Vue d'ensemble

### Qu'est-ce qu'un Request Flow ?

Un **Request Flow** (flux de requête) est le parcours complet d'une requête HTTP à travers toutes les couches de l'architecture hexagonale, du client jusqu'à la base de données et retour.

### Architecture en Couches

```
┌─────────────────────────────────────────────────────────────┐
│  HTTP CLIENT                                                │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  1. PRIMARY ADAPTER (FastAPI Router)                        │
│     • Reçoit les requêtes HTTP                              │
│     • Valide le format HTTP (Pydantic)                      │
│     • Convertit DTO → Entité                                │
│     Fichier: src/adapters/primary/fastapi/routers/         │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  2. PRIMARY PORT (Interface Use Cases)                      │
│     • Définit le CONTRAT d'entrée                           │
│     • Interface abstraite (ABC)                             │
│     Fichier: src/ports/primary/                            │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  3. DOMAIN SERVICE                                          │
│     • Orchestre la logique métier                           │
│     • Applique les règles business                          │
│     • AUCUNE dépendance externe                             │
│     Fichier: src/domain/services/                          │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  4. DOMAIN ENTITY                                           │
│     • Contient les données métier                           │
│     • Valide ses propres règles                             │
│     • Python pur (dataclass)                                │
│     Fichier: src/domain/entities/                          │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  5. SECONDARY PORT (Interface Repository)                   │
│     • Définit le CONTRAT de persistance                     │
│     • Interface abstraite (ABC)                             │
│     Fichier: src/ports/secondary/                          │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  6. SECONDARY ADAPTER (Repository Implementation)           │
│     • Implémente l'accès aux données                        │
│     • Convertit Entité ↔ Modèle ORM                         │
│     • Code technique (SQLAlchemy)                           │
│     Fichier: src/adapters/secondary/repositories/          │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  DATABASE (SQLite / MySQL / PostgreSQL)                     │
└─────────────────────────────────────────────────────────────┘
```

### Principe Fondamental: Inversion de Dépendances

**RÈGLE D'OR:** Toutes les dépendances pointent VERS le domaine.

```
Adapters → Ports → Domain
   ↓        ↓        ↑
Dépendent  Définit  Ne dépend
  du       le       de RIEN
domaine  contrat
```

---

## Conventions de Nommage

### 🌍 Règle Fondamentale : Anglais pour le Code, Français pour les Commentaires

Ce projet suit une convention stricte de nommage pour assurer la cohérence et la lisibilité internationale du code.

#### ✅ EN ANGLAIS (obligatoire)

**Tous les éléments de code doivent être nommés en anglais :**

- **Noms de fichiers** : `project_type.py`, `user_repository.py`, `task_service.py`
- **Classes** : `ProjectService`, `UserRepository`, `TaskEntity`
- **Méthodes et fonctions** : `calculate_progress()`, `get_user()`, `create_project()`
- **Variables** : `user_id`, `project_name`, `total_hours`
- **Constantes** : `MAX_RETRIES`, `DEFAULT_TIMEOUT`
- **Attributs de classe** : `created_at`, `updated_at`, `is_active`
- **Paramètres de fonction** : `user_id: int`, `start_date: date`
- **Valeurs d'énumération** : `ProjectType.INTERNAL`, `Status.ACTIVE`

**Exemples :**

```python
# ✅ CORRECT
class ProjectType(str, Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
    MAINTENANCE = "MAINTENANCE"

class ProjectService:
    def calculate_progress(self, project_id: int) -> float:
        project = self._repository.find_by_id(project_id)
        return project.calculate_advancement()
```

```python
# ❌ INCORRECT
class TypeProjet(str, Enum):
    INTERNE = "INTERNE"
    EXTERNE = "EXTERNE"

class ServiceProjet:
    def calculer_avancement(self, projet_id: int) -> float:
        projet = self._depot.trouver_par_id(projet_id)
        return projet.calculer_avancement()
```

#### ✅ EN FRANÇAIS (recommandé)

**Tous les commentaires et documentation doivent être en français :**

- **Docstrings de modules** : Description du fichier en français
- **Docstrings de classes** : Explication du rôle de la classe
- **Docstrings de méthodes** : Description de la fonction, paramètres, retour, exceptions
- **Commentaires inline** : Explications du code
- **Messages d'erreur** : Messages aux développeurs
- **Logs de debug** : Messages de logging

**Exemples :**

```python
# ✅ CORRECT
class ProjectService:
    """
    Service métier pour la gestion des projets.

    Ce service contient la logique métier complexe qui va au-delà
    des simples règles de validation d'une entité.
    """

    def calculate_progress(self, project_id: int) -> float:
        """
        Calcule le pourcentage d'avancement d'un projet.

        Args:
            project_id: L'identifiant unique du projet

        Returns:
            Pourcentage d'avancement (0-100%)

        Raises:
            ProjectNotFoundError: Si le projet n'existe pas
        """
        # Récupérer le projet depuis le repository
        project = self._repository.find_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError(f"Projet {project_id} introuvable")

        # Calculer via la méthode métier de l'entité
        return project.calculate_advancement()
```

#### 📋 Exemples Comparatifs

| Élément | ❌ Incorrect | ✅ Correct |
|---------|-------------|-----------|
| Fichier | `type_projet.py` | `project_type.py` |
| Classe | `TypeProjet` | `ProjectType` |
| Enum value | `INTERNE` | `INTERNAL` |
| Méthode | `calculer_avancement()` | `calculate_progress()` |
| Variable | `heures_reelles` | `actual_hours` |
| Paramètre | `projet_id` | `project_id` |
| Docstring | (vide ou anglais) | "Calcule le pourcentage..." |
| Commentaire | `# Calculate hours` | `# Calcule les heures` |

#### 🎯 Rationnelle

**Pourquoi l'anglais pour le code ?**
- Compatibilité internationale et réutilisabilité
- Cohérence avec les libraries Python (Pydantic, FastAPI, SQLAlchemy)
- Facilite la contribution de développeurs non-francophones
- Standard de l'industrie pour le code source

**Pourquoi le français pour les commentaires ?**
- Équipe principalement francophone
- Documentation métier en français
- Facilite la compréhension du domaine métier
- Règles business spécifiques au contexte français

#### ⚠️ Exceptions Autorisées

**Seulement dans ces cas spécifiques :**

1. **Valeurs métier stockées en base** : Si le client demande explicitement des valeurs en français dans la DB
2. **Messages utilisateur final** : Affichés dans l'interface (mais utiliser i18n)
3. **Noms de tables/colonnes legacy** : Si migration depuis système existant

**Ces exceptions doivent être documentées et justifiées.**

---

## Checklist Rapide

Avant de commencer, assurez-vous d'avoir:

- [ ] Compris les règles métier de la fonctionnalité
- [ ] Identifié l'entité du domaine concernée
- [ ] Défini les cas d'usage (use cases)
- [ ] Vérifié qu'aucune entité/port existant ne convient
- [ ] Préparé les tests (approche TDD recommandée)

**Ordre d'implémentation recommandé:**

1. ✅ Entité du domaine
2. ✅ Ports (interfaces)
3. ✅ Service métier
4. ✅ Adapter repository
5. ✅ DTOs (schemas)
6. ✅ Router FastAPI
7. ✅ Tests (à chaque étape idéalement)

---

## Étape 1: Définir l'Entité du Domaine

### Localisation
```
src/domain/entities/votre_entite.py
```

### Template

```python
"""
Entité [NOM] du domaine.

Cette entité représente [DESCRIPTION MÉTIER].

Règles métier:
- [Règle 1]
- [Règle 2]
- [Règle 3]
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class VotreEntite:
    """
    Entité [NOM] avec validation métier intégrée.

    Attributes:
        id: Identifiant unique (None si pas encore persisté)
        champ1: Description du champ
        champ2: Description du champ
    """

    # Attributs (types explicites OBLIGATOIRES)
    id: Optional[int]
    champ_requis: str
    champ_optionnel: Optional[str]
    date_creation: datetime

    def __post_init__(self) -> None:
        """Validation automatique à la création."""
        self._validate()

    def _validate(self) -> None:
        """
        Valide les règles métier de l'entité.

        Raises:
            ValueError: Si une règle métier n'est pas respectée
        """
        if not self.champ_requis or self.champ_requis.strip() == "":
            raise ValueError("Le champ_requis ne peut pas être vide")

        # Autres validations métier...

    def methode_metier(self) -> bool:
        """
        Logique métier de l'entité.

        Returns:
            Résultat du calcul métier
        """
        # Implémentation...
        pass
```

### ✅ CE QUI EST PERMIS

```python
# Imports autorisés
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict
from enum import Enum
from decimal import Decimal

# Méthodes métier
def calculer_total(self) -> float:
    return self.prix * self.quantite

# Méthodes de validation
def est_valide(self) -> bool:
    return self.statut == "actif"

# Properties pour logique métier
@property
def nom_complet(self) -> str:
    return f"{self.prenom} {self.nom}"
```

### ❌ CE QUI EST INTERDIT

```python
# ❌ INTERDIT: Imports externes
from fastapi import HTTPException        # NON
from sqlalchemy import Column            # NON
from pydantic import BaseModel           # NON

# ❌ INTERDIT: Accès direct à la base de données
def save(self):
    db.session.add(self)  # NON

# ❌ INTERDIT: Logique d'infrastructure
def send_email(self):
    smtp.send(...)  # NON

# ❌ INTERDIT: Dépendances à d'autres couches
def to_json(self):
    return jsonify(self)  # NON
```

### 🧪 Tests pour l'Entité

```python
# tests/unit/domain/test_votre_entite.py

def test_entite_creation_valide():
    """Une entité valide doit être créée sans erreur."""
    entite = VotreEntite(
        id=None,
        champ_requis="valeur",
        champ_optionnel=None,
        date_creation=datetime.now()
    )
    assert entite.champ_requis == "valeur"

def test_entite_rejette_champ_vide():
    """Un champ vide doit lever une ValueError."""
    with pytest.raises(ValueError, match="ne peut pas être vide"):
        VotreEntite(
            id=None,
            champ_requis="",  # Invalide
            champ_optionnel=None,
            date_creation=datetime.now()
        )

def test_methode_metier():
    """La méthode métier doit calculer correctement."""
    entite = VotreEntite(...)
    resultat = entite.methode_metier()
    assert resultat == valeur_attendue
```

---

## Étape 2: Créer les Ports (Interfaces)

### 2A. Port Primaire (Use Cases)

**Localisation:** `src/ports/primary/votre_use_cases.py`

```python
"""
Port primaire: interface des cas d'usage pour [ENTITÉ].

Ce port définit le CONTRAT que le domaine expose vers l'extérieur.
Les adapters primaires (API, CLI) dépendent de cette interface.
"""
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List
from src.domain.entities.votre_entite import VotreEntite


class VotreUseCasesPort(ABC):
    """
    Interface des cas d'usage pour [ENTITÉ].

    Cette interface définit les opérations métier que le domaine
    expose aux adapters primaires.
    """

    @abstractmethod
    def creer_entite(
        self,
        champ1: str,
        champ2: Optional[str],
        champ3: date
    ) -> VotreEntite:
        """
        Crée une nouvelle entité.

        Args:
            champ1: Description du champ
            champ2: Description du champ optionnel
            champ3: Description du champ date

        Returns:
            L'entité créée avec son ID

        Raises:
            EntityAlreadyExistsError: Si l'entité existe déjà
            DomainValidationError: Si les règles métier ne sont pas respectées
        """
        pass

    @abstractmethod
    def recuperer_entite(self, entite_id: int) -> VotreEntite:
        """
        Récupère une entité par son ID.

        Args:
            entite_id: L'identifiant de l'entité

        Returns:
            L'entité trouvée

        Raises:
            EntityNotFoundError: Si l'entité n'existe pas
        """
        pass

    @abstractmethod
    def lister_entites(
        self,
        offset: int = 0,
        limit: int = 20
    ) -> List[VotreEntite]:
        """
        Liste les entités avec pagination.

        Args:
            offset: Nombre d'entités à sauter
            limit: Nombre maximum d'entités à retourner

        Returns:
            Liste des entités
        """
        pass
```

### 2B. Port Secondaire (Repository)

**Localisation:** `src/ports/secondary/votre_repository.py`

```python
"""
Port secondaire: interface du repository pour [ENTITÉ].

Ce port définit le CONTRAT de persistance que le domaine attend.
Le domaine dépend de cette INTERFACE, pas de l'implémentation.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.votre_entite import VotreEntite


class VotreRepositoryPort(ABC):
    """
    Interface du repository pour [ENTITÉ].

    Cette interface définit les opérations de persistance nécessaires
    pour le domaine, sans se soucier de l'implémentation technique.
    """

    @abstractmethod
    def save(self, entite: VotreEntite) -> VotreEntite:
        """
        Sauvegarde une entité et retourne l'entité avec son ID.

        Args:
            entite: L'entité à sauvegarder

        Returns:
            L'entité sauvegardée avec son ID généré

        Raises:
            RepositoryError: Si la sauvegarde échoue
        """
        pass

    @abstractmethod
    def find_by_id(self, entite_id: int) -> Optional[VotreEntite]:
        """
        Récupère une entité par son ID.

        Args:
            entite_id: L'identifiant de l'entité

        Returns:
            L'entité trouvée ou None
        """
        pass

    @abstractmethod
    def find_all(
        self,
        offset: int = 0,
        limit: int = 20
    ) -> List[VotreEntite]:
        """
        Récupère toutes les entités avec pagination.

        Args:
            offset: Nombre d'entités à sauter
            limit: Nombre maximum d'entités à retourner

        Returns:
            Liste des entités
        """
        pass

    @abstractmethod
    def exists_by_field(self, field_value: str) -> bool:
        """
        Vérifie si une entité avec cette valeur existe.

        Args:
            field_value: La valeur à vérifier

        Returns:
            True si l'entité existe, False sinon
        """
        pass

    @abstractmethod
    def delete(self, entite_id: int) -> bool:
        """
        Supprime une entité.

        Args:
            entite_id: L'identifiant de l'entité à supprimer

        Returns:
            True si la suppression a réussi, False sinon
        """
        pass

    @abstractmethod
    def update(self, entite: VotreEntite) -> VotreEntite:
        """
        Met à jour une entité existante.

        Args:
            entite: L'entité avec les nouvelles valeurs

        Returns:
            L'entité mise à jour

        Raises:
            EntityNotFoundError: Si l'entité n'existe pas
        """
        pass
```

### ✅ Règles pour les Ports

1. **Toujours abstraits** (ABC)
2. **Type hints complets** sur tous les paramètres et retours
3. **Docstrings détaillées** avec Args, Returns, Raises
4. **Pas d'implémentation** (seulement `pass`)
5. **Imports minimaux** (seulement types et entités du domaine)

### ❌ Interdictions

```python
# ❌ INTERDIT: Implémentation dans un port
def save(self, entite: VotreEntite) -> VotreEntite:
    db.session.add(entite)  # NON
    return entite

# ❌ INTERDIT: Dépendances externes
from fastapi import Depends  # NON

# ❌ INTERDIT: Logique métier
def save(self, entite: VotreEntite) -> VotreEntite:
    if entite.prix < 0:  # NON - logique métier dans port
        raise ValueError("Prix invalide")
```

---

## Étape 3: Implémenter le Service Métier

### Localisation
```
src/domain/services/votre_service.py
```

### Template

```python
"""
Service métier pour [ENTITÉ].

Ce service contient la logique métier complexe et orchestre
les interactions entre entités et repositories.
"""
from datetime import date, datetime
from typing import Optional, List

from src.domain.entities.votre_entite import VotreEntite
from src.domain.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    DomainValidationError
)
from src.ports.primary.votre_use_cases import VotreUseCasesPort
from src.ports.secondary.votre_repository import VotreRepositoryPort


class VotreService(VotreUseCasesPort):
    """
    Service métier pour [ENTITÉ].

    Implémente VotreUseCasesPort (port primaire).
    Dépend de VotreRepositoryPort (port secondaire - interface uniquement).
    """

    def __init__(self, repository: VotreRepositoryPort) -> None:
        """
        Injection de dépendance via le constructeur.

        Args:
            repository: Interface du repository (pas l'implémentation concrète)
        """
        self._repository = repository

    def creer_entite(
        self,
        champ1: str,
        champ2: Optional[str],
        champ3: date
    ) -> VotreEntite:
        """
        Cas d'usage: Créer une nouvelle entité.

        Logique métier:
        1. Vérifier l'unicité (règle métier)
        2. Créer l'entité (validation automatique)
        3. Sauvegarder via le repository

        Args:
            champ1: Description
            champ2: Description optionnelle
            champ3: Description date

        Returns:
            L'entité créée avec son ID

        Raises:
            EntityAlreadyExistsError: Si l'entité existe déjà
            DomainValidationError: Si les règles métier ne sont pas respectées
        """
        # Règle métier: vérifier l'unicité
        if self._repository.exists_by_field(champ1):
            raise EntityAlreadyExistsError(f"Entité avec {champ1} existe déjà")

        # Créer l'entité (validation automatique dans __post_init__)
        entite = VotreEntite(
            id=None,
            champ1=champ1,
            champ2=champ2,
            champ3=champ3,
            date_creation=datetime.now()
        )

        # Règles métier supplémentaires (si nécessaire)
        if entite.methode_metier() == condition_invalide:
            raise DomainValidationError("Condition métier non respectée")

        # Persistance via le port secondaire
        entite_sauvegardee = self._repository.save(entite)

        return entite_sauvegardee

    def recuperer_entite(self, entite_id: int) -> VotreEntite:
        """
        Cas d'usage: Récupérer une entité par son ID.

        Args:
            entite_id: L'identifiant de l'entité

        Returns:
            L'entité trouvée

        Raises:
            EntityNotFoundError: Si l'entité n'existe pas
        """
        entite = self._repository.find_by_id(entite_id)

        if entite is None:
            raise EntityNotFoundError(f"Entité avec ID {entite_id} introuvable")

        return entite

    def lister_entites(
        self,
        offset: int = 0,
        limit: int = 20
    ) -> List[VotreEntite]:
        """
        Cas d'usage: Lister les entités avec pagination.

        Args:
            offset: Nombre d'entités à sauter
            limit: Nombre maximum d'entités à retourner

        Returns:
            Liste des entités
        """
        # Validation des paramètres
        if offset < 0:
            raise DomainValidationError("L'offset ne peut pas être négatif")

        if limit < 1 or limit > 100:
            raise DomainValidationError("Le limit doit être entre 1 et 100")

        return self._repository.find_all(offset=offset, limit=limit)
```

### ✅ CE QUI EST PERMIS

```python
# Orchestration de logique métier
def creer_avec_validation_complexe(self, ...):
    if condition_metier_1 and condition_metier_2:
        # Logique métier complexe
        pass

# Coordination entre entités
def transferer(self, source_id: int, dest_id: int):
    source = self._repository.find_by_id(source_id)
    dest = self._repository.find_by_id(dest_id)
    # Logique de transfert

# Appel à plusieurs repositories (si le service en a besoin)
def __init__(
    self,
    entite_repo: VotreRepositoryPort,
    autre_repo: AutreRepositoryPort
):
    self._entite_repo = entite_repo
    self._autre_repo = autre_repo
```

### ❌ CE QUI EST INTERDIT

```python
# ❌ INTERDIT: Accès direct à la base de données
def save_direct(self, entite):
    db.session.add(entite)  # NON - utiliser le repository

# ❌ INTERDIT: Code d'infrastructure
def send_notification(self):
    smtp.send_email(...)  # NON - déléguer à un service

# ❌ INTERDIT: Dépendre d'implémentations concrètes
def __init__(self, repository: SQLAlchemyRepository):  # NON
    # Doit être: repository: VotreRepositoryPort (interface)

# ❌ INTERDIT: Logique HTTP
def handle_request(self, request: Request):  # NON
    # Le service ne doit pas connaître HTTP
```

### 🧪 Tests du Service

```python
# tests/unit/domain/test_votre_service.py

from unittest.mock import Mock
import pytest

@pytest.fixture
def mock_repository():
    """Mock du repository pour tests unitaires."""
    return Mock(spec=VotreRepositoryPort)

@pytest.fixture
def service(mock_repository):
    """Service avec repository mocké."""
    return VotreService(mock_repository)


def test_creer_entite_success(service, mock_repository):
    """Créer une entité avec succès."""
    # Arrange
    mock_repository.exists_by_field.return_value = False
    mock_repository.save.return_value = VotreEntite(
        id=1, champ1="test", ...
    )

    # Act
    resultat = service.creer_entite(champ1="test", ...)

    # Assert
    assert resultat.id == 1
    mock_repository.exists_by_field.assert_called_once_with("test")
    mock_repository.save.assert_called_once()

def test_creer_entite_rejette_doublon(service, mock_repository):
    """Ne pas créer une entité en doublon."""
    # Arrange
    mock_repository.exists_by_field.return_value = True

    # Act & Assert
    with pytest.raises(EntityAlreadyExistsError):
        service.creer_entite(champ1="test", ...)

    # Vérifier que save n'a pas été appelé
    mock_repository.save.assert_not_called()
```

---

## Étape 4: Créer l'Adapter Repository

### Localisation
```
src/adapters/secondary/repositories/sqlalchemy_votre_repository.py
```

### Template

```python
"""
Adapter secondaire: implémentation SQLAlchemy du repository.

Implémente VotreRepositoryPort avec SQLAlchemy.
Compatible: SQLite, MySQL, PostgreSQL, Oracle, etc.
"""
from typing import Optional, List
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Date, DateTime, Float, Text

from src.domain.entities.votre_entite import VotreEntite
from src.ports.secondary.votre_repository import VotreRepositoryPort


# Modèle SQLAlchemy (ORM) - Couche technique
class Base(DeclarativeBase):
    pass


class VotreEntiteModel(Base):
    """
    Modèle de table SQL pour [ENTITÉ].

    IMPORTANT: Ce n'est PAS l'entité du domaine.
    C'est un modèle technique pour la persistance.
    """
    __tablename__ = "votre_table"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    champ1: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    champ2: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    champ3: Mapped[date] = mapped_column(Date, nullable=False)
    date_creation: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class SQLAlchemyVotreRepository(VotreRepositoryPort):
    """
    Implémentation SQLAlchemy du repository.

    Cette classe contient UNIQUEMENT du code technique d'accès aux données.
    Aucune logique métier ici.
    """

    def __init__(self, db_session: Session) -> None:
        """
        Injection de la session SQLAlchemy.

        Args:
            db_session: Session SQLAlchemy pour les opérations DB
        """
        self._session = db_session

    def save(self, entite: VotreEntite) -> VotreEntite:
        """
        Sauvegarde une entité dans la base de données.

        Conversion: Entité domaine → Modèle ORM → DB
        """
        # Conversion de l'entité domaine vers le modèle ORM
        model = VotreEntiteModel(
            champ1=entite.champ1,
            champ2=entite.champ2,
            champ3=entite.champ3,
            date_creation=entite.date_creation
        )

        # Opération technique de persistance
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)

        # Conversion du modèle ORM vers l'entité domaine
        return self._to_domain(model)

    def find_by_id(self, entite_id: int) -> Optional[VotreEntite]:
        """Récupère une entité par ID depuis la base."""
        model = self._session.query(VotreEntiteModel).filter(
            VotreEntiteModel.id == entite_id
        ).first()

        if model is None:
            return None

        return self._to_domain(model)

    def find_all(
        self,
        offset: int = 0,
        limit: int = 20
    ) -> List[VotreEntite]:
        """Récupère toutes les entités avec pagination."""
        models = self._session.query(VotreEntiteModel)\
            .offset(offset)\
            .limit(limit)\
            .all()

        return [self._to_domain(model) for model in models]

    def exists_by_field(self, field_value: str) -> bool:
        """Vérifie si une entité avec cette valeur existe."""
        count = self._session.query(VotreEntiteModel).filter(
            VotreEntiteModel.champ1 == field_value
        ).count()
        return count > 0

    def delete(self, entite_id: int) -> bool:
        """Supprime une entité de la base."""
        model = self._session.query(VotreEntiteModel).filter(
            VotreEntiteModel.id == entite_id
        ).first()

        if model is None:
            return False

        self._session.delete(model)
        self._session.commit()
        return True

    def update(self, entite: VotreEntite) -> VotreEntite:
        """Met à jour une entité existante."""
        model = self._session.query(VotreEntiteModel).filter(
            VotreEntiteModel.id == entite.id
        ).first()

        if model is None:
            from src.domain.exceptions import EntityNotFoundError
            raise EntityNotFoundError(f"Entité {entite.id} introuvable")

        # Mise à jour des champs
        model.champ1 = entite.champ1
        model.champ2 = entite.champ2
        model.champ3 = entite.champ3

        self._session.commit()
        self._session.refresh(model)

        return self._to_domain(model)

    def _to_domain(self, model: VotreEntiteModel) -> VotreEntite:
        """
        Convertit un modèle ORM en entité du domaine.

        IMPORTANT: Cette méthode isole le domaine de la couche technique.

        Args:
            model: Le modèle SQLAlchemy

        Returns:
            L'entité du domaine
        """
        return VotreEntite(
            id=model.id,
            champ1=model.champ1,
            champ2=model.champ2,
            champ3=model.champ3,
            date_creation=model.date_creation
        )
```

### ✅ CE QUI EST PERMIS

```python
# Requêtes SQL complexes
def find_by_criteria(self, criteria: dict):
    query = self._session.query(Model)
    for key, value in criteria.items():
        query = query.filter(getattr(Model, key) == value)
    return query.all()

# Joins si nécessaire
def find_with_relations(self, id: int):
    return self._session.query(Model)\
        .join(RelatedModel)\
        .filter(Model.id == id)\
        .first()

# Transactions
def save_multiple(self, entites: List[VotreEntite]):
    for entite in entites:
        model = self._to_model(entite)
        self._session.add(model)
    self._session.commit()
```

### ❌ CE QUI EST INTERDIT

```python
# ❌ INTERDIT: Logique métier
def save(self, entite: VotreEntite):
    if entite.prix < 0:  # NON - validation métier
        raise ValueError("Prix invalide")
    # La validation doit être dans l'entité ou le service

# ❌ INTERDIT: Exposer les modèles ORM
def find_by_id(self, id: int) -> VotreEntiteModel:  # NON
    return self._session.query(VotreEntiteModel).first()
    # Doit retourner: VotreEntite (pas le modèle)

# ❌ INTERDIT: Mélanger domaine et ORM
class VotreEntite(Base):  # NON
    # L'entité du domaine ne doit PAS hériter de Base
```

### 🧪 Tests d'Intégration du Repository

```python
# tests/integration/test_votre_repository.py

@pytest.fixture
def db_session():
    """Session de test avec rollback automatique."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def repository(db_session):
    """Repository avec session de test."""
    return SQLAlchemyVotreRepository(db_session)


def test_save_generates_id(repository):
    """Sauvegarder une entité doit générer un ID."""
    entite = VotreEntite(id=None, champ1="test", ...)

    saved = repository.save(entite)

    assert saved.id is not None
    assert saved.id > 0

def test_find_by_id_returns_entity(repository, db_session):
    """find_by_id doit retourner l'entité correcte."""
    # Créer directement en base
    model = VotreEntiteModel(champ1="test", ...)
    db_session.add(model)
    db_session.commit()

    # Tester
    found = repository.find_by_id(model.id)

    assert found is not None
    assert found.champ1 == "test"
```

---

## Étape 5: Créer les DTOs (Schemas)

### Localisation
```
src/adapters/primary/fastapi/schemas/votre_schemas.py
```

### Template

```python
"""
Schemas Pydantic pour [ENTITÉ].

Ces DTOs (Data Transfer Objects) définissent la structure
des requêtes/réponses HTTP. Ils appartiennent à la couche adapter.
"""
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional


class CreateVotreEntiteRequest(BaseModel):
    """
    DTO pour la requête de création.

    FastAPI utilise ce schema pour:
    - Valider les données d'entrée HTTP
    - Générer la documentation OpenAPI
    """
    champ1: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Description du champ1"
    )
    champ2: Optional[str] = Field(
        None,
        description="Description optionnelle du champ2"
    )
    champ3: date = Field(
        ...,
        description="Date du champ3"
    )

    @field_validator('champ1')
    @classmethod
    def validate_champ1(cls, v: str) -> str:
        """Validation supplémentaire HTTP (pas métier)."""
        if v and not v[0].isupper():
            raise ValueError("Le champ1 doit commencer par une majuscule")
        return v


class UpdateVotreEntiteRequest(BaseModel):
    """
    DTO pour la requête de mise à jour.

    Tous les champs sont optionnels (PATCH sémantique).
    """
    champ1: Optional[str] = Field(None, min_length=1, max_length=255)
    champ2: Optional[str] = None
    champ3: Optional[date] = None


class VotreEntiteResponse(BaseModel):
    """
    DTO pour la réponse contenant une entité.

    Ce schema définit la structure JSON retournée par l'API.
    """
    id: int
    champ1: str
    champ2: Optional[str]
    champ3: date
    date_creation: datetime

    # Champs calculés (depuis méthodes métier)
    champ_calcule: bool

    class Config:
        """Configuration Pydantic."""
        from_attributes = True  # Permet conversion depuis objets Python
```

### ✅ CE QUI EST PERMIS

```python
# Validations de format HTTP
@field_validator('email')
@classmethod
def validate_email(cls, v: str) -> str:
    if '@' not in v:
        raise ValueError("Format email invalide")
    return v

# Contraintes Pydantic
prix: float = Field(..., gt=0, description="Prix positif")
age: int = Field(..., ge=18, le=120)

# Alias pour mapping JSON
nom_client: str = Field(..., alias="nomClient")
```

### ❌ CE QUI EST INTERDIT

```python
# ❌ INTERDIT: Logique métier
@field_validator('budget')
@classmethod
def validate_budget(cls, v: float, info) -> float:
    if v > info.data['limite_entreprise']:  # NON - règle métier
        raise ValueError("Budget trop élevé")
    # La validation métier doit être dans le domaine

# ❌ INTERDIT: Accès base de données
def check_unique(self):
    if db.query(...).exists():  # NON
        raise ValueError("Existe déjà")

# ❌ INTERDIT: Imports du domaine dans les validators
from src.domain.entities.votre_entite import VotreEntite  # NON (si utilisé dans validators)
```

---

## Étape 6: Implémenter le Router FastAPI

### Localisation
```
src/adapters/primary/fastapi/routers/votre_router.py
```

### Template

```python
"""
Adapter primaire: Router FastAPI pour [ENTITÉ].

Expose les endpoints HTTP et fait le pont entre HTTP et le domaine.
Dépend du PORT PRIMAIRE (interface), pas directement du service.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated, List
import logging

from src.adapters.primary.fastapi.schemas.votre_schemas import (
    CreateVotreEntiteRequest,
    UpdateVotreEntiteRequest,
    VotreEntiteResponse
)
from src.ports.primary.votre_use_cases import VotreUseCasesPort
from src.domain.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    DomainValidationError
)

# Logger pour ce module
logger = logging.getLogger(__name__)

# Création du router FastAPI
router = APIRouter(
    prefix="/api/votre-entites",
    tags=["Votre Entités"]
)


def get_votre_use_cases() -> VotreUseCasesPort:
    """
    Dépendance FastAPI pour injecter les cas d'usage.

    Cette fonction est appelée par FastAPI pour obtenir le service.
    C'est ici que l'injection de dépendances se produit.
    """
    from src.di_container import get_votre_service
    return get_votre_service()


# Type annotation pour l'injection de dépendances
VotreUseCasesDep = Annotated[VotreUseCasesPort, Depends(get_votre_use_cases)]


@router.post(
    "",
    response_model=VotreEntiteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une nouvelle entité",
    description="Crée une nouvelle entité avec toutes les informations requises"
)
def create_entite(
    request: CreateVotreEntiteRequest,
    use_cases: VotreUseCasesDep
) -> VotreEntiteResponse:
    """
    Endpoint POST /api/votre-entites

    Rôle de cet adapter:
    1. Recevoir la requête HTTP (FastAPI le fait automatiquement)
    2. Valider les données (Pydantic le fait automatiquement)
    3. Appeler le cas d'usage du domaine
    4. Convertir la réponse du domaine en DTO HTTP
    5. Gérer les erreurs et les convertir en codes HTTP appropriés

    Args:
        request: DTO validé par Pydantic
        use_cases: Service métier injecté (via le port primaire)

    Returns:
        DTO de réponse avec l'entité créée

    Raises:
        HTTPException: En cas d'erreur métier ou technique
    """
    try:
        # Appel du cas d'usage du domaine (via le port primaire)
        entite = use_cases.creer_entite(
            champ1=request.champ1,
            champ2=request.champ2,
            champ3=request.champ3
        )

        # Conversion de l'entité domaine vers le DTO de réponse
        return VotreEntiteResponse(
            id=entite.id,
            champ1=entite.champ1,
            champ2=entite.champ2,
            champ3=entite.champ3,
            date_creation=entite.date_creation,
            champ_calcule=entite.methode_metier()  # Appel méthode métier
        )

    except EntityAlreadyExistsError as e:
        # Conflit - l'entité existe déjà
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    except DomainValidationError as e:
        # Erreur de validation métier
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # Erreur technique inattendue
        logger.error(
            "Unexpected error creating entite",
            exc_info=True,
            extra={"champ1": request.champ1}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne s'est produite"  # Message générique
        )


@router.get(
    "/{entite_id}",
    response_model=VotreEntiteResponse,
    summary="Récupérer une entité",
    description="Récupère les détails d'une entité par son ID"
)
def get_entite(
    entite_id: int,
    use_cases: VotreUseCasesDep
) -> VotreEntiteResponse:
    """
    Endpoint GET /api/votre-entites/{entite_id}

    Args:
        entite_id: ID de l'entité (extrait de l'URL par FastAPI)
        use_cases: Service métier injecté

    Returns:
        DTO de réponse avec l'entité

    Raises:
        HTTPException: Si l'entité n'existe pas
    """
    try:
        entite = use_cases.recuperer_entite(entite_id)

        return VotreEntiteResponse(
            id=entite.id,
            champ1=entite.champ1,
            champ2=entite.champ2,
            champ3=entite.champ3,
            date_creation=entite.date_creation,
            champ_calcule=entite.methode_metier()
        )

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"Unexpected error getting entite", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne s'est produite"
        )


@router.put(
    "/{entite_id}",
    response_model=VotreEntiteResponse,
    summary="Mettre à jour une entité"
)
def update_entite(
    entite_id: int,
    request: UpdateVotreEntiteRequest,
    use_cases: VotreUseCasesDep
) -> VotreEntiteResponse:
    """
    Endpoint PUT /api/votre-entites/{entite_id}

    Met à jour une entité existante (PATCH sémantique - champs optionnels).
    """
    try:
        # Récupérer l'entité existante
        entite = use_cases.recuperer_entite(entite_id)

        # Appliquer les modifications (seulement les champs fournis)
        if request.champ1 is not None:
            entite.champ1 = request.champ1
        if request.champ2 is not None:
            entite.champ2 = request.champ2
        if request.champ3 is not None:
            entite.champ3 = request.champ3

        # Sauvegarder (via un use case update)
        entite_mise_a_jour = use_cases.mettre_a_jour_entite(entite)

        return VotreEntiteResponse(
            id=entite_mise_a_jour.id,
            champ1=entite_mise_a_jour.champ1,
            champ2=entite_mise_a_jour.champ2,
            champ3=entite_mise_a_jour.champ3,
            date_creation=entite_mise_a_jour.date_creation,
            champ_calcule=entite_mise_a_jour.methode_metier()
        )

    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except DomainValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error("Unexpected error updating entite", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne")


@router.delete(
    "/{entite_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une entité"
)
def delete_entite(
    entite_id: int,
    use_cases: VotreUseCasesDep
) -> None:
    """
    Endpoint DELETE /api/votre-entites/{entite_id}

    Supprime une entité (retourne 204 No Content si succès).
    """
    try:
        success = use_cases.supprimer_entite(entite_id)

        if not success:
            raise EntityNotFoundError(entite_id)

    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        logger.error("Unexpected error deleting entite", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne")


@router.get(
    "",
    response_model=List[VotreEntiteResponse],
    summary="Lister les entités"
)
def list_entites(
    offset: int = Query(0, ge=0, description="Nombre d'entités à sauter"),
    limit: int = Query(20, ge=1, le=100, description="Nombre max d'entités"),
    use_cases: VotreUseCasesDep
) -> List[VotreEntiteResponse]:
    """
    Endpoint GET /api/votre-entites?offset=0&limit=20

    Liste les entités avec pagination.
    """
    try:
        entites = use_cases.lister_entites(offset=offset, limit=limit)

        return [
            VotreEntiteResponse(
                id=entite.id,
                champ1=entite.champ1,
                champ2=entite.champ2,
                champ3=entite.champ3,
                date_creation=entite.date_creation,
                champ_calcule=entite.methode_metier()
            )
            for entite in entites
        ]

    except DomainValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error("Unexpected error listing entites", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne")
```

### ✅ CE QUI EST PERMIS

```python
# Conversion DTO ↔ Entité
entite = use_cases.creer(...)
return DTOResponse(**entite.__dict__)

# Gestion d'erreurs par type
except EntityNotFoundError:
    raise HTTPException(status_code=404)

# Logging avec contexte
logger.info("Entity created", extra={"id": entite.id})

# Query parameters avec validation
def list(skip: int = Query(0, ge=0), limit: int = Query(10, le=100)):
    pass
```

### ❌ CE QUI EST INTERDIT

```python
# ❌ INTERDIT: Logique métier dans le router
@router.post("/")
def create(request: DTO):
    if request.prix < 0:  # NON - logique métier
        raise HTTPException(400)
    # Doit être dans le service ou l'entité

# ❌ INTERDIT: Accès direct au repository
def get(id: int, repo: Repository = Depends()):  # NON
    return repo.find(id)
    # Doit passer par le service

# ❌ INTERDIT: Exposer les détails techniques
except Exception as e:
    raise HTTPException(500, detail=str(e))  # NON - stack trace exposée
```

### 🧪 Tests E2E du Router

```python
# tests/e2e/test_votre_api.py

from fastapi.testclient import TestClient

@pytest.fixture
def client():
    from src.main import app
    return TestClient(app)


def test_create_entite_success(client):
    """Créer une entité via l'API doit retourner 201."""
    response = client.post("/api/votre-entites", json={
        "champ1": "test",
        "champ2": "valeur",
        "champ3": "2025-01-01"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["champ1"] == "test"
    assert data["id"] is not None

def test_create_duplicate_returns_409(client):
    """Créer un doublon doit retourner 409 Conflict."""
    # Créer une première fois
    client.post("/api/votre-entites", json={"champ1": "unique", ...})

    # Tenter de recréer
    response = client.post("/api/votre-entites", json={"champ1": "unique", ...})

    assert response.status_code == 409
    assert "existe déjà" in response.json()["detail"]
```

---

## Étape 7: Tests (TDD)

### Approche TDD Recommandée

Pour chaque fonctionnalité, suivre le cycle **RED → GREEN → REFACTOR**:

```
1. RED:    Écrire le test qui échoue
2. GREEN:  Écrire le code minimum pour passer le test
3. REFACTOR: Améliorer le code (qualité, performance)
```

### Structure des Tests

```
tests/
├── unit/                    # Tests unitaires (pas de DB, pas de HTTP)
│   ├── domain/
│   │   ├── test_votre_entite.py          # Tests de l'entité
│   │   └── test_votre_service.py         # Tests du service (avec mocks)
│   └── adapters/
│       └── test_votre_schemas.py         # Tests des DTOs Pydantic
│
├── integration/             # Tests d'intégration (avec DB réelle)
│   └── test_votre_repository.py          # Tests du repository
│
└── e2e/                     # Tests end-to-end (API complète)
    └── test_votre_api.py                 # Tests des endpoints
```

### Ordre d'Implémentation TDD

#### 1. Tests de l'Entité (Unit)
```python
# Écrire AVANT de coder l'entité
def test_entite_valide_les_regles_metier():
    with pytest.raises(ValueError):
        VotreEntite(champ_invalide=...)
```

#### 2. Tests du Service (Unit avec Mocks)
```python
# Écrire AVANT de coder le service
def test_service_appelle_repository(mock_repository):
    service = VotreService(mock_repository)
    service.creer(...)
    mock_repository.save.assert_called_once()
```

#### 3. Tests du Repository (Integration)
```python
# Écrire AVANT de coder le repository
def test_repository_persiste_entite(db_session):
    repo = SQLAlchemyRepository(db_session)
    entite = repo.save(VotreEntite(...))
    assert entite.id is not None
```

#### 4. Tests E2E (End-to-End)
```python
# Écrire AVANT de coder le router
def test_api_cree_entite(client):
    response = client.post("/api/entites", json={...})
    assert response.status_code == 201
```

### Fixtures Essentielles

```python
# tests/conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock

@pytest.fixture(scope="session")
def test_engine():
    """Engine SQLite en mémoire."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(test_engine):
    """Session DB avec rollback automatique."""
    connection = test_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def mock_repository():
    """Mock du repository pour tests unitaires."""
    return Mock(spec=VotreRepositoryPort)

@pytest.fixture
def service(mock_repository):
    """Service avec repository mocké."""
    return VotreService(mock_repository)
```

### Commandes de Test

```bash
# Lancer tous les tests
uv run pytest tests/ -v

# Tests par catégorie
uv run pytest tests/unit/ -v           # Unitaires uniquement
uv run pytest tests/integration/ -v    # Intégration uniquement
uv run pytest tests/e2e/ -v            # E2E uniquement

# Avec couverture
uv run pytest --cov=src --cov-report=html

# Mode TDD (watch)
uv run pytest-watch  # Relance tests à chaque modification
```

---

## Règles Strictes par Couche

### 🔷 DOMAINE (Entités + Services)

**✅ AUTORISÉ:**
- Python standard library uniquement
- Imports entre entités du domaine
- Imports des ports (interfaces)
- Imports des exceptions du domaine
- dataclasses, typing, datetime, decimal, enum

**❌ INTERDIT:**
- FastAPI, Pydantic
- SQLAlchemy, pymysql
- Requests, httpx
- Tout framework/library externe

**Règle d'or:** Le domaine ne dépend de RIEN

---

### 🔌 PORTS (Interfaces)

**✅ AUTORISÉ:**
- ABC (abstract base class)
- Imports d'entités du domaine
- Type hints (typing)
- Docstrings complètes

**❌ INTERDIT:**
- Implémentations concrètes
- Code d'infrastructure
- Logique métier

**Règle d'or:** Définir uniquement le CONTRAT

---

### 🔧 ADAPTERS

**✅ AUTORISÉ:**
- Frameworks (FastAPI, SQLAlchemy)
- Imports des ports (dépendre des interfaces)
- Conversion DTO ↔ Entité
- Code technique/infrastructure

**❌ INTERDIT:**
- Logique métier
- Dépendre d'autres adapters
- Court-circuiter les ports

**Règle d'or:** Dépendre des INTERFACES, pas des implémentations

---

## Anti-Patterns à Éviter

### ❌ Anti-Pattern #1: Logique Métier dans le Router

```python
# ❌ MAUVAIS
@router.post("/entites")
def create(request: DTO):
    if request.budget > 100000:  # Logique métier dans le router !
        raise HTTPException(400, "Budget trop élevé")
    # ...

# ✅ BON
@router.post("/entites")
def create(request: DTO, service: ServicePort):
    entite = service.creer(...)  # La validation est dans le service
```

### ❌ Anti-Pattern #2: Entité = Modèle ORM

```python
# ❌ MAUVAIS
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Project(Base):  # L'entité hérite de Base !
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    # Mélange domaine et infrastructure

# ✅ BON
# Domaine: src/domain/entities/project.py
@dataclass
class Project:
    id: Optional[int]
    # ...

# Adapter: src/adapters/secondary/repositories/...
class ProjectModel(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
```

### ❌ Anti-Pattern #3: Service Dépend d'une Implémentation

```python
# ❌ MAUVAIS
from src.adapters.secondary.repositories.sqlalchemy_repo import SQLAlchemyRepo

class ProjectService:
    def __init__(self, repo: SQLAlchemyRepo):  # Dépendance concrète !
        self._repo = repo

# ✅ BON
from src.ports.secondary.project_repository import ProjectRepositoryPort

class ProjectService:
    def __init__(self, repo: ProjectRepositoryPort):  # Dépendance abstraite
        self._repo = repo
```

### ❌ Anti-Pattern #4: Pas de Conversion DTO → Entité

```python
# ❌ MAUVAIS
@router.post("/projects")
def create(request: CreateProjectRequest, service: ServicePort):
    project = service.create_project(request)  # Passer le DTO directement !

# ✅ BON
@router.post("/projects")
def create(request: CreateProjectRequest, service: ServicePort):
    # Convertir DTO → paramètres primitifs
    project = service.create_project(
        name=request.name,
        description=request.description,
        # ...
    )
```

### ❌ Anti-Pattern #5: Validation Métier Dupliquée

```python
# ❌ MAUVAIS
# Dans le DTO
class CreateProjectRequest(BaseModel):
    budget: float

    @field_validator('budget')
    def validate_budget(cls, v):
        if v <= 0:  # Validation métier dans le DTO !
            raise ValueError("Budget positif")

# Dans l'entité
@dataclass
class Project:
    budget: float

    def _validate(self):
        if self.budget <= 0:  # Duplication !
            raise ValueError("Budget positif")

# ✅ BON
# DTO: validation FORMAT uniquement
class CreateProjectRequest(BaseModel):
    budget: float = Field(..., gt=0)  # Simple contrainte format

# Entité: validation MÉTIER
@dataclass
class Project:
    budget: float

    def _validate(self):
        if self.budget <= 0:
            raise ValueError("Le budget doit être positif")
        if self.budget > self.limite_entreprise():
            raise ValueError("Budget dépasse la limite entreprise")
```

---

## Exemple Complet: Feature "Tasks"

Voici un exemple complet d'implémentation d'une nouvelle fonctionnalité "Tasks" (tâches liées aux projets).

### 1. Entité Task

```python
# src/domain/entities/task.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

class TaskStatus(Enum):
    """Statuts possibles d'une tâche."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

@dataclass
class Task:
    """
    Entité Task du domaine.

    Règles métier:
    - Le titre ne peut pas être vide
    - La date limite doit être dans le futur (si définie)
    - Une tâche DONE ne peut pas être réouverte
    """
    id: Optional[int]
    project_id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    due_date: Optional[datetime]
    created_at: datetime

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.title or self.title.strip() == "":
            raise ValueError("Le titre de la tâche ne peut pas être vide")

        if self.due_date and self.due_date < datetime.now():
            raise ValueError("La date limite doit être dans le futur")

    def is_overdue(self) -> bool:
        """Vérifie si la tâche est en retard."""
        if self.status == TaskStatus.DONE:
            return False
        if not self.due_date:
            return False
        return datetime.now() > self.due_date

    def mark_as_done(self) -> None:
        """Marque la tâche comme terminée (logique métier)."""
        self.status = TaskStatus.DONE
```

### 2. Ports

```python
# src/ports/primary/task_use_cases.py

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List
from src.domain.entities.task import Task, TaskStatus

class TaskUseCasesPort(ABC):
    @abstractmethod
    def create_task(
        self,
        project_id: int,
        title: str,
        description: Optional[str],
        due_date: Optional[datetime]
    ) -> Task:
        pass

    @abstractmethod
    def get_task(self, task_id: int) -> Task:
        pass

    @abstractmethod
    def list_tasks_by_project(self, project_id: int) -> List[Task]:
        pass

    @abstractmethod
    def mark_task_done(self, task_id: int) -> Task:
        pass


# src/ports/secondary/task_repository.py

from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.task import Task

class TaskRepositoryPort(ABC):
    @abstractmethod
    def save(self, task: Task) -> Task:
        pass

    @abstractmethod
    def find_by_id(self, task_id: int) -> Optional[Task]:
        pass

    @abstractmethod
    def find_by_project_id(self, project_id: int) -> List[Task]:
        pass

    @abstractmethod
    def update(self, task: Task) -> Task:
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        pass
```

### 3. Service

```python
# src/domain/services/task_service.py

from datetime import datetime
from typing import Optional, List

from src.domain.entities.task import Task, TaskStatus
from src.domain.exceptions import EntityNotFoundError, DomainValidationError
from src.ports.primary.task_use_cases import TaskUseCasesPort
from src.ports.secondary.task_repository import TaskRepositoryPort

class TaskService(TaskUseCasesPort):
    def __init__(self, task_repository: TaskRepositoryPort) -> None:
        self._repository = task_repository

    def create_task(
        self,
        project_id: int,
        title: str,
        description: Optional[str],
        due_date: Optional[datetime]
    ) -> Task:
        # Créer l'entité (validation automatique)
        task = Task(
            id=None,
            project_id=project_id,
            title=title,
            description=description,
            status=TaskStatus.TODO,
            due_date=due_date,
            created_at=datetime.now()
        )

        # Sauvegarder
        return self._repository.save(task)

    def get_task(self, task_id: int) -> Task:
        task = self._repository.find_by_id(task_id)
        if task is None:
            raise EntityNotFoundError(f"Task {task_id} introuvable")
        return task

    def list_tasks_by_project(self, project_id: int) -> List[Task]:
        return self._repository.find_by_project_id(project_id)

    def mark_task_done(self, task_id: int) -> Task:
        task = self.get_task(task_id)

        # Logique métier
        if task.status == TaskStatus.DONE:
            raise DomainValidationError("La tâche est déjà terminée")

        task.mark_as_done()
        return self._repository.update(task)
```

### 4. Repository (Adapter Secondaire)

```python
# src/adapters/secondary/repositories/sqlalchemy_task_repository.py

from typing import Optional, List
from sqlalchemy.orm import Session, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from datetime import datetime

from src.domain.entities.task import Task, TaskStatus
from src.ports.secondary.task_repository import TaskRepositoryPort
from src.adapters.secondary.repositories.sqlalchemy_project_repository import Base

class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(SQLEnum(TaskStatus), nullable=False)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

class SQLAlchemyTaskRepository(TaskRepositoryPort):
    def __init__(self, db_session: Session) -> None:
        self._session = db_session

    def save(self, task: Task) -> Task:
        model = TaskModel(
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            due_date=task.due_date,
            created_at=task.created_at
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_domain(model)

    def find_by_id(self, task_id: int) -> Optional[Task]:
        model = self._session.query(TaskModel).filter(
            TaskModel.id == task_id
        ).first()
        return self._to_domain(model) if model else None

    def find_by_project_id(self, project_id: int) -> List[Task]:
        models = self._session.query(TaskModel).filter(
            TaskModel.project_id == project_id
        ).all()
        return [self._to_domain(m) for m in models]

    def update(self, task: Task) -> Task:
        model = self._session.query(TaskModel).filter(
            TaskModel.id == task.id
        ).first()

        if model is None:
            from src.domain.exceptions import EntityNotFoundError
            raise EntityNotFoundError(f"Task {task.id} introuvable")

        model.title = task.title
        model.description = task.description
        model.status = task.status.value
        model.due_date = task.due_date

        self._session.commit()
        self._session.refresh(model)
        return self._to_domain(model)

    def delete(self, task_id: int) -> bool:
        model = self._session.query(TaskModel).filter(
            TaskModel.id == task_id
        ).first()

        if model is None:
            return False

        self._session.delete(model)
        self._session.commit()
        return True

    def _to_domain(self, model: TaskModel) -> Task:
        return Task(
            id=model.id,
            project_id=model.project_id,
            title=model.title,
            description=model.description,
            status=TaskStatus(model.status),
            due_date=model.due_date,
            created_at=model.created_at
        )
```

### 5. DTOs (Adapter Primaire)

```python
# src/adapters/primary/fastapi/schemas/task_schemas.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CreateTaskRequest(BaseModel):
    project_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    status: str
    due_date: Optional[datetime]
    created_at: datetime
    is_overdue: bool

    class Config:
        from_attributes = True
```

### 6. Router (Adapter Primaire)

```python
# src/adapters/primary/fastapi/routers/tasks_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
import logging

from src.adapters.primary.fastapi.schemas.task_schemas import (
    CreateTaskRequest,
    TaskResponse
)
from src.ports.primary.task_use_cases import TaskUseCasesPort
from src.domain.exceptions import EntityNotFoundError, DomainValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

def get_task_use_cases() -> TaskUseCasesPort:
    from src.di_container import get_task_service
    return get_task_service()

TaskUseCasesDep = Annotated[TaskUseCasesPort, Depends(get_task_use_cases)]

@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    request: CreateTaskRequest,
    use_cases: TaskUseCasesDep
) -> TaskResponse:
    try:
        task = use_cases.create_task(
            project_id=request.project_id,
            title=request.title,
            description=request.description,
            due_date=request.due_date
        )

        return TaskResponse(
            id=task.id,
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            due_date=task.due_date,
            created_at=task.created_at,
            is_overdue=task.is_overdue()
        )

    except DomainValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error creating task", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne")

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, use_cases: TaskUseCasesDep) -> TaskResponse:
    try:
        task = use_cases.get_task(task_id)
        return TaskResponse(
            id=task.id,
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            due_date=task.due_date,
            created_at=task.created_at,
            is_overdue=task.is_overdue()
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Error getting task", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne")

@router.get("/project/{project_id}", response_model=List[TaskResponse])
def list_tasks_by_project(
    project_id: int,
    use_cases: TaskUseCasesDep
) -> List[TaskResponse]:
    try:
        tasks = use_cases.list_tasks_by_project(project_id)
        return [
            TaskResponse(
                id=t.id,
                project_id=t.project_id,
                title=t.title,
                description=t.description,
                status=t.status.value,
                due_date=t.due_date,
                created_at=t.created_at,
                is_overdue=t.is_overdue()
            )
            for t in tasks
        ]
    except Exception as e:
        logger.error("Error listing tasks", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne")

@router.post("/{task_id}/done", response_model=TaskResponse)
def mark_task_done(task_id: int, use_cases: TaskUseCasesDep) -> TaskResponse:
    try:
        task = use_cases.mark_task_done(task_id)
        return TaskResponse(
            id=task.id,
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            due_date=task.due_date,
            created_at=task.created_at,
            is_overdue=task.is_overdue()
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error marking task done", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne")
```

### 7. Enregistrer le Router

```python
# src/main.py

from src.adapters.primary.fastapi.routers import projects_router, tasks_router

app.include_router(projects_router.router)
app.include_router(tasks_router.router)  # Ajouter le nouveau router
```

### 8. DI Container

```python
# src/di_container.py

def get_task_repository() -> SQLAlchemyTaskRepository:
    """Factory pour créer le repository de tâches."""
    db_session = get_db_session()
    return SQLAlchemyTaskRepository(db_session)

def get_task_service() -> TaskUseCasesPort:
    """Factory pour créer le service de tâches."""
    repository = get_task_repository()
    return TaskService(task_repository=repository)
```

---

## Checklist de Validation

Avant de soumettre votre feature:

### Code
- [ ] L'entité du domaine n'a aucune dépendance externe
- [ ] Le service implémente le port primaire (interface)
- [ ] Le service dépend du port secondaire (pas de l'implémentation)
- [ ] Le repository implémente le port secondaire
- [ ] Conversion DTO ↔ Entité dans le router
- [ ] Pas de logique métier dans le router
- [ ] Exceptions métier personnalisées utilisées
- [ ] Logging avec contexte (pas de print)
- [ ] Type hints complets partout
- [ ] Docstrings sur toutes les classes et méthodes publiques

### Tests
- [ ] Tests unitaires de l'entité (100% couverture)
- [ ] Tests unitaires du service (avec mocks)
- [ ] Tests d'intégration du repository (avec DB)
- [ ] Tests E2E des endpoints (avec TestClient)
- [ ] Tous les tests passent: `uv run pytest tests/ -v`
- [ ] Type checking passe: `uv run mypy src/ --strict`
- [ ] Couverture >= 80%: `uv run pytest --cov=src`

### Architecture
- [ ] Domaine isolé (vérifier avec grep, aucun import externe)
- [ ] Inversion de dépendances respectée
- [ ] Ports clairement définis
- [ ] Adapters interchangeables
- [ ] Pas d'anti-patterns détectés

### Documentation
- [ ] README.md mis à jour avec nouveau endpoint
- [ ] CHANGELOG.md mis à jour
- [ ] Docstrings complètes
- [ ] Swagger UI génère correctement la doc

### Performance
- [ ] Requêtes SQL optimisées (pas de N+1)
- [ ] Pagination implémentée pour les listes
- [ ] Indexes DB créés si nécessaire

---

## Commandes de Vérification

```bash
# Vérifier que le domaine est pur
grep -r "from fastapi\|from sqlalchemy\|from pydantic" src/domain/
# Résultat attendu: aucune ligne

# Vérifier les imports circulaires
uv run python -c "from src.domain.services.votre_service import VotreService; print('OK')"

# Vérifier le type checking
uv run mypy src/ --strict

# Lancer tous les tests
uv run pytest tests/ -v --cov=src --cov-report=term-missing

# Vérifier le linting
uv run ruff check src/

# Vérifier le formatage
uv run black src/ --check
```

---

## Ressources

### Documentation Interne
- `README.md` - Vue d'ensemble du projet
- `TESTING.md` - Guide des tests
- `CONTRIBUTING.md` - Guidelines de contribution
- `documents/ARCHITECTURE_COMPLIANCE.md` - Conformité architecture

### Références Externes
- [Architecture Hexagonale](https://alistair.cockburn.us/hexagonal-architecture/) - Article original
- [FastAPI](https://fastapi.tiangolo.com/) - Documentation officielle
- [SQLAlchemy](https://docs.sqlalchemy.org/) - Documentation ORM
- [Pydantic](https://docs.pydantic.dev/) - Validation de données

---

## Support

**Questions ?** Consultez les mainteneurs du projet ou créez une issue sur le repository.

**Améliorations ?** Ce guide évolue avec le projet. N'hésitez pas à proposer des améliorations !

---

**Version:** 1.0
**Dernière mise à jour:** 2025-11-07
**Mainteneurs:** Équipe Architecture
