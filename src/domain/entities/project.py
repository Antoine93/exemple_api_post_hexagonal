"""
Entité métier Project - PURE PYTHON, aucune dépendance externe.
Contient UNIQUEMENT la logique métier liée à l'entité elle-même.
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from src.domain.entities.project_type import ProjectType


@dataclass
class Project:
    """
    Entité Project du domaine.

    Règles métier:
    - Le budget doit être positif
    - La date d'échéance doit être après la date de début
    - Le nom ne peut pas être vide
    - Le numéro ne peut pas être vide
    - Les heures planifiées doivent être >= 0
    - Les heures réelles doivent être >= 0
    - Si est_template=True, le projet est un modèle réutilisable
    - Si projet_template_id est fourni, ce projet a été créé depuis un template

    Attributs:
        id: Identifiant unique (None si pas encore persisté)
        numero: Numéro unique du projet
        nom: Nom du projet
        description: Description détaillée
        date_debut: Date de début du projet
        date_echeance: Date de fin prévue
        type: Type de projet (enum ProjectType)
        stade: Stade actuel du projet
        commentaire: Commentaires libres
        heures_planifiees: Nombre d'heures planifiées
        heures_reelles: Nombre d'heures réellement passées
        est_template: Indique si ce projet est un template
        projet_template_id: ID du template source (si créé depuis template)
        responsable_id: ID de l'utilisateur responsable
        entreprise_id: ID de l'entreprise cliente
        contact_id: ID du contact principal (optionnel)
        date_creation: Date de création du projet
    """

    # Identifiants
    id: Optional[int]
    numero: str

    # Informations générales
    nom: str
    description: str
    type: ProjectType
    stade: Optional[str]
    commentaire: Optional[str]

    # Dates
    date_debut: date
    date_echeance: date
    date_creation: datetime

    # Heures
    heures_planifiees: float
    heures_reelles: float

    # Templates
    est_template: bool
    projet_template_id: Optional[int]

    # Relations
    responsable_id: int
    entreprise_id: int
    contact_id: Optional[int]

    def __post_init__(self) -> None:
        """Validation des règles métier de l'entité."""
        self._validate()

    def _validate(self) -> None:
        """
        Valide les règles métier de base.

        Raises:
            ValueError: Si une règle métier n'est pas respectée
        """
        # Validation du nom
        if not self.nom or self.nom.strip() == "":
            raise ValueError("Le nom du projet ne peut pas être vide")

        # Validation du numéro
        if not self.numero or self.numero.strip() == "":
            raise ValueError("Le numéro du projet ne peut pas être vide")

        # Validation des dates
        if self.date_echeance <= self.date_debut:
            raise ValueError("La date d'échéance doit être après la date de début")

        # Validation des heures
        if self.heures_planifiees < 0:
            raise ValueError("Les heures planifiées doivent être >= 0")

        if self.heures_reelles < 0:
            raise ValueError("Les heures réelles doivent être >= 0")

        # Validation du type
        if not isinstance(self.type, ProjectType):
            raise ValueError(f"Le type doit être une instance de ProjectType, reçu: {type(self.type)}")

    def is_active(self) -> bool:
        """
        Vérifie si le projet est actif (logique métier).

        Un projet est actif si la date actuelle est entre date_debut et date_echeance.

        Returns:
            bool: True si le projet est actif, False sinon
        """
        today = date.today()
        return self.date_debut <= today <= self.date_echeance

    def days_remaining(self) -> int:
        """
        Calcule les jours restants jusqu'à l'échéance (logique métier).

        Returns:
            int: Nombre de jours restants (0 si dépassé)
        """
        today = date.today()
        if today > self.date_echeance:
            return 0
        return (self.date_echeance - today).days

    def calculer_avancement(self) -> float:
        """
        Calcule le pourcentage d'avancement basé sur les heures.

        Formule: (heures_reelles / heures_planifiees) * 100

        Returns:
            float: Pourcentage d'avancement (0.0 si heures_planifiees = 0)
                   Peut dépasser 100% si les heures réelles dépassent les heures planifiées
        """
        if self.heures_planifiees == 0:
            return 0.0

        return (self.heures_reelles / self.heures_planifiees) * 100

    def calculer_ecart_temps(self) -> float:
        """
        Calcule l'écart entre les heures réelles et planifiées.

        Un écart positif indique un dépassement.
        Un écart négatif indique qu'il reste des heures planifiées.

        Returns:
            float: Écart en heures (heures_reelles - heures_planifiees)
        """
        return self.heures_reelles - self.heures_planifiees

    def est_en_retard(self) -> bool:
        """
        Vérifie si le projet est en retard.

        Un projet est en retard si les heures réelles dépassent les heures planifiées
        OU si la date actuelle dépasse la date d'échéance.

        Returns:
            bool: True si en retard, False sinon
        """
        today = date.today()
        retard_temporel = today > self.date_echeance
        retard_heures = self.heures_reelles > self.heures_planifiees

        return retard_temporel or retard_heures

    def is_template(self) -> bool:
        """
        Vérifie si ce projet est un template.

        Returns:
            bool: True si c'est un template, False sinon
        """
        return self.est_template

    def created_from_template(self) -> bool:
        """
        Vérifie si ce projet a été créé depuis un template.

        Returns:
            bool: True si créé depuis un template, False sinon
        """
        return self.projet_template_id is not None
