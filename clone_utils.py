import os
import stat
import errno
from git import Repo

# Function to handle errors during directory removal
def handle_remove_readonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.unlink, os.rmdir) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU)  # Change permissions to allow deletion
        func(path)
    else:
        raise

# Function to clone or pull a repository into a specified folder
def clone_or_pull_repo(repo_url, clone_dir):
    if os.path.exists(clone_dir):
        if os.listdir(clone_dir):
            # Directory exists and is not empty; pull latest changes
            try:
                repo = Repo(clone_dir)
                origin = repo.remotes.origin
                origin.pull()  # Pull the latest changes
                print(f"Pulled latest changes in {clone_dir} from {repo_url}")
                return True, f"Pulled latest changes in {clone_dir} from {repo_url}"
            except Exception as e:
                print(f"Failed to pull updates in {clone_dir}: {str(e)}")
                return False, f"Failed to pull updates in {clone_dir}: {str(e)}"
        else:
            # Directory exists but is empty; clone the repository
            try:
                Repo.clone_from(repo_url, clone_dir)
                print(f"Cloned {repo_url} into {clone_dir} successfully")
                return True, f"Cloned {repo_url} into {clone_dir} successfully"
            except Exception as e:
                print(str(e))
                return False, str(e)
    else:
        # Directory does not exist; clone the repository
        try:
            Repo.clone_from(repo_url, clone_dir)
            print(f"Cloned {repo_url} into {clone_dir} successfully")
            return True, f"Cloned {repo_url} into {clone_dir} successfully"
        except Exception as e:
            print(str(e))
            return False, str(e)
