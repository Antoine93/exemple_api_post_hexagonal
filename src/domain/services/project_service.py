"""
Service du domaine: contient la LOGIQUE MÉTIER.
Orchestre les entités et utilise les ports secondaires.
NE DÉPEND PAS des adapters, uniquement des INTERFACES (ports).
"""
from datetime import date, datetime
from typing import Optional
from src.domain.entities.project import Project
from src.domain.entities.project_type import ProjectType
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
        Cas d'usage: Créer un nouveau projet.

        Logique métier:
        1. Vérifier que le numero n'existe pas déjà
        2. Vérifier que le nom n'existe pas déjà
        3. Créer l'entité (validation automatique via __post_init__)
        4. Sauvegarder via le port secondaire

        Args:
            Tous les attributs du projet

        Returns:
            Le projet créé avec son ID

        Raises:
            ProjectAlreadyExistsError: Si le numero ou nom existe déjà
            ValueError: Si les règles métier ne sont pas respectées
        """
        # Règle métier: vérifier l'unicité du numéro
        if self._repository.exists_by_numero(numero):
            raise ProjectAlreadyExistsError(f"Un projet avec le numéro '{numero}' existe déjà")

        # Règle métier: vérifier l'unicité du nom
        if self._repository.exists_by_name(nom):
            raise ProjectAlreadyExistsError(f"Un projet avec le nom '{nom}' existe déjà")

        # Création de l'entité (validation automatique dans __post_init__)
        project = Project(
            id=None,  # Sera généré par la base de données
            numero=numero,
            nom=nom,
            description=description,
            date_debut=date_debut,
            date_echeance=date_echeance,
            type=type,
            stade=stade,
            commentaire=commentaire,
            heures_planifiees=heures_planifiees,
            heures_reelles=heures_reelles,
            est_template=est_template,
            projet_template_id=projet_template_id,
            responsable_id=responsable_id,
            entreprise_id=entreprise_id,
            contact_id=contact_id,
            date_creation=datetime.now()
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
            ProjectNotFoundError: Si le projet n'existe pas
        """
        project = self._repository.find_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError(project_id)

        return project

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
        Cas d'usage: Mettre à jour un projet existant.

        Logique métier:
        1. Vérifier que le projet existe
        2. Si le numero change, vérifier qu'il n'existe pas déjà
        3. Si le nom change, vérifier qu'il n'existe pas déjà
        4. Mettre à jour uniquement les champs fournis
        5. Recréer l'entité avec validation
        6. Sauvegarder via le port secondaire

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
        # 1. Récupérer le projet existant
        existing_project = self._repository.find_by_id(project_id)
        if existing_project is None:
            raise ProjectNotFoundError(project_id)

        # 2. Si le numero change, vérifier qu'il n'existe pas déjà
        if numero is not None and numero != existing_project.numero:
            if self._repository.exists_by_numero(numero):
                raise ProjectAlreadyExistsError(f"Un projet avec le numéro '{numero}' existe déjà")

        # 3. Si le nom change, vérifier qu'il n'existe pas déjà
        if nom is not None and nom != existing_project.nom:
            if self._repository.exists_by_name(nom):
                raise ProjectAlreadyExistsError(f"Un projet avec le nom '{nom}' existe déjà")

        # 4. Créer le projet avec les valeurs mises à jour
        updated_project = Project(
            id=project_id,
            numero=numero if numero is not None else existing_project.numero,
            nom=nom if nom is not None else existing_project.nom,
            description=description if description is not None else existing_project.description,
            date_debut=date_debut if date_debut is not None else existing_project.date_debut,
            date_echeance=date_echeance if date_echeance is not None else existing_project.date_echeance,
            type=type if type is not None else existing_project.type,
            stade=stade if stade is not None else existing_project.stade,
            commentaire=commentaire if commentaire is not None else existing_project.commentaire,
            heures_planifiees=heures_planifiees if heures_planifiees is not None else existing_project.heures_planifiees,
            heures_reelles=heures_reelles if heures_reelles is not None else existing_project.heures_reelles,
            est_template=est_template if est_template is not None else existing_project.est_template,
            projet_template_id=projet_template_id if projet_template_id is not None else existing_project.projet_template_id,
            responsable_id=responsable_id if responsable_id is not None else existing_project.responsable_id,
            entreprise_id=entreprise_id if entreprise_id is not None else existing_project.entreprise_id,
            contact_id=contact_id if contact_id is not None else existing_project.contact_id,
            date_creation=existing_project.date_creation  # Ne jamais modifier la date de création
        )

        # 5. Sauvegarder via le port secondaire
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

    def dupliquer_projet(
        self,
        project_id: int,
        nouveau_numero: str,
        nouveau_nom: str,
        nouvelle_date_debut: date,
        nouvelle_date_echeance: date
    ) -> Project:
        """
        Cas d'usage: Dupliquer un projet existant.

        Logique métier:
        1. Récupérer le projet source
        2. Vérifier que le nouveau numero n'existe pas
        3. Vérifier que le nouveau nom n'existe pas
        4. Créer un nouveau projet avec les données du source
        5. Mettre heures_reelles à 0
        6. Sauvegarder le nouveau projet

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
        # 1. Récupérer le projet source
        source_project = self._repository.find_by_id(project_id)
        if source_project is None:
            raise ProjectNotFoundError(project_id)

        # 2. Vérifier l'unicité du nouveau numero
        if self._repository.exists_by_numero(nouveau_numero):
            raise ProjectAlreadyExistsError(f"Un projet avec le numéro '{nouveau_numero}' existe déjà")

        # 3. Vérifier l'unicité du nouveau nom
        if self._repository.exists_by_name(nouveau_nom):
            raise ProjectAlreadyExistsError(f"Un projet avec le nom '{nouveau_nom}' existe déjà")

        # 4. Créer le nouveau projet (copie du source)
        nouveau_projet = Project(
            id=None,  # Sera généré
            numero=nouveau_numero,
            nom=nouveau_nom,
            description=source_project.description,
            date_debut=nouvelle_date_debut,
            date_echeance=nouvelle_date_echeance,
            type=source_project.type,
            stade=source_project.stade,
            commentaire=source_project.commentaire,
            heures_planifiees=source_project.heures_planifiees,
            heures_reelles=0.0,  # Remis à zéro
            est_template=False,  # Un projet dupliqué n'est pas un template
            projet_template_id=None,  # Pas créé depuis un template
            responsable_id=source_project.responsable_id,
            entreprise_id=source_project.entreprise_id,
            contact_id=source_project.contact_id,
            date_creation=datetime.now()
        )

        # 5. Sauvegarder
        return self._repository.save(nouveau_projet)

    def sauvegarder_comme_template(self, project_id: int) -> Project:
        """
        Cas d'usage: Transformer un projet en template.

        Args:
            project_id: ID du projet à transformer en template

        Returns:
            Le projet modifié (maintenant template)

        Raises:
            ProjectNotFoundError: Si le projet n'existe pas
        """
        # Récupérer le projet
        project = self._repository.find_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)

        # Mettre est_template à True
        project_as_template = Project(
            id=project.id,
            numero=project.numero,
            nom=project.nom,
            description=project.description,
            date_debut=project.date_debut,
            date_echeance=project.date_echeance,
            type=project.type,
            stade=project.stade,
            commentaire=project.commentaire,
            heures_planifiees=project.heures_planifiees,
            heures_reelles=project.heures_reelles,
            est_template=True,  # Devient template
            projet_template_id=project.projet_template_id,
            responsable_id=project.responsable_id,
            entreprise_id=project.entreprise_id,
            contact_id=project.contact_id,
            date_creation=project.date_creation
        )

        return self._repository.update(project_as_template)

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
        Cas d'usage: Créer un projet depuis un template.

        Logique métier:
        1. Récupérer le template
        2. Vérifier que c'est bien un template
        3. Vérifier l'unicité du numero et nom
        4. Créer le nouveau projet basé sur le template
        5. Remettre heures_reelles à 0
        6. Mettre est_template à False
        7. Définir projet_template_id

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
        # 1. Récupérer le template
        template = self._repository.find_by_id(template_id)
        if template is None:
            raise ProjectNotFoundError(template_id)

        # 2. Vérifier que c'est bien un template
        if not template.is_template():
            raise ValueError(f"Le projet {template_id} n'est pas un template")

        # 3. Vérifier l'unicité
        if self._repository.exists_by_numero(numero):
            raise ProjectAlreadyExistsError(f"Un projet avec le numéro '{numero}' existe déjà")

        if self._repository.exists_by_name(nom):
            raise ProjectAlreadyExistsError(f"Un projet avec le nom '{nom}' existe déjà")

        # 4. Créer le nouveau projet basé sur le template
        nouveau_projet = Project(
            id=None,  # Sera généré
            numero=numero,
            nom=nom,
            description=template.description,
            date_debut=date_debut,
            date_echeance=date_echeance,
            type=template.type,
            stade=template.stade,
            commentaire=template.commentaire,
            heures_planifiees=template.heures_planifiees,
            heures_reelles=0.0,  # Remis à zéro
            est_template=False,  # Pas un template
            projet_template_id=template_id,  # Lien vers le template source
            responsable_id=responsable_id,
            entreprise_id=entreprise_id,
            contact_id=contact_id,
            date_creation=datetime.now()
        )

        return self._repository.save(nouveau_projet)

    def find_templates(self) -> list[Project]:
        """
        Cas d'usage: Lister tous les templates.

        Returns:
            Liste des projets avec est_template=True
        """
        return self._repository.find_templates()

    def calculer_avancement(self, project_id: int) -> float:
        """
        Cas d'usage: Calculer l'avancement d'un projet.

        Args:
            project_id: ID du projet

        Returns:
            Pourcentage d'avancement (0-100%)

        Raises:
            ProjectNotFoundError: Si le projet n'existe pas
        """
        project = self._repository.find_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)

        return project.calculer_avancement()

    def calculer_ecart_temps(self, project_id: int) -> dict:
        """
        Cas d'usage: Calculer l'écart temps d'un projet.

        Args:
            project_id: ID du projet

        Returns:
            Dict avec heures planifiées, réelles, écart et pourcentage

        Raises:
            ProjectNotFoundError: Si le projet n'existe pas
        """
        project = self._repository.find_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)

        ecart = project.calculer_ecart_temps()
        ecart_pourcentage = 0.0
        if project.heures_planifiees > 0:
            ecart_pourcentage = (ecart / project.heures_planifiees) * 100

        return {
            "heures_planifiees": project.heures_planifiees,
            "heures_reelles": project.heures_reelles,
            "ecart": ecart,
            "ecart_pourcentage": ecart_pourcentage
        }
