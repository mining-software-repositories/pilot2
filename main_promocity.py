import dao
import utility
import datetime
from pydriller import Repository

path_repository = 'promocity'

## 1. Carrega o banco de dados e cria as estruturas das tabelas
print('')
print(f'Configura e carrega o banco {dao.data_base}...')
db_session = dao.create_session()
dao.drop_tables()
dao.create_tables()
print(f'Banco {dao.data_base} carregado com sucesso! \n')

# 2. Carrega os manipuladores de CommitComplete e FileComplete
commitsCompleteCollection = dao.CommitsCompleteCollection(session=db_session)
filesCompleteCollection = dao.FilesCompleteCollection(session = db_session)

# 3. É preciso percorrer todos os commits, seus arquivos modificados e salva-los no Banco
print('Percorrendo todos os commits...')
t1 = datetime.datetime.now()
print(t1)
commits = []

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
    commits.append(commit)

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