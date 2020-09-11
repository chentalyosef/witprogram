import filecmp
import os
import random
import shutil
import sys
import time

import matplotlib.pyplot as plt
import networkx as nx

#To go up in the directory tree
# Method 1
#x = os.listdir('..')
# Method 2
#x= os.listdir('/')

def init():
    root_directory = os.getcwd()
    path_1 = os.path.join(root_directory, '.wit')
    root_list = [root_directory, path_1, path_1]
    name_list = ['.wit', 'images', 'staging_area']
    i = 0
    while i < 3:
        path = os.path.join(root_list[i], name_list[i])
        try:
            os.mkdir(path)
        except FileExistsError:
            print(f'File {path} already exists.')
        i += 1
    with open(os.path.join(path_1, 'activated.txt'), 'w') as activate_text:
        activate_text.write('master')
    return root_directory

#############os.chdir("..") #Go up one directory from working directory
#############o = [os.path.join(d,o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))] # Gets all directories in the folder as a tuple
########Then you can search the tuple for the directory you want and open the file in that directory:

#for item in o:
#    if os.path.exists(item + '\\testfile.txt'):
#    file = item + '\\testfile.txt'
####################Then you can do stuf with the full file path 'file'


def add(path, root_directory):
    current_directory = os.getcwd()
    if '.wit' not in os.listdir(root_directory):
        raise FileExistsError('File .wit does not exist in repository.')
    destination = os.path.join(root_directory, '.wit', 'staging_area')
    if os.path.isfile(path):
        if root_directory == current_directory:  # if it is a file in the root directory add file to staging area.
            shutil.copy(path, destination)
        else:  # if the file is not in the root directory.
            path_directory = os.path.join(current_directory, path)
            path_directory_without_root = path_directory.replace(root_directory, '')
            path_parts = path_directory_without_root.split(os.sep)  # separate path_directory.
            for part in path_parts:  # check if folder exists in root directory staging area.
                destination_files = os.listdir(destination)
                if part not in destination_files:
                    if part != path_parts[-1]:  # make sure file isn't opened as directory.
                        os.mkdir(os.path.join(destination, part))
                    if part == path_parts[-1]:  # the file is added at the end.
                        shutil.copy(os.path.join(destination, part), destination)
                destination = os.path.join(destination, part)  # if exists: go in, if not: create it and go in.
    elif os.path.isdir(path):  # if folder, add all folders above and files in folder to staging area.
        path_directory = os.path.join(current_directory, path)
        path_directory_without_root = path_directory.replace(root_directory, '')
        path_parts = path_directory_without_root.split(os.sep)
        for part in path_parts:
            destination_files = os.listdir(destination)
            if part not in destination_files:
                os.mkdir(os.path.join(destination, part))
            destination = os.path.join(destination, part)
        path_files = os.listdir(path)  # finally, add all the files from the folder.
        for path_file in path_files:
            shutil.copy(os.path.join(destination, path_file), destination)



def commit(message, root_directory):
    if '.wit' not in os.listdir(root_directory):
        raise FileExistsError('File .wit does not exist in repository.')
    numbers_letters = list(range(10)) + [chr(i) for i in range(97, 103)]
    temp_name = random.choices(numbers_letters, k=40)
    second_temp_name = [str(part) for part in temp_name]
    commit_id = "".join(second_temp_name)
    name_folder = os.path.join(root_directory, 'wit', 'images', commit_id)
    try:
        os.mkdir(name_folder)
    except FileExistsError:
        print(f'File {name_folder} already exists.')
    name_file = os.path.join(root_directory, 'wit', 'images', f'{commit_id}.txt')
    a_file = os.path.join(root_directory, '.wit', 'references.txt')
    if not os.path.exists(a_file):
        parent = None  # if a reference file doesn't exist yet, there is not parent file
    else:
        with open(a_file, 'r') as reference_file:
            head_line = reference_file.readline()
            parent = head_line[5:-1]
    message = message  # a message from the cmd
    data = f'''parent={parent}
    date={time.asctime()} +0300
    message={message}'''
    # how do i do the +0300 without a simple string?!!!!?
    with open(name_file, 'w') as f:
        f.write(data)
    staging_area_info = os.path.join(root_directory, '.wit', 'staging_area')
    shutil.copy(staging_area_info, name_folder)

    path_1 = os.path.join(root_directory, '.wit', 'activated.txt')
    with open(path_1, 'w') as activate_text:
        current_branch = activate_text.readline()
    with open(a_file, 'r') as reference_file:
        head_last = reference_file.readline()
        master_line = reference_file.readline()
        branch_line = reference_file.readline()
    if current_branch == head_last[5:-1]:
        with open(a_file, 'w') as file:
            file.write(head_last)
            file.write(master_line)
            location = branch_line.find('=')
            branch_name = branch_line[:location]
            file.write(f"{branch_name}={commit_id}")
            if current_branch == branch_name:  # the conditions for advancing the master tag
                master_change = True
            else:
                master_change = False

    head_string = f"HEAD={commit_id}\n"
    master_string = f"master={commit_id}"
    if os.path.exists(a_file):
        with open(a_file, 'r') as reference_file:
            head_line = reference_file.readline()
            master_line = reference_file.readline()
        if master_change:
            with open(a_file, 'w') as file:
                file.write(head_string)
                file.write(master_string)
        else:
            with open(a_file, 'w') as file:
                file.write(head_string)
                file.write(master_line)
    else:
        with open(a_file, 'w') as file:
            file.write(head_string)
            file.write(master_string)


def status(root_directory):
    if '.wit' not in os.listdir(root_directory):
        raise FileExistsError('File .wit does not exist in repository.')
    file = os.path.join(root_directory, '.wit', 'references.txt')
    with open(file, 'r') as reference_file:
        head_line = reference_file.readline()
        current_commit_id = head_line[5:-1]
    root_directory_folders = list(os.listdir(root_directory))
    changes_to_be_committed = []
    changes_not_staged_for_commit = []
    untracked_files = []
    for entry in root_directory_folders:
        staging_file = os.path.join(root_directory, '.wit', 'staging_area', entry)
        entry_file = os.path.join(root_directory, entry)
        if os.path.isfile(entry):
            if os.path.exists(staging_file):
                same_file = filecmp.cmp(entry_file, staging_file, shallow=False)
                if same_file:
                    changes_to_be_committed.append(entry)
                else:
                    changes_not_staged_for_commit.append(entry)
            else:
                untracked_files.append(entry)
        else:
            three_lists = [changes_to_be_committed, changes_not_staged_for_commit, untracked_files]
            all_lists = find_directory_files(entry, entry_file, staging_file, three_lists)
            changes_to_be_committed.extend(all_lists[0])
            changes_not_staged_for_commit.extend(all_lists[1])
            untracked_files.extend(all_lists[2])
    message = f"""
        Current commit id : {current_commit_id}.
        Changes to be committed: {','.join(changes_to_be_committed)}.
        Changes not staged for commit: {','.join(changes_not_staged_for_commit)}.
        Untracked files: {','.join(untracked_files)}.
        """
    print(message)
    final_list = [changes_to_be_committed, changes_not_staged_for_commit, untracked_files]
    return final_list


def find_directory_files(entry, entry_file, staging_file, three_lists):
    """The case where entry is a directory."""
    folder_files = [a_file for a_file in os.listdir(entry_file) if os.path.isfile(a_file)]  # gets files in folder
    common = folder_files
    # compare the files in the folder to the folder in staging area:
    match, mismatch, errors = filecmp.cmpfiles(entry_file, staging_file, common, shallow=False)  # returns 3 lists
    three_lists[0].extend(match)
    three_lists[1].extend(mismatch)
    three_lists[2].extend(errors)

    folder_folders = [directory for directory in os.listdir(entry) if os.path.isdir(directory)]
    if len(folder_folders) > 1:  # there are also directories in entry
        for directory in folder_folders:  # make sure to compare files in those directories too
            entry_file = os.path.join(entry_file, directory)
            staging_file = os.path.join(staging_file, directory)
            entry = directory
            return find_directory_files(entry, entry_file, staging_file, three_lists)
    else:
        return three_lists


def checkout(root_directory, commit_id, file_list):
    if '.wit' not in os.listdir(root_directory):
        raise FileExistsError('File .wit does not exist in repository.')
    if file_list[0] > 1 or file_list[1] > 1:  # changes_to_be_committed, changes_not_staged_for_commit
        return "Function failed. Files are present in Changes to be committed or Changes not staged for commit."
    if commit_id.isalpha():  # i'm assuming branch has no numbers in it
        branch_name = commit_id
    else:
        file = os.path.join(root_directory, '.wit', 'references.txt')
        with open(file, 'r') as reference_file:
            _ = reference_file.readline()
            _ = reference_file.readline()
            branch_id = reference_file.readline()
            location = branch_id.find('=')
            branch_name = branch_id[:location]

    path_1 = os.path.join(root_directory, '.wit')
    with open(os.path.join(path_1, 'activated.txt'), 'w') as activate_text:
        activate_text.write(branch_name)

    current_id = commit_id
    if commit_id == 'master':
        file = os.path.join(root_directory, '.wit', 'references.txt')
        with open(file, 'r') as reference_file:
            _ = reference_file.readline()
            master_line = reference_file.readline()
            current_id = master_line[7:]

    commit_id_path = os.path.join(root_directory, '.wit', 'images', current_id)
    commit_id_files = os.listdir(commit_id_path)
    for file in commit_id_files:
        if file not in file_list[2]:  # not an untracked file
            commit_id_file = os.path.join(commit_id_path, file)
            shutil.copy(commit_id_file, root_directory)  # copy commit id to root directory

    file = os.path.join(root_directory, '.wit', 'references.txt')
    with open(file, 'r') as reference_file:
        _ = reference_file.readline()  # find head
        master_line = reference_file.readline()
    with open(file, 'w') as reference_file:
        new_head_line = f"""HEAD={commit_id}\n"""  # change it to current commit_id
        reference_file.write(new_head_line)
        reference_file.write(master_line)

    staging_folder = os.path.join(root_directory, '.wit', 'staging_area')
    staging_files = os.listdir(staging_folder)
    for file in staging_files:
        if os.path.isfile(file):
            os.remove(file)
        elif os.path.isdir(file):
            try:
                os.rmdir(file)
            except OSError:
                shutil.rmtree(file)
    shutil.copy(commit_id_path, staging_folder)


def graph(root_directory):
    if '.wit' not in os.listdir(root_directory):
        raise FileExistsError('File .wit does not exist in repository.')
    a_file = os.path.join(root_directory, '.wit', 'references.txt')
    circles = []
    with open(a_file, 'r') as reference_file:
        head_line = reference_file.readline()
        commit_name = head_line[5:-1]

    while commit_name is not None:
        commit_text = os.path.join(root_directory, 'wit', 'images', f'{commit_name}.txt')
        with open(commit_text, 'r') as texts:
            parent_line = texts.readline()
            commit_parent = parent_line[7:-1]
        father_son = (commit_name, commit_parent)
        circles.append(father_son)
        commit_name = commit_parent

    G = nx.DiGraph()
    G.add_edges_from(circles)
    edges = [circles]
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), node_size=500)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='b', arrows=True)
    plt.show()


def branch(branch_name, root_directory):
    if '.wit' not in os.listdir(root_directory):
        raise FileExistsError('File .wit does not exist in repository.')

    file = os.path.join(root_directory, '.wit', 'references.txt')
    with open(file, 'r') as reference_file:
        head_line = reference_file.readline()
        commit_id = head_line[5:-1]
        master_line = reference_file.readline()
    with open(file, 'w') as reference_file:
        reference_file.write(head_line)
        reference_file.write(master_line)
        reference_file.write(f"{branch_name}={commit_id}")





root_dir = init()  # sys.argv[1]() ?
# שכחת לצרף את הקוד שמטפל ב־sys.argv
add(sys.argv[2], root_dir)
commit(sys.argv[2], root_dir)
file_list = status(root_dir)
checkout(root_dir, sys.argv[2], file_list)
graph(root_dir)
branch(sys.argv[2], root_dir)