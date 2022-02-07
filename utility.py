import json
from pydriller import Repository
import subprocess
import os
from pathlib import Path
import plotly.graph_objects as go

def concat_str(str1, str2):
    temp = str1 + ',' + str2
    return temp

def convert_list_to_str(lista):
    temp = ''
    if len(lista) > 0:
        temp = ','.join( str(v) for v in lista)
    return temp

def convert_modifield_list_to_str(lista):
    list_aux = []
    for each in lista:
        list_aux.append(each.filename)
    str = convert_list_to_str(list_aux)
    return str

def convert_dictionary_to_str(dictionary):
    temp = ''
    if len(dictionary) > 0:
        temp = str(json.dumps(dictionary))
    return temp

def list_commits_between_tags(from_tag, to_tag, my_repository):
    list_temp = []
    for commit in Repository(my_repository, from_tag=from_tag, to_tag=to_tag).traverse_commits():
        list_temp.append(commit)
    return list_temp

# Immprime n linhas da lista fornecida
def print_n(n, list_to_print):
  """
  Print n lines of a list
  @param: int n: amout of lines to print
  @param: list list_to_print: list to print
  @return n lines to print
  """
  i = 1
  for each in list_to_print:
    if i < n:
      print(each)
      i +=1

# Ordena um dicionario por value
def sort_dictionary_by_value(x, reverse=True):
  """
  Sort a dictionary by value 
  @param: dictionary x: a dictionary to sort
  @param: bool reverse: True sort decreasing value from max to min
  @return a sorted dictionary
  """
  return sorted(x.items(), key=lambda kv: kv[1], reverse=reverse)

def run_bash_command(bashCommand):
  """"
  Executa um comando bash
  @param: str bashCommand: comando bash
  @return int result: 0 ok 
  """
  result = 0
  try: 
    subprocess.run(bashCommand, shell=True, executable='/bin/bash')
  except subprocess.CalledProcessError as e:
      print(f'Returned code: {e.returncode}, output: {e.output}')
      result = e.returncode
  return result

def create_file_from_bash_tree(repository_src, filename, all_files_directories=True):
  """
  Cria um arquivo texto a partir da execucao de um comando bash
  @param: str repository_src: src do repositorio que sera analisado
  @param: str all_files_directories: True para gerar todos os arquivos e diretorios
  @param: str filename: nome do arquivo de entrada
  :raises ExceptionType:Exception caso aconteca algum erro
  @return str filename: arquivo criado com todos os arquivos e diretorios e seus paths completos
  """
  try: 
    if all_files_directories: 
      bashCommand = f"tree {repository_src} -i -f > {filename}"
    else: 
      bashCommand = f"tree {repository_src} -d -i -f > {filename}"
    if run_bash_command(bashCommand) == 0:
        print(f'File {filename} created successfully!')
    else:
        raise Exception(f"Erro while try to create the file {filename}")
  except Exception as ex:
    print(f'Erro: {ex}')
  return filename

# Dado um arquivo texto, gera uma lista contendo cada linha do arquivo como cada item da lista
def convert_file_in_list(filename, bash_tree=True):
    """
    Convert as linhas de um arquivo texto em uma lista com as linhas do arquivo
    Retorna a lista das linhas do arquivo
    @param: str filename: nome do arquivo de entrada
    @param: bool bash_tree: True se foi gerado por um comando bash tree
    @return list list_of_lines
    :raises ExceptionType:Exception caso aconteca algum erro
    """
    list_of_lines = []
    try:
        with open(filename) as file:
            for line in file:
                line = line.rstrip("\n")
                list_of_lines.append(line)
            if bash_tree:
                # Remove os dois ultimos elementos no caso de um arquivo gerado pelo comando tree
                del list_of_lines[-1]
                del list_of_lines[-1]
    except Exception as ex:
        print(f'Erro: {ex}')
    return list_of_lines

# Cria um arquivo texto onde cada linha tem o Loc e o arquivo fonte do repositorio
def create_loc_file_from_bash_tree(repository_src, filename):
  """
  Cria um arquivo texto a partir da execucao de um comando bash tree
  @param: str repository_src: src do repositorio que sera analisado
  @param: str filename: nome do arquivo de entrada
  :raises ExceptionType:Exception caso aconteca algum erro
  """
  try: 
    bashCommand = f"find {repository_src} -name *.java | xargs wc -l > {filename}"
    if run_bash_command(bashCommand) == 0:
        print(f'File {filename} created successfully!')
    else:
        raise Exception(f'Erro while try to create the file {filename}')
  except Exception as ex:
    print(f'Erro: {ex}')
  return filename

# Lista com LoCs de cada arquivo: (loc, arquivo)
def generate_list_locs_files(repository, filename):
    """
    Cria uma lista de loc por arquivo a partir de um arquivo de locs e files
    @param: str repository: src do repositorio que sera analisado
    @param: str filename: nome do arquivo de entrada
    """
    list_locs_files = []
    try:
        with open(filename) as file:
            for line in file:
                line = line.strip()
                if repository in line:
                    line = line.split(' ')
                    elemento = line[0], line[1]
                    list_locs_files.append(elemento)
    except Exception as ex:
        print(f'Erro: {ex}')
    return list_locs_files

# dado um arquivo fonte retorna seu LoC correspondente
def search_loc_of_file(file_name, list):
  """
  Para cada arquivo procura sua LOC (Lines of Code)
  @param: str file_name: nome do arquivo que sera procurado na lista de arquivos fonte com suas locs
  @param: str list: lista contendo todos os arquivos fonte do projeto e suas respectivas LoCs
  @return int Loc: do arquivo dado
  """
  for each in list:
    if file_name in each[1]:
      return int(each[0])

# Dicionario com o LoC de cada arquivo
def create_dicionario_loc_filename(lista):
    dicionario = {}
    for item in lista:
        loc = item[0]
        name = item[1].split('/')[-1]
        dicionario[name] = loc
    return dicionario

# Dicionario com a frequencia de commits de cada arquivo
def create_dicionario_fc_filename(dicionario_fc):
    dicionario = {}
    for k, v in dicionario_fc.items():
      dicionario[k] = len(v)
    return dicionario