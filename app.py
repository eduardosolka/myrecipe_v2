from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from __init__ import app, db
from models import Usuario,Receita,PathImagem,Ingrediente,Relacionamento_ingrediente_receita,Medidas,Receitas_salvas,Avaliacoes
import plotly.express as px
from datetime import datetime
import base64 as b64
import numpy
import os
import uuid
import bleach
import pandas as pd
from flask_pagedown import PageDown

app.config.from_object('config')


@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        senha = request.form['password']
        nascimento = request.form['nascimento']
        foto_nome = request.files['foto'].filename
        cep = request.form['cep']
        user = Usuario(name, email, senha, nascimento, cep, foto_nome,0,0,0,0)
        db.session.add(user)
        db.session.commit()

        maior_id = db.session.execute('select max(id) from myrecipe_producao.usuarios')
        for id_novo in maior_id:
            id_novo = id_novo[0]
        foto = request.files['foto']  
        diretorio = r"/home/ubuntu/myrecipe_v2/static/uploads/users/"+str(id_novo)
        os.makedirs(diretorio)       
        foto.save(os.path.join(diretorio, foto.filename))       
        user = Usuario.query.filter_by(email=email).first()
        login_user(user)
        return redirect(url_for('homepage'))
    return render_template('cadastro_usuario.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        user = Usuario.query.filter_by(email=email).first()

        if not user or not user.verify_password(senha):
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('homepage'))

    return render_template('login.html')


@app.route('/homepage', methods=['GET'])
@login_required
def homepage():
    receitas = db.session.execute(''' SELECT * FROM myrecipe_producao.tb_receita where privada = 0 order by id_receita desc limit 20 ''')
    receitas_salvas = db.session.execute('''select rs.id_receita,tr.titulo,count(rs.id_receita) as quantidade_salvas FROM myrecipe_producao.tb_receitas_salvas rs
            inner join myrecipe_producao.tb_receita as tr on rs.id_receita = tr.id_receita
            group by rs.id_receita,tr.titulo order by quantidade_salvas desc limit 20;''')

    maiores_avaliacoes = db.session.execute('''select avg(ta.nota) as media_nota, ta.id_receita,tr.titulo FROM myrecipe_producao.tb_avaliacoes ta 
            inner join myrecipe_producao.tb_receita tr on tr.id_receita = ta.id_receita
            group by ta.id_receita order by media_nota desc limit 20;''')
    paths = PathImagem.query.all()
    for path in paths:
        path.path_imagem = (path.path_imagem.replace("/","#").split("#",-1))[-1]
    return render_template('feed_logado.html',
        receitas_novas=sorted(receitas,key=lambda receita :receita.id_receita,reverse=True),
        receitas_salvas=receitas_salvas,paths=paths,maiores_avaliacoes=maiores_avaliacoes)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('home_sem_login.html')


@app.route('/cadastrar_receita', methods=['GET', 'POST'])
@login_required
def cadastrar_receita():
    if request.method == 'POST':
        titulo = request.form['titulo']
        vegetariana = False
        if 'vegetariana' in request.form:
            if request.form['vegetariana'] == 'on':
                vegetariana = True
        vegana = False
        if 'vegana' in request.form:
            if request.form['vegana'] == 'on':
                vegana = True
        semgluten = False
        if 'semgluten' in request.form:
            if request.form['semgluten'] == 'on':
                semgluten = True
        semlactose = False
        if 'semlactose' in request.form:
            if request.form['semlactose'] == 'on':
                semlactose = True
        saudavel = False
        if 'saudavel' in request.form:
            if request.form['saudavel'] == 'on':
                saudavel = True
        porcoes = int(request.form['porcoes'])
        tempo_preparo = int(request.form['tempo'])
        tipo_refeicao = int(request.form['tiporefeicao'])
        instrucoes = request.form['editordata']
        # teste = permite_tags(instrucoes)
        privada = False
        if  'privada' in request.form:
            if request.form['privada'] == 'on':
                privada = True

        receita = Receita(titulo,vegetariana,vegana,semgluten,semlactose,saudavel,porcoes,tempo_preparo,tipo_refeicao,instrucoes,privada,current_user.id)
        db.session.add(receita)
        db.session.commit()
        
        receita_nova = db.session.execute('select max(id_receita) from myrecipe_producao.tb_receita')
        
        for receita in receita_nova:
            id_novo = receita[0]

        
        for i in range(50):
            if 'quantidade'+str(i) in request.form:
                quantidade = request.form['quantidade'+str(i)]
                ingrediente = request.form['ingrediente'+str(i)]
                unidademedida = request.form['unidademedida'+str(i)]
                relaciona_ingrediente(id_novo, ingrediente, quantidade, unidademedida)
    

        
        diretorio = r"/home/ubuntu/myrecipe_v2/static/uploads/recipes/"+str(id_novo)

        os.makedirs(diretorio)
        foto = request.files['foto']
        foto.save(os.path.join(diretorio, foto.filename))

        path_imagem = PathImagem(id_novo,foto.filename)
        db.session.add(path_imagem)
        db.session.commit()
        flash("Receita cadastrada com sucesso!")
    return render_template('cadastrar_receita.html')

def relaciona_ingrediente(receita,ingrediente,quantidade,medida):
    rel_ingrediente_receita = Relacionamento_ingrediente_receita(receita,ingrediente,quantidade,medida)
    db.session.add(rel_ingrediente_receita)
    db.session.commit() 

@app.route('/cadastrar_ingrediente', methods=['GET', 'POST'])
@login_required
def cadastrar_ingrediente():
    if request.method == 'POST':
        nomesingular = request.form['nomesingular']
        nomeplural = request.form['nomeplural']  
        ingrediente = Ingrediente(nomesingular, nomeplural)
        db.session.add(ingrediente)
        db.session.commit() 
    return render_template('cadastrar_ingrediente.html')

@app.route('/cadastrar_medidas', methods=['GET', 'POST'])
@login_required
def cadastrar_medidas():
    if request.method == 'POST':
        medida_singular = request.form['medida_singular']
        medida_plural = request.form['medida_plural'] 
        medidas = Medidas(medida_singular,medida_plural)
        db.session.add(medidas)
        db.session.commit()    
    return render_template('cadastrar_medidas.html')

@app.route('/mostrar_receita/<int:id_receita>', methods=['GET', 'POST'])
@login_required
def mostrar_receita(id_receita):    
    receita = Receita.query.filter_by(id_receita=id_receita).first()
    ingredientes = Relacionamento_ingrediente_receita.query.filter_by(id_receita=id_receita)
    medidas = Medidas.query.all()
    paths = PathImagem.query.all() 
    recomendacoes = recomendacao(id_receita)
    return render_template('mostrar_receita.html',receita=receita,paths=paths,ingredientes=ingredientes,medidas=medidas,recomendacoes=recomendacoes)

@app.route('/minhas_receitas', methods=['GET', 'POST'])
@login_required
def minhas_receitas():
    ingredientes = Relacionamento_ingrediente_receita.query.all()
    receitas = db.session.execute(f''' SELECT * FROM myrecipe_producao.tb_receita where id_usuario={current_user.id} order by id_receita desc ''')
    medidas = Medidas.query.all()
    paths = PathImagem.query.all() 
    return render_template('minhas_receitas.html',paths=paths,ingredientes=ingredientes,medidas=medidas,receitas=receitas)

@app.route('/avaliacoes/<int:id_receita>/<int:nota>', methods=['GET', 'POST'])
@login_required
def avaliacoes(id_receita,nota):
    avaliacoes_dadas = Avaliacoes.query.filter_by(id_receita=id_receita,id_usuario=current_user.id).first()
    if(avaliacoes_dadas == None):
        id_receita = id_receita
        nota = nota
        avaliacoes = Avaliacoes(id_receita, current_user.id, nota)
        db.session.add(avaliacoes)
        db.session.commit()  

    return redirect(url_for('mostrar_salvas'))

    
@app.route('/salvar_receita/<int:id_receita>', methods=['GET', 'POST'])
@login_required
def salvar_receita(id_receita):
    receitas_salvas = Receitas_salvas.query.filter_by(id_receita=id_receita,id_usuario=current_user.id).first()
    if(receitas_salvas == None):
        hora = datetime.now()
        receitas_salvas = Receitas_salvas(id_receita, current_user.id, hora)
        db.session.add(receitas_salvas)
        db.session.commit()
        receita = Receita.query.filter_by(id_receita=id_receita).first()
        ingredientes = Relacionamento_ingrediente_receita.query.filter_by(id_receita=id_receita)
        receitas = Receita.query.all()
        medidas = Medidas.query.all()
        paths = PathImagem.query.all()
        recomendacoes = recomendacao(id_receita)
        return redirect(url_for('mostrar_receita',id_receita=id_receita))
    return redirect(url_for('mostrar_receita',id_receita=id_receita)) 
    
    
@app.route('/mostrar_salvas', methods=['GET', 'POST'])
@login_required
def mostrar_salvas():
    receitas_salvas = db.session.execute(f'''SELECT us.nome,rs.id_usuario as id_usuario,tr.* ,us_cria.nome as criador_receita  FROM myrecipe_producao.tb_receitas_salvas rs
    inner join myrecipe_producao.tb_receita tr on tr.id_receita = rs.id_receita
    inner join myrecipe_producao.usuarios us on us.id = rs.id_usuario
    left join myrecipe_producao.usuarios us_cria on tr.id_usuario = us_cria.id 
    where tr.privada = 0
    and rs.id_usuario = {current_user.id}
    group by tr.id_receita,rs.id_usuario,criador_receita
    order by rs.hora desc;''')
    
    avals = db.session.execute('select max(id_receita) from myrecipe_producao.tb_avaliacoes')
        
    for aval in avals:
        aval = aval[0]

    if aval == None:
        avaliadas = 0
    else:
        avaliadas = Avaliacoes.query.filter_by(id_usuario=current_user.id)
    
    medidas = Medidas.query.all()
    paths = PathImagem.query.all()
    return render_template('mostrar_salvas.html',receitas_salvas=receitas_salvas,paths=paths,medidas=medidas,avaliadas=avaliadas)


def levenshteinDistanceDP(token1, token2):
    distances = numpy.zeros((len(token1) + 1, len(token2) + 1))

    for t1 in range(len(token1) + 1):
        distances[t1][0] = t1

    for t2 in range(len(token2) + 1):
        distances[0][t2] = t2
        
    a = 0
    b = 0
    c = 0
    
    for t1 in range(1, len(token1) + 1):
        for t2 in range(1, len(token2) + 1):
            if (token1[t1-1] == token2[t2-1]):
                distances[t1][t2] = distances[t1 - 1][t2 - 1]
            else:
                a = distances[t1][t2 - 1]
                b = distances[t1 - 1][t2]
                c = distances[t1 - 1][t2 - 1]
                
                if (a <= b and a <= c):
                    distances[t1][t2] = a + 1
                elif (b <= a and b <= c):
                    distances[t1][t2] = b + 1
                else:
                    distances[t1][t2] = c + 1

    distancia = distances[len(token1)][len(token2)]
    if distancia < 1:
        peso = 1
    if distancia == 1:
        peso = 0.8
    if distancia == 2:
        peso = 0.3
    if distancia > 2:
        peso = 0

    return peso


def recomendacao(id_receita):
    id_receita_amostra = id_receita
    tabela_pesos = pd.DataFrame(columns=['id_receita','titulo','ingrediente','quantidade','peso'])
    result_amostras = Relacionamento_ingrediente_receita.query.filter_by(id_receita=id_receita_amostra)
    tamanho_amostra = result_amostras.count()
    receitas = Receita.query.filter(Receita.id_receita!=id_receita_amostra).all()
    
    for result_amostra in result_amostras:
        
        for receita in receitas:
            peso_ingrediente = []
            contagem_itens = db.session.execute(f'''SELECT count(*) FROM myrecipe_producao.tb_relacionamento_ingrediente_receita  
                                                where id_receita = {receita.id_receita}''')
            for quantidade_itens in contagem_itens:
                quantidade_itens = quantidade_itens[0]
            
            receitas_procuradas = db.session.execute(f'''SELECT tir.*, tr.titulo FROM myrecipe_producao.tb_relacionamento_ingrediente_receita tir 
                                                inner join myrecipe_producao.tb_receita tr on tir.id_receita = tr.id_receita 
                                                where tir.id_receita != {id_receita_amostra} limit 150''')
            
            for ingrediente in receitas_procuradas:
                contido = float(result_amostra.qtde_ingrediente)/float(ingrediente.qtde_ingrediente)
                if contido > 1:
                    contido = 1
                peso_ingrediente.append(float(contido)*float(levenshteinDistanceDP(result_amostra.ingrediente, ingrediente.ingrediente)))
            
            dados_pesos = [receita.id_receita, f'{str(receita.titulo)}', result_amostra.ingrediente, quantidade_itens, max(peso_ingrediente)]
            tabela_pesos.loc[len(tabela_pesos)] = dados_pesos
            tabela_recomendacoes = tabela_pesos.groupby('id_receita').agg(soma_pesos=('peso','sum'),quantidade_itens=('quantidade','max'),titulo=('titulo','max')).reset_index()
            tabela_recomendacoes['percentual_total'] = (tabela_recomendacoes['soma_pesos'] / tabela_recomendacoes['quantidade_itens']) 
            tabela_recomendacoes = tabela_recomendacoes.sort_values(by='percentual_total',ascending=False).head(10)
    return (tabela_recomendacoes)

@app.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    usuario = Usuario.query.filter_by(id=current_user.id).first()
    return render_template('editar_perfil.html',usuario=usuario)   

@app.route('/preferencias', methods=['GET', 'POST'])
@login_required
def preferencias():   
    if request.method == 'POST':
        usuario = Usuario.query.filter_by(id=current_user.id).first()
        
        if 'vegetariano' in request.form:
            if request.form['vegetariano']=='on': usuario.vegetariano = 1
        else: usuario.vegetariano = 0                
        db.session.commit()
        if 'vegano' in request.form:
            if request.form['vegano']=='on': usuario.vegano = 1
        else: usuario.vegano = 0
        db.session.commit()
        if 'alerg_gluten' in request.form:
            if request.form['alerg_gluten']=='on': usuario.alerg_gluten = 1
        else: usuario.alerg_gluten = 0
        db.session.commit()
        if 'into_lactose' in request.form:
            if request.form['into_lactose']=='on': usuario.into_lactose = 1
        else: usuario.into_lactose = 0
        db.session.commit()    
    usuario = Usuario.query.filter_by(id=current_user.id).first()        
    return render_template('cadastrar_preferencias.html',usuario=usuario)

@app.route('/editar_receita/<int:id_receita>', methods=['GET', 'POST'])
@login_required
def editar_receita(id_receita):
    receita_edit = Receita.query.filter_by(id_receita=id_receita).first()
    ingredientes = db.session.execute(f'''SELECT *, row_number() OVER (ORDER BY id_sequencial) as contador FROM myrecipe_producao.tb_relacionamento_ingrediente_receita where id_receita = {id_receita}''')

    if request.method == 'POST':
        if 'quantidade' in str(request.form):
            titulo = request.form['titulo']
            vegetariana = receita_edit.vegetariana
            if 'vegetariana' in request.form:
                if request.form['vegetariana'] == 'on':
                    vegetariana = True
            vegana = receita_edit.vegana
            if 'vegana' in request.form:
                if request.form['vegana'] == 'on':
                    vegana = True
            semgluten = receita_edit.gluten
            if 'semgluten' in request.form:
                if request.form['semgluten'] == 'on':
                    semgluten = True
            semlactose = receita_edit.lactose
            if 'semlactose' in request.form:
                if request.form['semlactose'] == 'on':
                    semlactose = True
            saudavel = receita_edit.saudavel
            if 'saudavel' in request.form:
                if request.form['saudavel'] == 'on':
                    saudavel = True
            porcoes = receita_edit.porcoes
            if 'porcoes' in request.form:
                porcoes = request.form['porcoes']
            tempo_preparo = receita_edit.tempo_preparo
            if 'tempo' in request.form:
                tempo_preparo = request.form['tempo']
            tipo_refeicao = receita_edit.tipo_refeicao
            if 'tiporefeicao' in request.form:
                tipo_refeicao = request.form['tiporefeicao']
            instrucoes = receita_edit.instrucoes
            if 'editordata' in request.form:
                instrucoes = request.form['editordata']
            privada = receita_edit.privada
            if  'privada' in request.form:
                if request.form['privada'] == 'on':
                    privada = True

            receita = Receita(titulo,vegetariana,vegana,semgluten,semlactose,saudavel,porcoes,tempo_preparo,tipo_refeicao,instrucoes,privada,current_user.id)        
            db.session.add(receita)
            db.session.commit()
            receita_nova = db.session.execute('select max(id_receita) from myrecipe_producao.tb_receita')
            
            for receita in receita_nova:
                id_novo = receita[0]

            
                for i in range(75):
                    if 'quantidade'+str(i) in request.form:
                        quantidade = request.form['quantidade'+str(i)]
                        ingrediente = request.form['ingrediente'+str(i)]
                        unidademedida = request.form['unidademedida'+str(i)]
                        relaciona_ingrediente(id_novo, ingrediente, quantidade, unidademedida)            
            diretorio = r"/home/ubuntu/myrecipe_v2/static/uploads/recipes/"+str(id_novo)

            os.makedirs(diretorio)
            foto = request.files['foto']
            foto.save(os.path.join(diretorio, foto.filename))

            path_imagem = PathImagem(id_novo,foto.filename)
            db.session.add(path_imagem)
            db.session.commit()
        else:
            flash('Precisa ter pelo menos um ingrediente, tente novamente!')

        return redirect(url_for('homepage'))
    return render_template('editar_receita.html',receita=receita_edit,ingredientes=ingredientes) 


@app.route('/deletar_receita/<int:id_receita>', methods=['GET', 'POST'])
@login_required
def deletar_receita(id_receita):
    
    receita = Receita.query.filter_by(id_receita=id_receita).first()
    if current_user.id == receita.id_usuario:
        Relacionamento_ingrediente_receita.query.filter_by(id_receita=id_receita).delete()
        db.session.commit()
        Avaliacoes.query.filter_by(id_receita=id_receita).delete()
        db.session.commit()
        PathImagem.query.filter_by(id_receita=id_receita).delete()
        db.session.commit()
        Receitas_salvas.query.filter_by(id_receita=id_receita).delete()
        db.session.commit()
        Receita.query.filter_by(id_receita=id_receita).delete()
        db.session.commit()
    
    flash("Receita removida")
    return redirect(url_for('minhas_receitas'))


@app.route('/buscar_ingrediente', methods=['GET', 'POST'])
@login_required
def buscar_ingredientes():
    
    if request.method == 'POST':
        busca = []
        ingredientes_busca = {}
        tabela_pesos = pd.DataFrame(columns=['id_receita','titulo','ingrediente','quantidade','peso']) 
        for i in range(50):
                if 'quantidade'+str(i) in request.form:
                    ingredientes_busca = {'quantidade': request.form['quantidade'+str(i)],
                                        'ingrediente': request.form['ingrediente'+str(i)],
                                        'unidademedida': request.form['unidademedida'+str(i)]}
                    busca.append(ingredientes_busca.copy())
        receitas = Receita.query.all()        

        for ingrediente in busca:                
            for receita in receitas:
                contagem_itens = db.session.execute(f'''SELECT count(*) FROM myrecipe_producao.tb_relacionamento_ingrediente_receita  
                                                where id_receita = {receita.id_receita} ''')

                for quantidade_itens in contagem_itens:
                    quantidade_itens = quantidade_itens[0]
                peso = []
                pesos_ingredientes = {}
                ingredientes_receita = db.session.execute(f'''SELECT tir.*, tr.titulo FROM myrecipe_producao.tb_relacionamento_ingrediente_receita tir 
                                                        inner join myrecipe_producao.tb_receita tr on tir.id_receita = tr.id_receita 
                                                        where tir.id_receita = {receita.id_receita};''')
                                                                   
                for ingrediente_rec in ingredientes_receita:
                    peso.append((float(ingrediente['quantidade'])/float(ingrediente_rec.qtde_ingrediente))*float(levenshteinDistanceDP(ingrediente['ingrediente'], ingrediente_rec.ingrediente)))


                dados_pesos = [receita.id_receita, f'{str(receita.titulo)}', ingrediente['ingrediente'], quantidade_itens, max(peso)]
                tabela_pesos.loc[len(tabela_pesos)] = dados_pesos
        tabela_recomendacoes = tabela_pesos.groupby('id_receita').agg(soma_pesos=('peso','sum'),quantidade_itens=('quantidade','max'),titulo=('titulo','max')).reset_index()
        tabela_recomendacoes['percentual_total'] = (tabela_recomendacoes['soma_pesos'] / tabela_recomendacoes['quantidade_itens'])
        tabela_recomendacoes = tabela_recomendacoes.sort_values(by='percentual_total',ascending=False).head(50)
        paths = PathImagem.query.all()
    return render_template('resultados_busca_ingredientes.html',buscas=busca,recomendacoes=tabela_recomendacoes,paths=paths)
                    
@app.route('/buscar_titulo', methods=['GET', 'POST'])
@login_required
def buscar_titulo():
    if request.method == 'POST':
        titulo = request.form['titulo']
        receitas = db.session.execute(f'''SELECT * FROM myrecipe_producao.tb_receita
                                        where upper(titulo) like upper('%{titulo}%') limit 20;''')
        paths = PathImagem.query.all()
        return render_template('resultados_busca_titulo.html',receitas=receitas,paths=paths,titulo=titulo)

@app.route('/receita_sl/<int:id_receita>', methods=['GET', 'POST'])
def receita_sl(id_receita):    
    receita = Receita.query.filter_by(id_receita=id_receita).first()
    ingredientes = Relacionamento_ingrediente_receita.query.filter_by(id_receita=id_receita)
    receitas = Receita.query.all()
    medidas = Medidas.query.all()
    paths = PathImagem.query.all()
    for path in paths:
        path.path_imagem = (path.path_imagem.replace("/","#").split("#",-1))[-1] 
    
    return render_template('mostra_receita_sem_login.html',receita=receita,paths=paths,ingredientes=ingredientes,medidas=medidas,receitas=receitas)


app.run(debug=True)