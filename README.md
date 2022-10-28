**Ong Stock**

Para rodar a aplicação deverá ter um MySQL local, com um schema ong_stock.

**Instalar os requirements**

Com o Python já instalado, rodar:
pip install flask flask_sqlalchemy flask_login werkzeug==2.0.0 mysql-connector-python mysqlclient

A pasta static é pra conter todos os arquivos estaticos, css, js.

Templates, os html

o __init__.py é só pra fazer a conexão do banco, aqui pode configurar as credenciais do teu banco.

app.py é a main do projeto

models.py, onde vai ficar todos os modelos/classes/tabelas, nele podemos definir uma classe que irá criar automaticamente uma tabela no banco de dados.

**Para criar a tabela que está no models.py**

Abre o terminal e dá um python
com o console python aberto dá rodar: 
from models import db
db.create_all()
exit

após isso terá criado a tabela no banco


Migrate 
unica vez!
set FLASK_APP=__init__.py

flask db init

sempre que for fazer um migrate
flask db migrate -m "create new table"

flask db upgrade