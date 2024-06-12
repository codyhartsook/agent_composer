#!/bin/bash

# Define project name
PROJECT_NAME="agent_composer"

# Create directories
mkdir -p $PROJECT_NAME
mkdir -p tests

# Create files
touch $PROJECT_NAME/__init__.py
touch $PROJECT_NAME/module.py
touch tests/__init__.py
touch tests/test_module.py
touch README.md
touch .gitignore

echo "Project structure for '$PROJECT_NAME' created successfully!"
