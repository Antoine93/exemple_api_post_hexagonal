#!/usr/bin/env python3
"""
Script pour créer des projets via l'API.
Usage: uv run python create_project.py
"""
import httpx
import json
from datetime import date, timedelta


def create_project(
    name: str,
    description: str,
    start_date: str,
    end_date: str,
    budget: float,
    manager_id: int,
    comment: str | None = None
):
    """
    Crée un projet via l'API.

    Args:
        name: Nom du projet
        description: Description du projet
        start_date: Date de début (format YYYY-MM-DD)
        end_date: Date de fin (format YYYY-MM-DD)
        budget: Budget du projet
        manager_id: ID du manager
        comment: Commentaire optionnel
    """
    url = "http://localhost:8000/api/projects"

    data = {
        "name": name,
        "description": description,
        "start_date": start_date,
        "end_date": end_date,
        "budget": budget,
        "manager_id": manager_id,
        "comment": comment
    }

    print(f"📤 Envoi de la requête POST à {url}")
    print(f"📋 Données: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print()

    try:
        response = httpx.post(url, json=data, timeout=10.0)

        if response.status_code == 201:
            print("✅ Projet créé avec succès!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erreur {response.status_code}")
            print(response.text)

    except httpx.ConnectError:
        print("❌ Erreur: Impossible de se connecter à l'API")
        print("Assurez-vous que le serveur est démarré avec:")
        print("  uv run hypercorn src.main:app --reload --bind 0.0.0.0:8000")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")


def main():
    """Point d'entrée principal avec des exemples de projets."""

    print("=" * 60)
    print("🚀 Création de projets via l'API")
    print("=" * 60)
    print()

    # Projet 1
    create_project(
        name="Migration Cloud Azure",
        description="Migration de l'infrastructure vers Azure Cloud",
        start_date="2025-02-01",
        end_date="2025-08-31",
        budget=250000.00,
        manager_id=1,
        comment="Priorité haute - Q1 2025"
    )

    print("\n" + "-" * 60 + "\n")

    # Projet 2
    create_project(
        name="Refonte Application Mobile",
        description="Refonte complète de l'application mobile iOS et Android",
        start_date="2025-03-15",
        end_date="2025-12-31",
        budget=180000.50,
        manager_id=2,
        comment="Design system + nouvelle architecture"
    )

    print("\n" + "-" * 60 + "\n")

    # Projet 3
    create_project(
        name="API Gateway Implementation",
        description="Mise en place d'une API Gateway pour tous les microservices",
        start_date="2025-01-10",
        end_date="2025-06-30",
        budget=95000.00,
        manager_id=1,
        comment="Kong Gateway + observabilité"
    )

    print("\n" + "=" * 60)
    print("✅ Script terminé!")
    print("=" * 60)


if __name__ == "__main__":
    main()
