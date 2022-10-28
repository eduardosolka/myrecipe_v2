from __init__ import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import datetime


@login_manager.user_loader
def get_user(user_id):
    return Usuario.query.filter_by(id=user_id).first()


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    nome = db.Column(db.String(86), nullable=False)
    email = db.Column(db.String(84), nullable=False, unique=True)
    senha = db.Column(db.String(128), nullable=False)
    nascimento = db.Column(db.String(20), nullable=False)
    cep = db.Column(db.String(15), nullable=False)
    foto = db.Column(db.String(100), nullable=False)
    vegetariano = db.Column(db.Boolean, nullable=False, default=False)
    vegano = db.Column(db.Boolean, nullable=False, default=False)
    alerg_gluten = db.Column(db.Boolean, nullable=False, default=False)
    into_lactose = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, nome, email, senha, nascimento, cep, foto, vegetariano,vegano,alerg_gluten,into_lactose):
        self.nome = nome
        self.email = email
        self.senha = generate_password_hash(senha)
        self.nascimento = nascimento
        self.cep = cep
        self.foto = foto
        self.vegetariano = vegetariano
        self.vegano = vegano
        self.alerg_gluten = alerg_gluten
        self.into_lactose = into_lactose

    def verify_password(self, senha):
        return check_password_hash(self.senha, senha)


class Receita(db.Model):
    __tablename__ = 'tb_receita'
    id_receita = db.Column(db.Integer, autoincrement=True, primary_key=True)
    titulo = db.Column(db.String(80), nullable=False)
    vegetariana = db.Column(db.Boolean, nullable=False, default=False)
    vegana = db.Column(db.Boolean, nullable=False, default=False)
    gluten = db.Column(db.Boolean, nullable=False, default=False)
    lactose = db.Column(db.Boolean, nullable=False, default=False)
    saudavel = db.Column(db.Boolean, nullable=False, default=False)
    porcoes = db.Column(db.Integer, nullable=False)
    tempo_preparo = db.Column(db.Integer, nullable=False)
    tipo_refeicao = db.Column(db.Integer, nullable=False)
    instrucoes = db.Column(db.Text(6500), nullable=False)
    privada = db.Column(db.Boolean, nullable=False, default=False)
    id_usuario = db.Column(db.Integer,db.ForeignKey('usuarios.id'),nullable=False)
    id_usuario_r = db.relationship('Usuario', primaryjoin='Usuario.id==Receita.id_usuario')

    def __init__(self, titulo, vegetariana, vegana, gluten, lactose, saudavel, porcoes, tempo_preparo, tipo_refeicao, instrucoes, privada, id_usuario):
        self.titulo = titulo
        self.vegetariana = vegetariana
        self.vegana = vegana
        self.gluten = gluten
        self.lactose = lactose
        self.saudavel = saudavel
        self.porcoes = porcoes
        self.tempo_preparo = tempo_preparo
        self.tipo_refeicao = tipo_refeicao
        self.instrucoes = instrucoes
        self.privada = privada
        self.id_usuario = id_usuario

class PathImagem(db.Model):
    __tablename__ = 'path_imagem_receita'
    id_receita = db.Column(db.Integer, db.ForeignKey('tb_receita.id_receita'),primary_key=True,nullable=False )
    id_receita_rt = db.relationship('Receita', foreign_keys=id_receita)
    path_imagem = db.Column(db.String(350), nullable=False)


    def __init__(self, id_receita, path_imagem):
        self.id_receita = id_receita
        self.path_imagem = path_imagem

class Ingrediente(db.Model):
    __tablename__ = 'tb_ingrediente'
    id_ingrediente = db.Column(db.Integer, autoincrement=True, primary_key=True)
    nome_singular = db.Column(db.String(150), nullable=False)
    nome_plural = db.Column(db.String(150), nullable=False)


    def __init__(self, nome_singular,nome_plural):
        self.nome_singular = nome_singular 
        self.nome_plural = nome_plural

class Relacionamento_ingrediente_receita(db.Model):
    __tablename__ = 'tb_relacionamento_ingrediente_receita'
    id_sequencial = db.Column(db.Integer, autoincrement=True, primary_key=True)
    id_receita = db.Column(db.Integer,db.ForeignKey('tb_receita.id_receita'),nullable=False)
    id_receita_rt = db.relationship('Receita', foreign_keys=id_receita)
    ingrediente = db.Column(db.String(150), nullable=False)
    qtde_ingrediente = db.Column(db.Integer, nullable=False)
    id_medida = db.Column(db.Integer, db.ForeignKey('tb_medidas.id_medida'),nullable=False)
    id_medida_rt = db.relationship('Medidas', foreign_keys=id_medida)


    def __init__(self, id_receita,ingrediente,qtde_ingrediente,id_medida):
        self.id_receita = id_receita 
        self.ingrediente = ingrediente
        self.qtde_ingrediente = qtde_ingrediente
        self.id_medida = id_medida

class Medidas(db.Model):
    __tablename__ = 'tb_medidas'
    id_medida = db.Column(db.Integer, autoincrement=True, primary_key=True)
    medida_singular = db.Column(db.String(100), nullable=False)
    medida_plural = db.Column(db.String(100), nullable=False)


    def __init__(self, medida_singular,medida_plural):
        self.medida_singular = medida_singular 
        self.medida_plural = medida_plural

class Receitas_salvas(db.Model):
    __tablename__ = 'tb_receitas_salvas'
    id_receita_salva = db.Column(db.Integer, autoincrement=True, primary_key=True)
    id_receita = db.Column(db.Integer,db.ForeignKey('tb_receita.id_receita'),nullable=False)
    id_receita_rt = db.relationship('Receita', foreign_keys=id_receita)
    id_usuario = db.Column(db.Integer,db.ForeignKey('usuarios.id'),nullable=False)
    id_usuario_rt = db.relationship('Usuario', primaryjoin='Usuario.id==Receitas_salvas.id_usuario')
    hora = db.Column(db.DateTime,default=datetime.datetime.utcnow)

    def __init__(self, id_receita,id_usuario,hora):
        self.id_receita = id_receita 
        self.id_usuario = id_usuario
        self.hora = hora
        
class Avaliacoes(db.Model):
    __tablename__ = 'tb_avaliacoes'
    id_avaliacao = db.Column(db.Integer, autoincrement=True, primary_key=True)
    id_receita = db.Column(db.Integer,db.ForeignKey('tb_receita.id_receita'),nullable=False)
    id_receita_av = db.relationship('Receita', foreign_keys=id_receita)
    id_usuario = db.Column(db.Integer,db.ForeignKey('usuarios.id'),nullable=False)
    id_usuario_av = db.relationship('Usuario', primaryjoin='Usuario.id==Avaliacoes.id_usuario')
    nota = db.Column(db.Integer,nullable=False)

    def __init__(self, id_receita,id_usuario,nota):
        self.id_receita = id_receita 
        self.id_usuario = id_usuario
        self.nota = nota
        