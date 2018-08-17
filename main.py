#!/usr/bin/env python3
#-*- coding: utf-8 -*-
"""
    @author: Hiago dos Santos (hiagop22@gmail.com)

    Múdulo responsável por obter a resolução da tela e chamar o módulo responsável
    pela interface gráfica
"""

from subprocess import check_call
        
def configura_resolucao():
    """Escreve a resolução da tela no arquivo resolution.py"""
    arquivo = 'resolution.py'
    comando = 'xdpyinfo  | grep \'dimensions:\''
    cmd = comando + '> ' + arquivo # Obtem a resolução da tela pelo terminal para que se adeque em várias telas
    check_call(cmd, shell=True)
    try:
        with open(arquivo) as p:
            resolution = 'RESOLUTION = ' + '\'%s\''%p.readlines()[0].split()[1]
        with open(arquivo, 'w') as p:
            p.write(resolution) 
    except Exception as e:
        raise e                  # É necessário que seja feito algo caso dê errado em se obter a resolução da tela
                                 # Sendo as sugestões bem vindas, principalmente nessa parte do projeto ;)

def chama_buscador():
    '''Chama o programa com a interface gráfica'''
    cmd = 'python3 buscador.py'
    check_call(cmd, shell=True)

configura_resolucao()
chama_buscador()