#!/usr/bin/env python3
"""
Script interactif pour créer des projets via l'API.
Usage: uv run python create_project_interactive.py
"""
import httpx
import json
from datetime import date


def create_project_interactive():
    """Crée un projet de manière interactive en demandant les informations à l'utilisateur."""

    print("=" * 60)
    print("🚀 Création d'un projet - Mode Interactif")
    print("=" * 60)
    print()

    # Collecte des informations
    name = input("📝 Nom du projet: ").strip()
    description = input("📋 Description: ").strip()
    start_date = input("📅 Date de début (YYYY-MM-DD): ").strip()
    end_date = input("📅 Date de fin (YYYY-MM-DD): ").strip()

    while True:
        try:
            budget = float(input("💰 Budget: ").strip())
            break
        except ValueError:
            print("❌ Veuillez entrer un nombre valide pour le budget")

    while True:
        try:
            manager_id = int(input("👤 ID du manager: ").strip())
            break
        except ValueError:
            print("❌ Veuillez entrer un nombre entier pour l'ID du manager")

    comment = input("💬 Commentaire (optionnel, appuyez sur Entrée pour ignorer): ").strip()
    if not comment:
        comment = None

    print()
    print("-" * 60)

    # Préparation des données
    data = {
        "name": name,
        "description": description,
        "start_date": start_date,
        "end_date": end_date,
        "budget": budget,
        "manager_id": manager_id,
        "comment": comment
    }

    print("📤 Données à envoyer:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print()

    confirm = input("Confirmer l'envoi ? (o/n): ").strip().lower()
    if confirm not in ['o', 'oui', 'y', 'yes']:
        print("❌ Annulé par l'utilisateur")
        return

    # Envoi de la requête
    url = "http://localhost:8000/api/projects"

    try:
        response = httpx.post(url, json=data, timeout=10.0)

        print()
        if response.status_code == 201:
            print("✅ Projet créé avec succès!")
            print()
            print("📊 Réponse du serveur:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erreur {response.status_code}")
            print(response.text)

    except httpx.ConnectError:
        print()
        print("❌ Erreur: Impossible de se connecter à l'API")
        print("Assurez-vous que le serveur est démarré avec:")
        print("  uv run hypercorn src.main:app --reload --bind 0.0.0.0:8000")
    except Exception as e:
        print()
        print(f"❌ Erreur inattendue: {e}")


def main():
    """Point d'entrée principal."""
    while True:
        create_project_interactive()

        print()
        print("-" * 60)
        again = input("Créer un autre projet ? (o/n): ").strip().lower()
        if again not in ['o', 'oui', 'y', 'yes']:
            break
        print()

    print()
    print("=" * 60)
    print("👋 Au revoir!")
    print("=" * 60)


if __name__ == "__main__":
    main()
