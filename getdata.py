from datetime import datetime
from pandas import DataFrame
import requests

from credentials import NOTION_TOKEN, DATABASE_ID

def notion_api(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Accept": "application/json",
        "Notion-Version": "2022-02-22",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + NOTION_TOKEN
    }
    response = requests.post(url, headers=headers)
    return format_data(response.json())

def format_data(data):
    def extract(page):
        prop = page['properties']
        entry = dict(
            id=page['id'],
            user_id=prop['Oleh']['people'][0]['id'],
            date=prop['Tanggal']['date']['start'],
            spent=prop['Nama']['title'][0]['plain_text'],
            value=prop['Nominal']['number'],
            qty=prop['Jumlah']['number'],
            category=prop['Kategori']['select']['name'],
            type=prop['Tipe']['select']['name']
        )
        entry['date'] = datetime.strptime(entry['date'],"%Y-%m-%d")
        return entry
    results = [extract(page) for page in data['results']]
    results = DataFrame(results)
    return results

if __name__ == "__main__":
    data = notion_api(DATABASE_ID)
    data.to_csv("laporan-keuangan.csv",index=False)