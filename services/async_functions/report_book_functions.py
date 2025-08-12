from postgrest import AsyncPostgrestClient
from services.supabase_client import *
import asyncio
import httpx
from urllib.parse import quote
from typing import List, Dict, Optional, Any


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
        "students!inner(id,name,surname,image_url),"
        "classes!inner(id,code,level_id)"
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
            "student_id": student.get("id"),
            "student_name": student.get("name"),
            "student_surname": student.get("surname"),
            "student_image": student.get("image_url"),
            "class_code": classe.get("code"),
            "level_id": classe.get("level_id"),
            "class_id": classe.get("id"),
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
        f"subjects(id,name,short_name,group)"
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
            "subject_name": n["subjects"]["name"] if n.get("subjects") else None,
            "subject_short_name": n["subjects"]["short_name"] if n.get("subjects") else None,
            "subject_group": n["subjects"]["group"] if n.get("subjects") else None
        }
        for n in notes
    ]

    return formatted_notes


async def get_class_statistics_sequence(access_token: str, year_id: str, class_id: str, sequence: str) -> Dict:
    """
    :param access_token:
    :param class_id:
    :param year_id:
    :param sequence:
    :return:
    """
    request_url = (
        f"{url}/rest/v1/classes_statistics?select=*"
        f"&class_id=eq.{class_id}&"
        f"&sequence=eq.{sequence}&"
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
        data = response.json()

    # On force un seul résultat (si plusieurs, on prend le premier)
    return data[0] if data else None


async def get_student_basic_infos(access_token: str, student_id: str) -> Dict:
    """
    :param: access_token:
    :param : student_id:
    :return:
    """
    request_url = (
        f"{url}/rest/v1/students?select=*"
        f"&id=eq.{student_id}"
    )
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(request_url, headers=headers)
        response.raise_for_status()
        data = response.json()

    # On force un seul résultat (si plusieurs, on prend le premier)
    return data[0] if data else None


async def get_student_discipline_by_sequence(access_token: str, year_id: str, student_id: str, sequence: str)-> List[Dict]:
    """

    :param access_token:
    :param year_id:
    :param student_id:
    :param sequence:
    :return:
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": key,
        "Accept": "application/json"
    }
    request_url = (
        f"{url}/rest/v1/discipline?select=*"
        f"&year_id=eq.{year_id}&"
        f"&student_id=eq.{student_id}&"
        f"&sequence=eq.{sequence}"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(request_url, headers=headers)

    response.raise_for_status()
    return response.json()


import httpx
from typing import Dict, List

# Assurez-vous que ces variables sont définies dans votre environnement
URL = "YOUR_SUPABASE_URL"
KEY = "YOUR_SUPABASE_ANON_KEY"


async def get_student_registration_details(access_token: str, year_id: str, student_id: str) -> List[Dict]:
    """
    Récupère les détails d'inscription d'un étudiant en incluant les informations
    sur l'étudiant, la classe et le professeur principal pour une année donnée.

    Args:
        access_token (str): Le jeton d'accès de l'utilisateur.
        year_id (str): L'ID de l'année scolaire.
        student_id (str): L'ID de l'étudiant.

    Returns:
        List[Dict]: Une liste de dictionnaires contenant les détails ou une liste vide si non trouvé.
    """

    # La requête de jointure est définie ici
    # La syntaxe de Supabase/PostgREST utilise le point-virgule pour lier les tables
    select_query = (
        "*, "  # Sélectionne toutes les colonnes de la table 'registrations'
        "students(*), "  # Sélectionne toutes les colonnes de la table 'students' liée
        "classes:class_id(code, count:registrations(count)), "  # Sélectionne le code de la classe et son effectif
        "head_teachers:class_id(teachers(name, surname))"  # Sélectionne le nom du professeur principal
    )

    request_url = (
        f"{URL}/rest/v1/registrations?select={select_query}"
        f"&student_id=eq.{student_id}"
        f"&year_id=eq.{year_id}"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": KEY,
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(request_url, headers=headers)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur 4xx/5xx

    return response.json()






