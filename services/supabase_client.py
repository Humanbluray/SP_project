import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
app_url = os.getenv('APP_URL')

school_name_fr = os.getenv('SCHOOL_NAME_FR')
school_name_en = os.getenv('SCHOOL_NAME_EN')
school_code = os.getenv('SCHOOL_CODE')
school_delegation_fr = os.getenv('SCHOOL_DELEGATION_FR')
school_delegation_en = os.getenv('SCHOOL_DELEGATION_EN')
national_devise_fr = os.getenv('NATIONAL_DEVISE_FR')
national_devise_en = os.getenv('NATIONAL_DEVISE_EN')
school_republic_fr = os.getenv('SCHOOL_REPUBLIC_FR')
school_republic_en = os.getenv('SCHOOL_REPUBLIC_EN')
logo_url = os.getenv('LOGO_URL')

supabase_client = create_client(url, key)

# supabase_client.auth.sign_in_with_password(
#     {"email": 'principal@mail.com', 'password': '123456'}
# )
#
# resp = supabase_client.table('sequence_averages').select('*, classes(code)').execute()
# tle: list = []
#
# for item in resp.data:
#     if item['classes']['code'] == '3e ALL 2':
#         print(f"class_id: {item['class_id']}")
#         print(f"year_id: {item['year_id']}")
#         dico: dict = {}
#         for key in item.keys():
#             dico[key] = item[key]
#
#         tle.append(dico)
#
# print(f"longueur {len(tle)}")
#
# average = 0
# list_value = []
# nb_sup_10 = 0
#
# for item in tle:
#     if item['value'] >= 10:
#         nb_sup_10 += 1
#
#     average += item['value']
#     list_value.append(item['value'])
#
# moy_gen = average / len(tle)
# print(f"moygen: {moy_gen}")
#
# print(f"nb > 10 {nb_sup_10}")
# print(f'notemin {min(list_value)}')
# print(f'notemax {max(list_value)}')
# print(f'taux de réussite: {nb_sup_10 * 100 / len(tle)}')
#
#
#
#
#
#
#
#
#
