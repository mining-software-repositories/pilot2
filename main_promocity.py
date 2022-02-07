import dao
import utility
import datetime
from pydriller import Repository

path_repository = 'promocity'
repositorio_src = path_repository + '/' + 'src'
dir_src_java = 'src/main/java'

def load_db(path_repository, create=False):
    ## 1. Carrega o banco de dados e cria as estruturas das tabelas
    print(f'Configura e carrega o banco {dao.data_base}...')
    db_session = dao.create_session()
    print(f'Banco {dao.data_base} carregado com sucesso! \n')

    # 2. Carrega os manipuladores de CommitComplete e FileComplete
    commitsCompleteCollection = dao.CommitsCompleteCollection(session=db_session)
    filesCompleteCollection = dao.FilesCompleteCollection(session = db_session)

    if create: 
        dao.drop_tables()
        dao.create_tables()

        # 3. É preciso percorrer todos os commits, seus arquivos modificados e salva-los no Banco
        print('Percorrendo todos os commits...')
        t1 = datetime.datetime.now()
        print(t1)

        for commit in Repository(path_repository).traverse_commits():    
            c = dao.CommitComplete(name = commit.hash, 
                hash = commit.hash, 
                msg = commit.msg,
                author = utility.concat_str(commit.author.name,commit.author.email), 
                committer = utility.concat_str(commit.committer.name,commit.committer.email), 
                author_date = commit.author_date,
                author_timezone = commit.author_timezone,
                committer_date = commit.committer_date,
                committer_timezone = commit.committer_timezone,
                branches = utility.convert_list_to_str(commit.branches),
                in_main_branch = commit.in_main_branch,
                merge = commit.merge,
                modified_files = utility.convert_modifield_list_to_str(commit.modified_files),
                parents = utility.convert_list_to_str(commit.parents),
                project_name = commit.project_name,
                project_path = commit.project_path,
                deletions = commit.deletions,
                insertions = commit.insertions,
                lines = commit.lines,
                files = commit.files,
                dmm_unit_size = commit.dmm_unit_size,
                dmm_unit_complexity = commit.dmm_unit_complexity,
                dmm_unit_interfacing = commit.dmm_unit_interfacing)
            
            commitsCompleteCollection.insert_commit(c)

            for m in commit.modified_files:
                commit_by_hash = commitsCompleteCollection.query_commit_by_hash(commit.hash)
                if m is not None and  m.filename is not None:
                    if '.java' in m.filename:
                        is_java = True
                    else:
                        is_java = False
                    mf = dao.FileComplete(
                        name = m.filename,
                        hash = commit.hash,
                        is_java = is_java,
                        old_path = m.old_path,
                        new_path = m.new_path,
                        filename = m.filename,
                        change_type = m.change_type.name,
                        diff = str(m.diff),
                        diff_parsed = utility.convert_dictionary_to_str(m.diff_parsed),
                        added_lines = m.added_lines,
                        deleted_lines = m.deleted_lines,
                        source_code = str(m.source_code),
                        source_code_before = str(m.source_code_before),
                        methods = utility.convert_list_to_str(m.methods),
                        methods_before = utility.convert_list_to_str(m.methods_before),
                        changed_methods = utility.convert_list_to_str(m.changed_methods),
                        nloc = m.nloc,
                        complexity = m.complexity,
                        token_count = m.token_count, 
                        commit_id = commit_by_hash.id
                    )
                    # salva o arquivo correte
                    filesCompleteCollection.insert_file(mf)

        t2 = datetime.datetime.now()
        print(t2)
        print(f'Analise concluida em: {t2 -t1}')

    return filesCompleteCollection, commitsCompleteCollection

# 1. Carrega o banco de dados
filesCompleteCollection, commitsCompleteCollection = load_db(path_repository, create=False)

# 2. Consulta Commits e arquivos
# 2.1. Lista os commits entre duas tags
commits_tag_promocity_100_122 = utility.list_commits_between_tags(from_tag='promocity-v1.0.0', to_tag='promocity-v1.2.2', my_repository=path_repository)
list_commits_tag_promocity_100_122 = [commit.hash for commit in commits_tag_promocity_100_122]

# 2.2. Gera um dicionario commit -> lista de arquivos do commit
dicionario_commits_arquivos = {}
for hash_commit in list_commits_tag_promocity_100_122:
    commit = commitsCompleteCollection.query_commit_by_hash(hash_commit)
    if commit is not None and commit.modified_files is not None:
      dicionario_commits_arquivos[hash_commit] = commit.modified_files
    else:
      dicionario_commits_arquivos[hash_commit] = ''
print(dicionario_commits_arquivos)

print('')
# 2.3. Gera um dicionario file -> lista de commits
dicionario_file_commits = {}
lista_unique_files = filesCompleteCollection.query_unique_files()
for filename in lista_unique_files:
    dicionario_file_commits[filename] = filesCompleteCollection.query_commits_from_file_name(filename)
print(dicionario_file_commits)

t1 = datetime.datetime.now()
print(t1)

# 3. Gera uma lista contendo todos os arquivos e diretorios do repositorio src
files_and_directories = utility.create_file_from_bash_tree(repositorio_src, "arquivosediretorios.txt")
all_files_and_directories = utility.convert_file_in_list(files_and_directories)

# 4. Gera uma lista contendo todos os diretorios do repositorio src
directories = utility.create_file_from_bash_tree(repositorio_src, "diretorios.txt", all_files_directories=False)
all_directories = utility.convert_file_in_list(directories)

# 5. Lista de diretorios do diretório src/main/java do repositorio
all_directories_from_src = [ each for each in all_directories if (dir_src_java in each) ]

# 6 Lista todos os diretorios que estao no dir_src_java
all_directories_and_java_files_from_src = [each for each in all_files_and_directories if (dir_src_java in each)]

# 7. Lista todos os arquivos .java do diretório src/main/java do repositório
all_java_files_from_src = [each for each in all_files_and_directories if ((dir_src_java in each) and ('.java' in each))]

print(f'Lista todos os arquivos .java do {path_repository} no diretorio {dir_src_java}')
for each in all_java_files_from_src:
    print(each)
print('')

# 8. Lista todos os arquivos .java com suas LoCs
file_loc_files = utility.create_loc_file_from_bash_tree(repositorio_src, 'locarquivosjava.txt')
list_locs_files = utility.generate_list_locs_files(path_repository, file_loc_files)
list_locs_java_files = [each for each in list_locs_files if (dir_src_java in each[1]) ]

print(f'Lista todos os arquivos .java e suas LoCs do {path_repository} no diretorio {dir_src_java}')
for each in list_locs_java_files:
    print(each)
print('')

t2 = datetime.datetime.now()
print(t2)
print(f'Analise dos LoCs dos .java concluida em: {t2 -t1}')

# 8. Dado um arquivo mostra a quantidade total de linhas alteradas dentro da faixa de commits analisada
promotion = filesCompleteCollection.query_all_modifications_by_name('Promotion.java')
print(f'Quantidade de linhas totais modificadas de Promotion.java: { promotion }')

# 9. Dado um arquivo mostra a frequencia de commits dentro da faixa de commits analisada
print(utility.sort_dictionary_by_value( utility.create_dicionario_fc_filename(dicionario_file_commits)) )