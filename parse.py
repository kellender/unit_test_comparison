import os

import subprocess
from subprocess import check_output

import json, re

# hashes of commits that were already touched
hashes = []

# metadata dictionary
metadata = {}

def add_child( parent_hash, child_hash ) :
  """
  <Purpose>
      This function assigns child nodes to metadata for the current node.
      Value added will be the child hash.
  
  <Arguments>
      Parent and childs' hashes.
  
  <Exceptions>
      None. Program will fail silently if algorithm is not found.
  
  <Returns>
      Nothing.
  """
  
  global metadata

  child_num = 2

  while True :
    # child label in metadata
    child = "child"+`child_num`
    # if a child with this lable exists increment the child number
    # else add the label and passed child hash to the parent's metadata
    if child in metadata[parent_hash] :
      child_num += 1
    else :
      metadata[parent_hash][child] = child_hash
      break

def add_timestamps( commit_hash ) :
  """
  <Purpose>
      This function adds timestamps to metadata associated with action.
  
  <Arguments>
      Committer's hash and a bool value indicating whether action
      is a merge or not.
  
  <Exceptions>
      None. Program will fail silently if algorithm is not found.
  
  <Returns>
      Nothing.
  """
  global metadata

  # git command for getting the author timestamp
  metadata[commit_hash]["author_timestamp"] = check_output(
    ["git", "show", "-s", "--format=%ai", commit_hash]
    ).strip( )

  # git command for getting the commit timestamp
  metadata[commit_hash]["commit_timestamp"] = check_output(
    ["git", "show", "-s", "--format=%ci", commit_hash]
    ).strip( )


# for now types include: HEAD, TAIL, commit, pre-branch/fork. amd merge
def add_type( commit_hash, commit_type ) :
  """
  <Purpose>
      Adds the "Type" of action attribute to the metadata.
  
  <Arguments>
      The commit's hash and commit's type from another call is required.
  
  <Exceptions>
      None. Program will fail silently if algorithm is not found.
  
  <Returns>
      Nothing.
  """
  
  global metadata

  # if there is no commit type for the passed commit, add it
  # else append the passed type to the "commit_type" attribute
  if "commit_type" not in metadata[commit_hash] :
    metadata[commit_hash]["commit_type"] = commit_type
  else :
    # could be "pre-branch/fork" and "merge" simultaneously
    metadata[commit_hash]["commit_type"] += "; "+commit_type

          
# Recurse thought the tree until the initial commit is reached.
def traverse( commit_hash, child_hash = None ) :
  """
  <Purpose>
      This function takes in the HEAD node and recurses backwards
      while visiting each node.
  
  <Arguments>
      HEAD node.
  
  <Exceptions>
      None. Program will fail silently if algorithm is not found.
  
  <Returns>
      Nothing.
  """
  
  global hashes
  global metadata

  # initialize the current commit as dictionary
  metadata[commit_hash] = {}

  # if a child hash was passed, add it to the current commit's metadata
  if child_hash :
      metadata[commit_hash]["child1"] = child_hash

  # text of the current git commit object
  # elements of current_commit are in the format "<label> <value>"
  current_commit = check_output(
      ["git", "cat-file", "-p", commit_hash]
      ).split( "\n" )
  
  # parents of the current commit
  parents = []
  for line in current_commit :
    # if the line isn't blank
    if len( line ) != 0 :
      # if the line has a parent hash, store the line
      # if the line has the commit's author, add it to the metadata
      # if the line has the commit's committer, add it to the metadata
    
      if line.startswith( "parent" ) :
        parents.append( line )
      elif line.startswith( "author" ) :
        author = line.split( " ", 1 )[1]
        metadata[commit_hash]["author"] = \
          author[:author.find( ">" )+1]
      elif line.startswith( "committer" ) :
        committer = line.split( " ", 1 )[1]
        metadata[commit_hash]["committer"] = \
          committer[:committer.find( ">" )+1]

  # add the author and committer timestamps to the commit's metadata
  add_timestamps( commit_hash )
  

 #for each commit
  git_out = subprocess.Popen("git checkout " + commit_hash, cwd = os.getcwd(), shell = True, 
    stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  commit, err = git_out.communicate()

  os.chdir("./scripts")
  from subprocess import call
  subprocess.call(["python", "initialize.py"]) # i am only usinbg call because for some reason on my vm i get different errors for build scripts
  subprocess.call(["python", "build.py", "-t"])
  os.chdir("../RUNNABLE")
  # popen is used here to pass output of test
  run_out = subprocess.Popen("python utf.py -f ut_seattlelib_tcptime.py", cwd = os.getcwd(), shell = True, 
    stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  out, err = run_out.communicate()

  # # for a single unit test
  
  
  unit_test_name = ""
  outcome = ""
  for line in out.splitlines():
    if("Running:" in line):
      for word in line.split():
        if ("ut" in word):
          unit_test_name = word
        if ("PASS" in word or "FAIL" in word):
          outcome = word

  print commit_hash + "\t" + str(unit_test_name) + "\t" + str(outcome) + "\t" + metadata[commit_hash]["commit_timestamp"]

  # # print "finish build scripts"
  os.chdir("..")
  run_out = subprocess.Popen("git stash save --keep-index", cwd = os.getcwd(), shell = True, 
    stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  run_out = subprocess.Popen("git stash drop", cwd = os.getcwd(), shell = True, 
    stdout = subprocess.PIPE, stderr = subprocess.PIPE)




  # if the commit has parents
  if len( parents ) > 0 :
  # for each parent, add them to the current commit's metadata
  # and add the current commit as each parent's child
    for i in range( 0, len( parents )  ) :
      # get the parent hash from the git commit object's line
      parent_hash = parents[i].split( )[1]

      # add the parent hash to the current commit
      metadata[commit_hash]["parent"+`i+1`] = parent_hash
      
      # if the parent hash isn't in hashes, add it and traverse the
      # parent commit
      # else add the current commit to the parent as a child
      if parent_hash not in hashes :
        hashes.append( parent_hash )
        traverse( parent_hash, commit_hash )
      else :
        add_child( parent_hash, commit_hash )


def parse_driver():
  git_process = subprocess.Popen("git clone https://github.com/SeattleTestbed/seattlelib_v2", cwd = os.getcwd(), shell = True, 
    stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  out, err = git_process.communicate()
  os.chdir("./seattlelib_v2")
  global metadata
  global hashes
  # hash of the HEAD commit
  print "hi"
  head = check_output( ["git", "rev-parse", "HEAD"] ).strip( )
  # add the head commit to hashes
  print "hi"
  
  hashes.append( head )
  # start the git commit object traversal
  print "hi"
  
  traverse( head )
  # add a commit type to each commit
  print "hi"




  # #for the first commit

  # git_out = subprocess.Popen("git rev-parse HEAD", cwd = os.getcwd(), shell = True, 
  #   stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  # commit, err = git_out.communicate()

  # os.chdir("./scripts")
  # from subprocess import call
  # subprocess.call(["python", "initialize.py"]) # i am only usinbg call because for some reason on my vm i get different errors for build scripts
  # subprocess.call(["python", "build.py", "-t"])
  # os.chdir("../RUNNABLE")
  # #popen is used here to pass output of test
  # run_out = subprocess.Popen("python utf.py -f ut_seattlelib_tcptime.py", cwd = os.getcwd(), shell = True, 
  #   stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  # out, err = run_out.communicate()

  # # for a single unit test
  
  
  # unit_test_name = ""
  # outcome = ""
  # for line in out.splitlines():
  #   if("Running:" in line):
  #     for word in line.split():
  #       if ("ut" in word):
  #         unit_test_name = word
  #       if ("PASS" in word or "FAIL" in word):
  #         outcome = word

  # print commit[0:7] + "\t" + str(unit_test_name) + "\t" + str(outcome)

  # # print "finish build scripts"
  # os.chdir("..")
  # run_out = subprocess.Popen("git stash save --keep-index", cwd = os.getcwd(), shell = True, 
  #   stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  # run_out = subprocess.Popen("git stash drop", cwd = os.getcwd(), shell = True, 
  #   stdout = subprocess.PIPE, stderr = subprocess.PIPE)




  # for commit, data in metadata.items():
  #   run_out = subprocess.Popen("git checkout " + str(commit), cwd = os.getcwd(), shell = True, 
  #     stdout = subprocess.PIPE, stderr = subprocess.PIPE)



  #   os.chdir("./scripts")
  #   from subprocess import call
  #   subprocess.call(["python", "initialize.py"]) # i am only usinbg call because for some reason on my vm i get different errors for build scripts
  #   subprocess.call(["python", "build.py", "-t"])
  #   os.chdir("../RUNNABLE")
  #   #popen is used here to pass output of test
  #   run_out = subprocess.Popen("python utf.py -f ut_seattlelib_tcptime.py", cwd = os.getcwd(), shell = True, 
  #     stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  #   out, err = run_out.communicate()

  #   # for a single unit test
    
    
  #   unit_test_name = ""
  #   outcome = ""
  #   for line in out.splitlines():
  #     if("Running:" in line):
  #       for word in line.split():
  #         if ("ut" in word):
  #           unit_test_name = word
  #         if ("PASS" in word or "FAIL" in word):
  #           outcome = word

  #   print commit[0:7] + "\t" + str(unit_test_name) + "\t" + str(outcome) + "\t" + str(data.get("commit_timestamp"))

  #   # print "finish build scripts"
  #   os.chdir("..")
  #   run_out = subprocess.Popen("git stash save --keep-index", cwd = os.getcwd(), shell = True, 
  #     stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  #   run_out = subprocess.Popen("git stash drop", cwd = os.getcwd(), shell = True, 
  #     stdout = subprocess.PIPE, stderr = subprocess.PIPE)














  #     # is it the head or tail commit
  #     hORt = False

  #     # if there are two or more children, it's a pre-branch/fork commit
  #     # if there are no children, it's a HEAD commit
  #     if "child2" in metadata[commit] :
  #         add_type( commit, "pre-branch/fork" )
  #     elif "child1" not in metadata[commit] :
  #         add_type( commit, "HEAD" )
  #         hORt = True

  #     # if there are two or more parents, it's a merge commit
  #     # if there are no parents, it's the tail commit
  #     # also no need to mark as the TAIL if it's the HEAD
  #     if "parent2" in metadata[commit] :
  #         add_type( commit, "merge" )
  #     elif "parent1" not in metadata[commit] and not hORt :
  #         add_type( commit, "TAIL" )
  #         hORt = True

  #     # if there are neither multiple parents nor multiple children
  #     # it's a normal commit
  #     if "parent2" not in metadata[commit] and \
  #         "child2" not in metadata[commit] and not hORt :
  #         add_type( commit, "commit" )

  # # check for code review
  # check_code_review( head )

  # # get repository name so that it can be appended to file names
  # path_to_name = check_output(["git", "rev-parse", "--show-toplevel"]).strip()
  # path_list = re.split('/', path_to_name)
  # repo_name = str(path_list[len(path_list) - 1])

  # # write metadata to a file in a json format
  # with open( "../metadata_" + repo_name + ".json", "w" ) as ofs :
  #     ofs.write( json.dumps( metadata, indent = 4 ) )

  # # pause the terminal in case metadata.json needs to be checked
  # # this time can be used to open a new terminal and run the
  # # acl.json file generator for permissions: ctrl.py
  # #raw_input("Program is paused, hit enter twice to run checker")
  # #raw_input("Once more...")

  # # run checker from check.py
  # metadata_lib.check_acl(metadata, "../" + acl_filename, "../violations_" + repo_name + ".json")

parse_driver()