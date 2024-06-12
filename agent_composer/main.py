import subprocess
import os
import requests
import sys
import importlib
import ast
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
from models.agent_state import AgentState
from langgraph.graph import StateGraph


def download_file_from_github(url, save_path):
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    with open(save_path, 'wb') as file:
        file.write(response.content)


def add_imports_to_file(file_path, imports):
    with open(file_path, 'r') as file:
        content = file.read()

    # Add the necessary imports at the beginning of the file
    new_content = '\n'.join(imports) + '\n' + content

    with open(file_path, 'w') as file:
        file.write(new_content)


def get_function_names(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Parse the file content
    tree = ast.parse(file_content, filename=file_path)

    # Extract function names
    function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    return function_names


def get_imports(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Parse the file content
    tree = ast.parse(file_content, filename=file_path)

    # Extract import statements
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]

    imported_modules = []
    for node in imports:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.append(node.module)

    return imported_modules


def install_dependencies(modules):
    for module in modules:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", module],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"Successfully installed {module}:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {module}:\n{e.stderr}")


def dynamic_import(module_name, function_name):
    module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    return function


def get_function_signature_and_types(file_path, function_name):
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Parse the file content
    tree = ast.parse(file_content, filename=file_path)

    # Find the function definition
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            # Extract argument type hints
            arg_types = {}
            for arg in node.args.args:
                if arg.annotation:
                    arg_types[arg.arg] = eval(arg.annotation.id, globals())
            return arg_types


def create_pydantic_instance(model_class):
    # For demonstration, create an instance with some sample data
    # In practice, you might want to populate this with actual data
    sample_data = {}
    for field_name, field_type in model_class.__annotations__.items():
        if field_type == int:
            sample_data[field_name] = 0
        elif field_type == str:
            sample_data[field_name] = ""
        elif field_type == float:
            sample_data[field_name] = 0.0
        elif field_type == bool:
            sample_data[field_name] = False
        elif issubclass(field_type, BaseModel):
            sample_data[field_name] = create_pydantic_instance(field_type)
        else:
            sample_data[field_name] = None
    return model_class(**sample_data)


def determine_needed_imports(type_hints):
    needed_imports = []
    current_globals = globals()
    for hint in type_hints.values():
        if isinstance(hint, type):
            module_name = hint.__module__
            class_name = hint.__name__
            # Check if this module is already imported in the main script
            if class_name in current_globals:
                import_statement = f'from {module_name} import {class_name}'
                needed_imports.append(import_statement)
    return needed_imports


def download_and_import_agent():
    # URL of the file to download from GitHub
    file_url = ('https://raw.githubusercontent.com/BenderScript/agent_composer/main/agent_composer/resources'
                '/remote_agents/chatbot.py')
    # Path where the downloaded file will be saved
    save_path = 'resources/local_agents/chatbot.py'

    # Step 1: Download the file from GitHub
    download_file_from_github(file_url, save_path)

    # Step 2: Add the path to the cloned repository to PYTHONPATH
    repo_path = os.path.dirname(save_path)
    sys.path.append(repo_path)

    # Step 3: Parse the file to get import statements
    imported_modules = get_imports(save_path)
    print(f"Imported modules: {imported_modules}")

    # Step 4: Install dependencies
    install_dependencies(imported_modules)

    # Step 5: Parse the file to get function names
    function_names = get_function_names(save_path)
    print(f"Functions in {save_path}: {function_names}")

    # Step 6: Get function signature and type hints without importing
    desired_function_name = 'chatbot'
    if desired_function_name in function_names:
        # Get function signature and type hints
        type_hints = get_function_signature_and_types(save_path, desired_function_name)
        print(f"Type hints of {desired_function_name}: {type_hints}")

        # Step 7: Determine necessary imports based on type hints
        needed_imports = determine_needed_imports(type_hints)

        # Step 8: Add necessary imports to the file
        add_imports_to_file(save_path, needed_imports)

        # Step 9: Dynamically import the function with the necessary imports included
        module_name = os.path.basename(save_path).replace('.py',
                                                          '')
        composed_agent = dynamic_import(module_name, desired_function_name)
        print(f"Dynamically imported function: {composed_agent.__name__}")

        # Identify Pydantic types and create instances
        for param_name, param_type in type_hints.items():
            if isinstance(param_type, type) and issubclass(param_type, BaseModel):
                print(f"{param_name} is of Pydantic type {param_type}")
            else:
                print(f"{param_name} is of type {param_type}, which is not a Pydantic model.")
        return composed_agent
    else:
        print(f"Function '{desired_function_name}' not found in the module.")

    return None


def main():
    # Load the .env file
    path = find_dotenv()
    print(path)
    load_dotenv(override=True, verbose=True)

    chatbot_agent = download_and_import_agent()
    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("chatbot_agent", chatbot_agent)
    graph_builder.set_entry_point("chatbot_agent")
    graph_builder.set_finish_point("chatbot_agent")
    graph = graph_builder.compile()

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        for event in graph.stream({"messages": ("user", user_input)}):
            for value in event.values():
                print("Assistant:", value["messages"][-1].content)


if __name__ == "__main__":
    main()
