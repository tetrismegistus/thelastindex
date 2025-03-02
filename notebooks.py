import os
import subprocess

notebooks_dir = "notebooks"
content_dir = "content"

for notebook in os.listdir(notebooks_dir):
    if notebook.endswith(".ipynb"):
        notebook_path = os.path.join(notebooks_dir, notebook)
        output_path = os.path.join(content_dir, notebook.replace(".ipynb", ".md"))
        
        subprocess.run([
            "jupyter", "nbconvert", "--to", "markdown",
            "--output", output_path, notebook_path
        ])

