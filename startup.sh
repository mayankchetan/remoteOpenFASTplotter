#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if a conda environment was provided
if [ $# -lt 1 ]; then
    echo "Error: Missing conda environment name"
    echo "Usage: $(basename $0) <conda_environment_name>"
    exit 1
fi

CONDA_ENV="$1"

# Change to the repository directory
cd "$SCRIPT_DIR"

# Check if this is a git repository
if [ -d .git ] || git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Checking for updates on remote repository..."
    
    # Fetch the latest from remote without merging
    git remote update &> /dev/null
    
    # Check if local is behind remote
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})
    BASE=$(git merge-base @ @{u})
    
    if [ $LOCAL = $REMOTE ]; then
        echo "Repository is up to date."
    elif [ $LOCAL = $BASE ]; then
        echo -e "\033[0;33mWARNING: Your local repository is behind the remote repository.\033[0m"
        echo "There are updates available that can be pulled."
        
        while true; do
            read -p "Do you want to continue without updating? (y/n/p for pull): " choice
            case "$choice" in
                y|Y ) echo "Continuing without updating..."; break;;
                n|N ) echo "Exiting."; exit 1;;
                p|P ) echo "Pulling updates..."; git pull; break;;
                * ) echo "Please answer y (continue), n (exit), or p (pull updates).";;
            esac
        done
    elif [ $REMOTE = $BASE ]; then
        echo -e "\033[0;33mNOTE: Your local repository has unpushed changes.\033[0m"
    else
        echo -e "\033[0;33mWARNING: Your local and remote repositories have diverged.\033[0m"
        echo "Please resolve this manually before running the application."
        
        while true; do
            read -p "Do you want to continue anyway? (y/n): " choice
            case "$choice" in
                y|Y ) echo "Continuing..."; break;;
                n|N ) echo "Exiting."; exit 1;;
                * ) echo "Please answer y or n.";;
            esac
        done
    fi
else
    echo "Not a git repository. Skipping update check."
fi

# Activate conda environment, run the app, then deactivate
echo "Activating conda environment: $CONDA_ENV"
echo "Starting Remote OpenFAST Plotter..."
source activate $CONDA_ENV && python "$SCRIPT_DIR/app.py" && source deactivate

# Return to original directory
cd - > /dev/null