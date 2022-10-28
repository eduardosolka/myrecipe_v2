import requests
import json

url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/complexSearch"

querystring = {"query":"cake","number": "20",}

headers = {
	"X-RapidAPI-Key": "bef9762c24msh0e3ee3b07607e1fp13bb0ajsn78f64f38a680",
	"X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
}

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)
resultados = json.loads(response.content)
with open("receitas_bolo.txt","a") as receitas:
        receitas.write(response.text)

for lista in resultados["results"]:
    json_lista = json.loads(json.dumps(lista))
    id = json_lista["id"]
    
    url = f"https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/{id}/information"

    headers = {
        "X-RapidAPI-Key": "bef9762c24msh0e3ee3b07607e1fp13bb0ajsn78f64f38a680",
        "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers)

    print(response.text)
    with open("informacao_receita_bolo.txt","a") as info:
        texto = str(id)+"@@ "+response.text
        info.write(texto)