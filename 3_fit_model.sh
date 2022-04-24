echo "Here we fit the model and output a joblib file"
indicators=$1
python msix/models/optimise_and_model.py --indicator $indicators