import requests
import json

# url = "https://lingvanex-translate.p.rapidapi.com/translate"

# palavra = "go"

# payload = {
# 	"from": "en_GB",
# 	"to": "pt_PT",
# 	"data": f"{palavra}",
# 	"platform": "api"
# }
# headers = {
# 	"content-type": "application/json",
# 	"X-RapidAPI-Key": "bef9762c24msh0e3ee3b07607e1fp13bb0ajsn78f64f38a680",
# 	"X-RapidAPI-Host": "lingvanex-translate.p.rapidapi.com"
# }

# response = requests.request("POST", url, json=payload, headers=headers)
# texto = json.loads(response.content)
# print(texto['result'])
texto = ([('titulo', 'teste 11'), ('vegetariana', 'on'), ('vegana', 'on'), ('porcoes', '1'), ('tempo', '5'), ('tiporefeicao', '1'), ('editordata', '<p>teste</p>')])
dicionario = {texto[i][0]: texto[i][1] for i in range(0, len(texto), 1)}
print(type(dicionario))

if 'vegetariana' in dicionario:
    print(type(dicionario['vegetariana']))
