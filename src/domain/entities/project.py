"""
Entité métier Project - PURE PYTHON, aucune dépendance externe.
Contient UNIQUEMENT la logique métier liée à l'entité elle-même.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Project:
    """
    Entité Project du domaine.

    Règles métier:
    - Le budget doit être positif
    - La date de fin doit être après la date de début
    - Le nom ne peut pas être vide
    """
    id: Optional[int]
    name: str
    description: str
    start_date: date
    end_date: date
    budget: float
    comment: Optional[str]
    manager_id: int

    def __post_init__(self):
        """Validation des règles métier de l'entité."""
        self._validate()

    def _validate(self):
        """Valide les règles métier de base."""
        if not self.name or self.name.strip() == "":
            raise ValueError("Le nom du projet ne peut pas être vide")

        if self.budget <= 0:
            raise ValueError("Le budget doit être positif")

        if self.end_date <= self.start_date:
            raise ValueError("La date de fin doit être après la date de début")

    def is_active(self) -> bool:
        """Vérifie si le projet est actif (logique métier)."""
        today = date.today()
        return self.start_date <= today <= self.end_date

    def days_remaining(self) -> int:
        """Calcule les jours restants (logique métier)."""
        today = date.today()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days
