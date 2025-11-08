"""
Port primaire: interface des cas d'usage.
Définit le CONTRAT que le domaine expose vers l'extérieur.
Les adapters primaires dépendent de CETTE INTERFACE.
"""
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Optional
from src.domain.entities.project import Project
from src.domain.entities.project_type import ProjectType


class ProjectUseCasesPort(ABC):
    """
    Interface des cas d'usage pour les projets.

    Cette interface définit les opérations métier que le domaine
    expose aux adapters primaires (API, CLI, etc.).

    Type Safety:
    - Toutes les méthodes ont des annotations de type complètes
    - Utilise Optional pour les paramètres optionnels
    - Utilise datetime.date pour les dates (pas de types ambigus)
    """

    @abstractmethod
    def create_project(
        self,
        numero: str,
        nom: str,
        description: str,
        date_debut: date,
        date_echeance: date,
        type: ProjectType,
        stade: Optional[str],
        commentaire: Optional[str],
        heures_planifiees: float,
        heures_reelles: float,
        est_template: bool,
        projet_template_id: Optional[int],
        responsable_id: int,
        entreprise_id: int,
        contact_id: Optional[int]
    ) -> Project:
        """
        Crée un nouveau projet.

        Args:
            numero: Numéro unique du projet
            nom: Nom du projet
            description: Description détaillée
            date_debut: Date de début du projet
            date_echeance: Date de fin du projet (doit être après date_debut)
            type: Type de projet (enum ProjectType)
            stade: Stade actuel du projet (optionnel)
            commentaire: Commentaire optionnel
            heures_planifiees: Heures planifiées (>= 0)
            heures_reelles: Heures réelles (>= 0)
            est_template: Indique si c'est un template
            projet_template_id: ID du template source (si créé depuis template)
            responsable_id: ID du responsable
            entreprise_id: ID de l'entreprise
            contact_id: ID du contact (optionnel)

        Returns:
            Le projet créé avec son ID généré

        Raises:
            ProjectAlreadyExistsError: Si le numero ou nom existe déjà
            ValueError: Si les règles métier ne sont pas respectées
        """
        pass

    @abstractmethod
    def get_project(self, project_id: int) -> Project:
        """
        Récupère un projet par son ID.

        Args:
            project_id: L'identifiant unique du projet

        Returns:
            Le projet trouvé

        Raises:
            ProjectNotFoundError: Si le projet n'existe pas
        """
        pass

    @abstractmethod
    def update_project(
        self,
        project_id: int,
        numero: Optional[str] = None,
        nom: Optional[str] = None,
        description: Optional[str] = None,
        date_debut: Optional[date] = None,
        date_echeance: Optional[date] = None,
        type: Optional[ProjectType] = None,
        stade: Optional[str] = None,
        commentaire: Optional[str] = None,
        heures_planifiees: Optional[float] = None,
        heures_reelles: Optional[float] = None,
        est_template: Optional[bool] = None,
        projet_template_id: Optional[int] = None,
        responsable_id: Optional[int] = None,
        entreprise_id: Optional[int] = None,
        contact_id: Optional[int] = None
    ) -> Project:
        """
        Met à jour un projet existant.

        Args:
            project_id: L'identifiant du projet à modifier
            Tous les autres paramètres sont optionnels (PATCH sémantique)

        Returns:
            Le projet modifié

        Raises:
            ProjectNotFoundError: Si le projet n'existe pas
            ProjectAlreadyExistsError: Si le nouveau numero/nom existe déjà
            ValueError: Si les règles métier ne sont pas respectées
        """
        pass

    @abstractmethod
    def delete_project(self, project_id: int) -> bool:
        """
        Supprime un projet.

        Args:
            project_id: L'identifiant du projet à supprimer

        Returns:
            True si le projet a été supprimé

        Raises:
            ProjectNotFoundError: Si le projet n'existe pas
        """
        pass

    @abstractmethod
    def list_projects(self, offset: int = 0, limit: int = 20) -> list[Project]:
        """
        Liste les projets avec pagination.

        Args:
            offset: Nombre de projets à ignorer (pour la pagination)
            limit: Nombre maximum de projets à retourner

        Returns:
            Liste de projets (peut être vide)
        """
        pass

    @abstractmethod
    def dupliquer_projet(
        self,
        project_id: int,
        nouveau_numero: str,
        nouveau_nom: str,
        nouvelle_date_debut: date,
        nouvelle_date_echeance: date
    ) -> Project:
        """
        Duplique un projet existant avec de nouvelles informations.

        Copie toutes les données du projet source sauf:
        - ID (sera généré)
        - numero (fourni en paramètre)
        - nom (fourni en paramètre)
        - dates (fournies en paramètres)
        - heures_reelles (remis à 0)

        Args:
            project_id: ID du projet à dupliquer
            nouveau_numero: Nouveau numéro unique
            nouveau_nom: Nouveau nom
            nouvelle_date_debut: Nouvelle date de début
            nouvelle_date_echeance: Nouvelle date d'échéance

        Returns:
            Le nouveau projet créé

        Raises:
            ProjectNotFoundError: Si le projet source n'existe pas
            ProjectAlreadyExistsError: Si le nouveau numero/nom existe déjà
            ValueError: Si les règles métier ne sont pas respectées
        """
        pass

    @abstractmethod
    def sauvegarder_comme_template(self, project_id: int) -> Project:
        """
        Transforme un projet existant en template.

        Met le champ est_template à True.

        Args:
            project_id: ID du projet à transformer en template

        Returns:
            Le projet modifié (maintenant template)

        Raises:
            ProjectNotFoundError: Si le projet n'existe pas
        """
        pass

    @abstractmethod
    def creer_depuis_template(
        self,
        template_id: int,
        numero: str,
        nom: str,
        date_debut: date,
        date_echeance: date,
        responsable_id: int,
        entreprise_id: int,
        contact_id: Optional[int] = None
    ) -> Project:
        """
        Crée un nouveau projet à partir d'un template.

        Copie les données du template sauf:
        - ID (sera généré)
        - numero, nom, dates (fournis en paramètres)
        - responsable_id, entreprise_id, contact_id (fournis en paramètres)
        - heures_reelles (remis à 0)
        - est_template (mis à False)
        - projet_template_id (mis à template_id)

        Args:
            template_id: ID du template source
            numero: Numéro unique du nouveau projet
            nom: Nom du nouveau projet
            date_debut: Date de début
            date_echeance: Date d'échéance
            responsable_id: ID du responsable
            entreprise_id: ID de l'entreprise
            contact_id: ID du contact (optionnel)

        Returns:
            Le nouveau projet créé depuis le template

        Raises:
            ProjectNotFoundError: Si le template n'existe pas
            ValueError: Si le template n'est pas marqué comme template
            ProjectAlreadyExistsError: Si le numero/nom existe déjà
        """
        pass

    @abstractmethod
    def find_templates(self) -> list[Project]:
        """
        Liste tous les projets templates.

        Returns:
            Liste des projets avec est_template=True
        """
        pass

    @abstractmethod
    def calculer_avancement(self, project_id: int) -> float:
        """
        Calcule le pourcentage d'avancement d'un projet.

        Args:
            project_id: ID du projet

        Returns:
            Pourcentage d'avancement (0-100%)

        Raises:
            ProjectNotFoundError: Si le projet n'existe pas
        """
        pass

    @abstractmethod
    def calculer_ecart_temps(self, project_id: int) -> dict:
        """
        Calcule l'écart entre heures planifiées et réelles.

        Args:
            project_id: ID du projet

        Returns:
            Dict avec:
                - heures_planifiees: float
                - heures_reelles: float
                - ecart: float (positif = dépassement, négatif = sous budget)
                - ecart_pourcentage: float

        Raises:
            ProjectNotFoundError: Si le projet n'existe pas
        """
        pass
