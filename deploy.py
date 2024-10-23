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


def collect_static():
    print("Collecting static files...")
    # Collect static files
    run_command("python manage.py collectstatic --noinput")


def deploy_to_heroku():
    # Push to Heroku
    run_command("git push heroku main")


if __name__ == "__main__":
    commit_message = input("Enter commit message: ")

    # Step 1: Collect static files
    collect_static()

    # Step 2: Add, commit, and push changes
    git_add_commit_push(commit_message)

    # Step 3: Deploy to Heroku
    deploy_to_heroku()
