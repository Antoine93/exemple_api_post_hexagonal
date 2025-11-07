"""
Service du domaine: contient la LOGIQUE MÉTIER.
Orchestre les entités et utilise les ports secondaires.
NE DÉPEND PAS des adapters, uniquement des INTERFACES (ports).
"""
from datetime import date
from typing import Optional
from src.domain.entities.project import Project
from src.domain.exceptions import ProjectAlreadyExistsError, ProjectNotFoundError
from src.ports.primary.project_use_cases import ProjectUseCasesPort
from src.ports.secondary.project_repository import ProjectRepositoryPort


class ProjectService(ProjectUseCasesPort):
    """
    Service métier pour la gestion des projets.

    Implémente l'interface ProjectUseCasesPort (port primaire) qui définit
    le contrat des cas d'usage exposés par le domaine.

    Ce service contient la logique métier complexe qui va au-delà
    des simples règles de validation d'une entité.

    Architecture:
    - Hérite de ProjectUseCasesPort (respect du contrat d'interface)
    - Dépend uniquement de ProjectRepositoryPort (inversion de dépendance)
    - Aucune dépendance vers les couches externes (adapters)
    """

    def __init__(self, project_repository: ProjectRepositoryPort) -> None:
        """
        Injection de dépendance via le constructeur.

        Args:
            project_repository: Une INTERFACE (port secondaire), pas une implémentation concrète.
        """
        self._repository = project_repository

    def create_project(
        self,
        name: str,
        description: str,
        start_date: date,
        end_date: date,
        budget: float,
        comment: Optional[str],
        manager_id: int
    ) -> Project:
        """
        Cas d'usage: Créer un nouveau projet.

        Logique métier:
        1. Vérifier que le nom n'existe pas déjà
        2. Créer l'entité (validation automatique via __post_init__)
        3. Sauvegarder via le port secondaire

        Args:
            name, description, etc.: Données du projet

        Returns:
            Le projet créé avec son ID

        Raises:
            ValueError: Si les règles métier ne sont pas respectées
        """
        # Règle métier: un projet avec ce nom ne doit pas déjà exister
        if self._repository.exists_by_name(name):
            raise ProjectAlreadyExistsError(name)

        # Création de l'entité (validation automatique dans __post_init__)
        project = Project(
            id=None,  # Sera généré par la base de données
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            comment=comment,
            manager_id=manager_id
        )

        # Persistance via le port secondaire
        saved_project = self._repository.save(project)

        return saved_project

    def get_project(self, project_id: int) -> Project:
        """
        Cas d'usage: Récupérer un projet par son ID.

        Args:
            project_id: L'identifiant du projet

        Returns:
            Le projet trouvé

        Raises:
            ValueError: Si le projet n'existe pas
        """
        project = self._repository.find_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError(project_id)

        return project

    def update_project(
        self,
        project_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        budget: Optional[float] = None,
        comment: Optional[str] = None,
        manager_id: Optional[int] = None
    ) -> Project:
        """
        Cas d'usage: Mettre à jour un projet existant.

        Logique métier:
        1. Vérifier que le projet existe
        2. Si le nom change, vérifier qu'il n'existe pas déjà
        3. Mettre à jour uniquement les champs fournis
        4. Recréer l'entité avec validation
        5. Sauvegarder via le port secondaire

        Args:
            project_id: L'identifiant du projet à modifier
            name: Nouveau nom (optionnel)
            description: Nouvelle description (optionnel)
            start_date: Nouvelle date de début (optionnel)
            end_date: Nouvelle date de fin (optionnel)
            budget: Nouveau budget (optionnel)
            comment: Nouveau commentaire (optionnel)
            manager_id: Nouvel ID du manager (optionnel)

        Returns:
            Le projet modifié

        Raises:
            ProjectNotFoundError: Si le projet n'existe pas
            ProjectAlreadyExistsError: Si le nouveau nom existe déjà
            ValueError: Si les règles métier ne sont pas respectées
        """
        # 1. Récupérer le projet existant
        existing_project = self._repository.find_by_id(project_id)
        if existing_project is None:
            raise ProjectNotFoundError(project_id)

        # 2. Si le nom change, vérifier qu'il n'existe pas déjà
        if name is not None and name != existing_project.name:
            if self._repository.exists_by_name(name):
                raise ProjectAlreadyExistsError(name)

        # 3. Créer le projet avec les valeurs mises à jour
        updated_project = Project(
            id=project_id,
            name=name if name is not None else existing_project.name,
            description=description if description is not None else existing_project.description,
            start_date=start_date if start_date is not None else existing_project.start_date,
            end_date=end_date if end_date is not None else existing_project.end_date,
            budget=budget if budget is not None else existing_project.budget,
            comment=comment if comment is not None else existing_project.comment,
            manager_id=manager_id if manager_id is not None else existing_project.manager_id
        )

        # 4. Sauvegarder via le port secondaire
        saved_project = self._repository.update(updated_project)

        return saved_project

    def delete_project(self, project_id: int) -> bool:
        """
        Cas d'usage: Supprimer un projet.

        Args:
            project_id: L'identifiant du projet à supprimer

        Returns:
            True si le projet a été supprimé

        Raises:
            ProjectNotFoundError: Si le projet n'existe pas
        """
        # Vérifier que le projet existe
        existing_project = self._repository.find_by_id(project_id)
        if existing_project is None:
            raise ProjectNotFoundError(project_id)

        # Supprimer le projet
        return self._repository.delete(project_id)

    def list_projects(self, offset: int = 0, limit: int = 20) -> list[Project]:
        """
        Cas d'usage: Lister les projets avec pagination.

        Args:
            offset: Nombre de projets à ignorer (pour la pagination)
            limit: Nombre maximum de projets à retourner

        Returns:
            Liste de projets (peut être vide)
        """
        return self._repository.find_all(offset=offset, limit=limit)
