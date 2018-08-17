#!/usr/bin/env python3
#-*- coding: utf-8 -*-
"""
    @author: Hiago dos Santos (hiagop22@gmail.com)
    Tela de login com opção de entrar e de criar novo usuário, sendo que
    os usuários cadastrados são armazenados em um arquivo database.
"""
import requests
from sys import exit
from constantes import *
import re

class Nivel(object):
	def __init__(self):
		self.graduacao = 'graduacao'
		self.posgraduacao = 'posgraduacao'

class Disciplina(object):
    def __init__(self):
        self.nome = ''
        self.departamento = ''
        self.codigo = ''
        self.nivel = ''
        self.vigencia = ''
        self.ementa = ''
        self.programa = ''
        self.bibliografia = ''
        self.pre_requisitos = [] #  Lista que contém as sublistas (de pré-requisitos), sendo
                                 #  que cada sublista é uma forma diferente de se alcançar a 
                                 #  disciplina desejada, por exemplo:
                                 #  [[opção 1 de cursar disciplina], [opcão 2 de cursar a displina]]
                                 #  Logo, neste exemplo você pode cursar a disciplina usando as matérias da sublista
                                 #  1 ou da sublista 2.
        self.erro = '' # Caso haja algum erro ao baixar a disciplina, esse atributo será mudado 

def baixar_pagina(endereco):
    '''Recebe um endereço e retorna duas strings. Por exemplo str1 e str2, sendo que :
        -> Caso dê tudo certo, str1 será uma string vazia e str2 será a string com o código html da página;
        -> Caso dê errado, str1 será uma string informando o erro e str2 será uma string vazia, ou então, caso
           surja um erro não conhecido str1 será "Erro desconhecido..." e str2 será uma string vazia '''
    try:
        pagina = requests.get(endereco, timeout = 2)
        return '', pagina.content.decode()
    except requests.exceptions.RequestException as e:
        return e, ''
    except:
        'Erro desconhecido...', ''

def retorna_parte_desejada(parte_desejada, pagina):
    #Ver https://pt.slideshare.net/bismarckjunior/manual-simples-expressoes-regulares-python?from_action=save
    opcao = re.compile('%s' % parte_desejada, re.S) 
    inicio = opcao.findall(pagina)  # Retorna uma lista com a ocorrência encontrada, ou uma lista vazia caso
                                    # não ache nada, logo o if é necessário para não se tentar acessar uma 
                                    # uma lista vazia e acabar gerando erro
    if inicio != []:
        inicio = re.sub(r"\r<br />", "\n", inicio[0]) # Substitui todos os '\r<br />' (<Enter> em linguagem html)
                                                      # por '\n' (<Enter> em linguagem python)
        return inicio

    return ''

def junta_listas(base, receberao_base):
    '''Insere o conteúdo da lista base, em cada sublista da lista receberao_base'''
    '''
        Entradas:
            a = [('a0'),('b0')]
            b = [[('a1'),('a2')],[('b1'),('b2')]]
        Após a função ser executada....Então:
            a = [('a0'),('b0')] ** Não muda **
            b = [[('a1'), ('a2'), ('a0'), ('b0')], [('b1'), ('b2'), ('a0'), ('b0')]] ** Esse sim, muda **
        
        Entradas:
            a = [[('a0'),('b0')], [('c0')]]
            b = [[('a1'),('a2')],[('b1'),('b2')]]
        Após a função ser executada....Então:
            a = [('a0'),('b0')] ** Não muda **
            [['a1', 'a2', 'a0', 'b0', 'c0'], ['b1', 'b2', 'a0', 'b0', 'c0']] ** Esse sim, muda ** 
    '''
    if not type(base[0]) is list:
        for x in range(len(receberao_base)):
            receberao_base[x] += base
    
    # Pode nãoser importante, mas por enquanto é melhor deixar
    else:
        for i in base:
            junta_listas(i, receberao_base)

def acha_prereq(pre_req, disc_atual, nivel):
    '''Acha recursivamente os pré-requisitos de disciplinas'''
    #print(disc_atual)
    #print('>>Pré-req')
    #print(pre_req)
    #print('\n')
    disc_ou = pre_req.split(OU_PRE_REQ)
    if disc_ou == []:
        return []

    # Variáveis auxiliares #
    aux_l = []
    cod_aux = ''
    disc_aux = ''
    erro = ''
    teste = []
    ex_list = []
    outra_lista = []
    tentativa = []

    # Formata os pré-requisitos de tal forma que cada lista dentro da lista é uma forma diferente de se cursar a disciplina 
    for x in range(len(disc_ou)):
        aux = disc_ou[x].split(E_PRE_REQ)
        aux_l.append([])
        for i in range(len(aux)):
            cod_aux = retorna_parte_desejada(CODIGO_PRE_REQ, aux[i])
            disc_aux = retorna_parte_desejada(NOME_DISC_PRE_REQ, aux[i])
            if cod_aux != '':
                aux_l[x].append(('%s\n%s'%(disc_aux, cod_aux), disc_atual))

    if aux_l == [[]]:
        aux_l.clear()

    # Após ter gerado uma lista com os pré-requisitos da disciplina recebida, busca cada pré-requisito da disciplina que
    # existe na lista
    for x in aux_l:
        tentativa.clear()
        tentativa.append([])
        w = 0
        for j in x:
            val = j[0].find('\n') + 1   # Achando o '\n', pois é ele quem divide a disciplina do código dela
            cod = j[0][val:]            # Após ter achado o '\n', pegamos o código da disciplina
            endereco = 'https://matriculaweb.unb.br/%s/disciplina.aspx?cod=%s' % (nivel, cod) # Baixamos a página
            erro, pagina = baixar_pagina(endereco) # A variável erro é necessária pois será retornada uma tupla
            pre_req = retorna_parte_desejada(PRE_REQUISITOS, pagina) # Obtemos uma string que contem os pré-requisitos
            
            # Otemos o nome da disciplina que estamos e o código dela
            if pre_req != '':
                disc_atual = j[0] #
                pagina = '' # Limpamos a string que tinhamos a página contida
                
                teste = acha_prereq(pre_req, disc_atual, nivel) # Recebe a lista de pré-requisitos
                
################## Início da parte que está precisando de correção de erros ###########################
#O problema é que está sendo recebido o pré-requisito de uma disciplina e ela já está sendo juntada logo 
#   com toda a lista a qual ela pertence e adicionada a uma lista, e depois é recebido um outro pré-requisito
#   de uma outra disciplina, mas esse novo pré-requisito mesmo não pertencendo á um ou é juntado com a lista 
#   de cadeias que veio antes dele, mas que não possui os outros pré-requisitos adicionado anteriormente...'''

                if teste != []: # Verifica se possui algum pré-requisito
                    for s in teste:
                        s.append(j)
                        tentativa[w].append(s)
                        w += 1
                        
        #if tentativa != []: 
            #combina(tentativa, outra_lista)

    
################## Fim da parte que está precisando de correção de erros ###########################

    if outra_lista != []:
        return outra_lista
    else:
        return aux_l


def encontra_disc(cod, nivel):
    disc = Disciplina()    
    endereco = 'https://matriculaweb.unb.br/%s/disciplina.aspx?cod=%s' % (nivel, cod)
    disc.erro, pagina = baixar_pagina(endereco) # Caso tenha dado tudo certo a variável página conterá uma string com o 
                                                # o código html da página e disc.erro será uma string vazia
    
    if disc.erro != '': # Verifica se houve algum erro
        return disc

    if pagina == '' or pagina == TEMPO_EXCEDIDO: # Caso não consiga baixar a página, vai retornar '' na variável página
        disc.erro = TEMPO_EXCEDIDO
        return disc
    
    # Algumas disciciplinas podem ter alguns atributos e outros não, sendo assim vários blocos 
    # condicionais para se fazer essa validação...
    nome = retorna_parte_desejada(NOME_DISC, pagina)
    if nome == '' : # Se o nome da disciplina não existe, possivelmente ela não existe
        disc.erro = DISCIPLINA_NAO_ENCONTRADA
        return disc
    disc.nome = nome + '\n'

    codigo = retorna_parte_desejada(CODIGO, pagina)
    if codigo != '':
        disc.codigo = codigo + '\n'

    departamento = retorna_parte_desejada(DEPARTAMENTO, pagina)
    if departamento != '':
        disc.departamento = departamento + '\n'
    
    vigencia = retorna_parte_desejada(VIGENCIA, pagina)
    if vigencia != '':
        disc.vigencia = vigencia + '\n'

    ementa = retorna_parte_desejada(EMENTA, pagina)
    if ementa != '':
        disc.ementa = ementa + '\n'

    pre_requisitos = retorna_parte_desejada(PRE_REQUISITOS, pagina)
    if pre_requisitos != 'Disciplina sem pré-requisitos':
        disc.pre_requisitos = acha_prereq(pre_requisitos, '%s\n%s'%(nome, codigo), nivel)
        #print(disc.pre_requisitos)
    else:
        disc.pre_requisitos = [' ']

    programa = retorna_parte_desejada(PROGRAMA, pagina)
    if programa != '':
        disc.programa = programa + '\n'

    bibliografia = retorna_parte_desejada(BIBLIOGRAFIA, pagina)
    if bibliografia != '':
        disc.bibliografia = bibliografia + '\n'

    nivel = retorna_parte_desejada(NIVEL, pagina)
    if nivel != '':
        disc.nivel = nivel + '\n'

    return disc

#encontra_disc('166014', 'graduacao')