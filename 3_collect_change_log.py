import json
import os
import subprocess
import sys


current_branch = ""

# >> fields from build_info.json
build_number = ""
build_date = ""
previous_build_tag = ""
repo_url = ""
git_branch = ""
application_version = ""
application_name = ""
previous_build_date = ""
build_tag = ""
# << fields from build_info.json

def check_not_empty(var, var_name):
    try:
        assert(var != "")
    except:
        print("check_info, %s is empty" % var_name)
        sys.stdout.flush()
        sys.exit(1)
    return

def get_current_git_branch():
    global current_branch

    print(">> get_current_git_branch")
    sys.stdout.flush()

    git_get_current_branch = ["git", "symbolic-ref", "--short", "HEAD"]

    try:

        codeproc = subprocess.Popen(git_get_current_branch, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        current_branch = codeproc.stdout.read().decode("utf-8").strip()

    except Exception as e:
        print("git symbolic-ref --short HEAD failed")
        print(e)
        sys.stdout.flush()
        sys.exit(1)

    sys.stdout.flush()

    print("<< get_current_git_branch, currentBranch: [%s]" % current_branch)
    return


def tag_branch():
    print(">> tag_branch gitTag [%s]" % build_tag)

    print("tag_branch, add tag [%s] to the branch [%s]" % (build_tag, git_branch))
    sys.stdout.flush()

    msg = "[%s] tag [%s] build [%s] at branch [%s]" % (application_name, build_tag, build_number, current_branch)

    git_tag_execute = ["git", "tag", "-a", "-f", "-m", msg, build_tag]

    error_message = "git tag failed"
    execute_command(error_message, git_tag_execute)

    print("<< tag_branch")
    return

def parse_build_info():
    print (">> parse_build_info")

    global build_info_json_filepath
    global \
        build_number, \
        build_date, \
        previous_build_tag, \
        repo_url, \
        git_branch, \
        application_version, \
        application_name, \
        previous_build_date, \
        build_tag

    build_info_json_filepath = os.path.join("build_info.json")

    print ("parse_build_info, Getting git configuration from %s" %build_info_json_filepath)

    if not os.path.exists(build_info_json_filepath):
        print("parse_build_info, %s does not exist" % build_info_json_filepath)
        sys.stdout.flush()
        sys.exit(1)

    try:
        f = open(build_info_json_filepath, 'r')
        configFileJson = json.load(f)
    except Exception as e:
        print("parse_build_info, json.load failed %s" % e)
        f.close()
        sys.stdout.flush()
        sys.exit(1)

    f.close()

    build_number           = configFileJson["build_number"]
    build_date             = configFileJson["build_date"]
    previous_build_tag     = configFileJson["previous_build_tag"]
    repo_url               = configFileJson["repo_url"]
    git_branch             = configFileJson["git_branch"]
    application_version    = configFileJson["application_version"]
    application_name       = configFileJson["application_name"]
    previous_build_date    = configFileJson["previous_build_date"]
    build_tag              = configFileJson["build_tag"]


    print("build_number           = %s" % build_number)
    print("build_date             = %s" % build_date)
    print("previous_build_date    = %s" % previous_build_date)
    print("repo_url               = %s" % repo_url)
    print("git_branch             = %s" % git_branch)
    print("application_version    = %s" % application_version)
    print("application_name       = %s" % application_name)
    print("build_tag              = %s" % build_tag)
    print("previous_build_tag     = %s" % previous_build_tag)

    check_not_empty(build_number, "build_number")
    check_not_empty(build_date, "build_date")
    check_not_empty(repo_url, "repo_url")
    check_not_empty(git_branch, "git_branch")
    check_not_empty(application_version, "application_version")
    check_not_empty(application_name, "application_name")
    check_not_empty(build_tag, "build_tag")
    check_not_empty(previous_build_tag, "previous_build_tag")

    print ("<< parse_build_info")
    return


def commit_build_info_json():
    print (">> commit_build_info_json")

    filename = "build_info.json"

    git_add = ["git", "add", filename]
    error_message = "git add %s failed" % filename

    execute_command(error_message, git_add)

    commit_message = "%s version %s at branch '%s' build updated to %s" % (application_name, application_version, current_branch, build_number)
    git_commit = ["git", "commit", "-m", commit_message, filename]
    error_message = "git commit %s failed" % filename

    execute_command(error_message, git_commit)

    print ("<< commit_build_info_json")


def execute_command(error_message, git_commit):
    try:

        codeproc = subprocess.Popen(git_commit, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = codeproc.stdout.read().decode("utf-8").strip()
        print(result)

    except Exception as e:
        print(error_message)
        print(e)
        sys.stdout.flush()
        sys.exit(1)


def push_changes():
    print(">> push_changes")

    print("push_changes, pushing")
    git_push_exec = ["git", "push"]
    error_message = "git push failed"
    execute_command(error_message, git_push_exec)

    print("push_changes, pushing up tag")
    git_push_tag_exec = ["git", "push", "origin", build_tag]
    error_message = "git push tag failed"
    execute_command(error_message, git_push_tag_exec)

    print("push_changes, force pushing")
    git_exec_push_force = ["git", "push", "--force"]
    error_message = "git push --force failed"
    execute_command(error_message, git_exec_push_force)

    print("<< push_changes")


def main(argv):
    print (">> main")

    sys.stdout.flush()

    # 1. Parse data in build_info.json
    parse_build_info()

    # 2. Get current branch from git
    get_current_git_branch()

    # Example: "git log --pretty=format:"%s" SetupBitbucketCloudCI/1.0/2..SetupBitbucketCloudCI/1.0/3~1"
    git_change_log = ["git", "log", "--pretty=format:\"%s\"", "%s..%s~1" %(previous_build_tag, build_tag)]

    code_proc = subprocess.Popen(git_change_log, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_text = code_proc.stdout.read().decode("utf-8").strip()

    with open("change_log_external.txt", "w+") as output:
        output.write("External\n\n")
        output.write(output_text)
        output.close()

    with open("change_log_internal.txt", "w+") as output:
        output.write("Internal\n\n")
        output.write(output_text)
        output.close()

    sys.stdout.flush()

    print ("<< main")
    return

if __name__ == '__main__':
    main(sys.argv)