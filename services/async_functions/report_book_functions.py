from postgrest import AsyncPostgrestClient
from services.supabase_client import url, key, supabase_client, app_url
import asyncio
import httpx
from typing import List, Dict, Optional, Any
from urllib.parse import quote
from collections import Counter


async def get_active_year_id(access_token) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{url}/rest/v1/years?active=eq.true&select=id",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            },
        )
        data = response.json()
        return data[0]['id'] if data else None


async def get_sequence_averages_with_details(
        access_token: str,
        year_id: str,
) -> List[Dict]:
    """
    Récupère les lignes de sequence_averages pour une année et une séquence données,
    avec nom de l'élève, code de la classe et level_id.
    """

    # 🔹 Requête REST avec jointures
    request_url = (
        f"{url}/rest/v1/sequence_averages"
        "?select=*,"
        "students!inner(name,surname,image_url),"
        "classes!inner(code,level_id)"
        f"&year_id=eq.{year_id}"
        f"&order=class_id.asc"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(
           request_url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        data = response.json()

    # 🔹 Reformater les données
    result = []
    for row in data:
        student = row.get("students", {})
        classe = row.get("classes", {})

        result.append({
            **row,  # tous les champs de sequence_averages
            "student_name": student.get("name"),
            "student_surname": student.get("surname"),
            "student_image": student.get("image_url"),
            "class_code": classe.get("code"),
            "level_id": classe.get("level_id"),
        })

    return result



async def get_notes_by_student_sequence_year(access_token: str, student_id: str, sequence_id: str, year_id: str, ):
    """

    :param access_token:
    :param student_id:
    :param sequence_id:
    :param year_id:
    :return:
    """
    request_url = (
        f"{url}/rest/v1/notes?select=id,"
        f"student_id,subject_id,sequence,year_id,value,coefficient," 
        f"subjects(short_name,group)"
        f"&student_id=eq.{student_id}"
        f"&sequence=eq.{sequence_id}"
        f"&year_id=eq.{year_id}"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(request_url, headers=headers)
        response.raise_for_status()
        notes = response.json()

    # Formatage des données pour ne garder que les paires clé-valeur avec le subject_short_name à plat
    formatted_notes = [
        {
            "id": n["id"],
            "student_id": n["student_id"],
            "subject_id": n["subject_id"],
            "sequence": n["sequence"],
            "year_id": n["year_id"],
            "value": n["value"],
            "coefficient": n["coefficient"],
            "subject_short_name": n["subjects"]["short_name"] if n.get("subjects") else None,
            "subject_group": n["subjects"]["group"] if n.get("subjects") else None
        }
        for n in notes
    ]

    return formatted_notes


async def get_classes_averages(
    access_token: str,
    year_id: str,
    sequence: str,
    class_id: str
):
    """
    Récupère toutes les moyennes de classes pour un year_id et une sequence.

    :param access_token: Jeton d'accès utilisateur (Bearer token)
    :param url: URL de base Supabase
    :param key: Clé API publique Supabase
    :param year_id: ID de l'année scolaire
    :param sequence: Nom ou identifiant de la séquence
    :param class_id: Nom ou identifiant de la classe
    :return: Liste de lignes
    """
    request_url = (
        f"{url}/rest/v1/classes_averages"
        f"?select=*"
        f"&year_id=eq.{year_id}"
        f"&sequence=eq.{sequence}"
        f"&class_id=eq.{class_id}"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(request_url, headers=headers)
        response.raise_for_status()
        return response.json()




