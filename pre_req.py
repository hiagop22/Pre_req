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

def baixar_pagina(endereco: str):
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
    # print("inicio ::: {}".format(inicio))
    if inicio != []:
        inicio = re.sub(r"\r<br />", "\n", inicio[0]) # Substitui todos os '\r<br />' (<Enter> em linguagem html)
                                                      # por '\n' (<Enter> em linguagem python)
        return inicio

    return ''

def junta_listas(base, receberao_base):
    print("base :: {},,, receberao_base ::: {}".format(base, receberao_base))
    """Insere o conteúdo da lista base, em cada sublista da lista receberao_base"""
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

def acha_prereq(pre_req: str, disc_atual: str, nivel: str):
    """Acha recursivamente os pré-requisitos de disciplinas"""
    print("pre_req IS :: {}".format(pre_req))
    print("disc_atual IS :: {}".format(disc_atual))
    # disc_ou = pre_req.split(OU_PRE_REQ)
    disc_ou = pre_req.split(OU_PRE_REQ)
    if not disc_ou:
        return []
    list_list_ands = []

    # Formata os pré-requisitos de tal forma que cada lista dentro da
    # lista é uma forma diferente de se cursar a disciplina 
    for idx, val in enumerate(disc_ou):
        aux = val.split(E_PRE_REQ)
        list_list_ands.append([])
        for i in range(len(aux)):
            cod_aux = retorna_parte_desejada(CODIGO_PRE_REQ, aux[i])
            disc_aux = retorna_parte_desejada(NOME_DISC_PRE_REQ, aux[i])
            if cod_aux :
                list_list_ands[idx].append( ( '%s\n%s'%(disc_aux, cod_aux) , disc_atual ) )
            # print("list_list_ands[{}] == {}".format(x,list_list_ands[x]))
    # if list_list_ands == [[]]:
    #     list_list_ands = []
    print("last list_list_ands ==> ", list_list_ands)

    # Após ter gerado uma lista com os pré-requisitos da disciplina recebida, busca cada pré-requisito da disciplina que
    # existe na lista
    tentativa = []
    for lista_ands in list_list_ands:
        for pre_req_direto in lista_ands:
            val = pre_req_direto[0].find('\n') + 1   # Achando o '\n', pois é ele quem divide a disciplina do código dela
            cod = pre_req_direto[0][val:]            # Após ter achado o '\n', pegamos o código da disciplina
            endereco = 'https://matriculaweb.unb.br/%s/disciplina.aspx?cod=%s' % (nivel, cod) # Baixamos a página
            erro, pagina = baixar_pagina(endereco) # A variável erro é necessária pois será retornada uma tupla
            pre_req = retorna_parte_desejada(PRE_REQUISITOS, pagina) # Obtemos uma string que contem os pré-requisitos
            
            # Otemos o nome da disciplina que estamos e o código dela
            if pre_req:
                print("\npre_req_direto :===> ", pre_req_direto, '\n')
                disc_atual = pre_req_direto[0] #
                pagina = '' # Limpamos a string que tinhamos a página contida
                
                req_ind = acha_prereq(pre_req, disc_atual, nivel) # Recebe a lista de pré-requisitos
                if req_ind:                    
                    # for i in req_ind:
                    #     i.append(pre_req_direto)
                    req_ind = [i+[pre_req_direto] for i in req_ind]
                    tentativa.extend(req_ind)
                else:                    
                    tentativa.append([pre_req_direto])                    
                print("req_ind ehhh ==> \n{}\n".format(req_ind))
        print("tentativa :: {}".format(tentativa))
    
    retornar = tentativa if tentativa else list_list_ands
    print('pre_req.py::acha_prereq ===> acha_prereq will return ===> {}'.format(retornar))
    return retornar

"""
    Recebe codigo de disciplina e string informando se é da graduação ou pós.
    Retorna 
"""
def encontra_disc(cod: int, nivel: str):
    print("cod :: {}".format(cod))
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
    if codigo:
        disc.codigo = codigo + '\n'

    departamento = retorna_parte_desejada(DEPARTAMENTO, pagina)
    if departamento:
        disc.departamento = departamento + '\n'
    
    vigencia = retorna_parte_desejada(VIGENCIA, pagina)
    if vigencia:
        disc.vigencia = vigencia + '\n'

    ementa = retorna_parte_desejada(EMENTA, pagina)
    if ementa :
        disc.ementa = ementa + '\n'

    pre_requisitos = retorna_parte_desejada(PRE_REQUISITOS, pagina)
    if pre_requisitos != 'Disciplina sem pré-requisitos':
        disc.pre_requisitos = acha_prereq(pre_requisitos, '%s\n%s'%(nome, codigo), nivel)
        print('MARKUP :: ', disc.pre_requisitos)
    else:
        disc.pre_requisitos = [' ']

    programa = retorna_parte_desejada(PROGRAMA, pagina)
    if programa:
        disc.programa = programa + '\n'

    bibliografia = retorna_parte_desejada(BIBLIOGRAFIA, pagina)
    if bibliografia:
        disc.bibliografia = bibliografia + '\n'

    nivel = retorna_parte_desejada(NIVEL, pagina)
    if nivel :
        disc.nivel = nivel + '\n'

    return disc

#encontra_disc('166014', 'graduacao')