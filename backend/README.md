# Recreate the conda environment
conda env create -f environment.yml

# Run the app
flask run --host=0.0.0.0 --port=5000

# Run the app with hot reloading
flask run --host=0.0.0.0 --port=5000 --reload