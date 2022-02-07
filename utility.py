import json
from pydriller import Repository

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