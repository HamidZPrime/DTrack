import os
import subprocess


def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.stderr}")


def git_add_commit_push(message="Update from script"):
    # Add changes
    run_command("git add .")

    # Commit changes
    run_command(f"git commit -m \"{message}\"")

    # Push to the main branch
    run_command("git push origin main")


def deploy_to_heroku():
    # Push to Heroku
    run_command("git push heroku main")


if __name__ == "__main__":
    commit_message = input("Enter commit message: ")
    git_add_commit_push(commit_message)
    deploy_to_heroku()
