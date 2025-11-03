"""
Service du domaine: contient la LOGIQUE MÉTIER.
Orchestre les entités et utilise les ports secondaires.
NE DÉPEND PAS des adapters, uniquement des INTERFACES (ports).
"""
from domain.entities.project import Project
from ports.secondary.project_repository import ProjectRepositoryPort


class ProjectService:
    """
    Service métier pour la gestion des projets.

    Ce service contient la logique métier complexe qui va au-delà
    des simples règles de validation d'une entité.
    """

    def __init__(self, project_repository: ProjectRepositoryPort):
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
        start_date,
        end_date,
        budget: float,
        comment: str,
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
            raise ValueError(f"Un projet avec le nom '{name}' existe déjà")

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
            raise ValueError(f"Le projet avec l'ID {project_id} n'existe pas")

        return project
