
import csv
import json
import os
import shutil
import sys
from lib.sqlite_db import SQLiteDBHelper

sys.path.insert(0, os.path.dirname(__file__))

PROJECTS_DIR = "projects"

# Initialize the database
db = SQLiteDBHelper("db/data.db")

def get_db():
    return db

def get_project_dir():
    return os.path.join(PROJECTS_DIR)

# Load CSV data into memory
def load_csv(csv_file):
    
    data = []
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
    return data

# Save updated CSV data back to the file
def save_csv(csv_file, data):
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def check_file_exists(file_path):
    """Check if a file exists at the specified path."""
    return os.path.exists(file_path)

def list_directories(path):
    # List all directories in the specified path
    return [path+'/'+name for name in os.listdir(os.path.join(path)) if os.path.isdir(os.path.join(path, name))]

def delete_file(file_path):
    try:
        os.remove(file_path)
        return True
    except FileNotFoundError:
        print("File not found.")
        return True
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False

def delete_and_recreate_folder(folder_path):
    try:
        # Delete the folder and its contents
        shutil.rmtree(folder_path)
        print(f"Deleted folder: {folder_path}")
        
        # Recreate the folder
        os.makedirs(folder_path)
        print(f"Recreated folder: {folder_path}")
    except FileNotFoundError:
        # If the folder doesn't exist, simply create it
        os.makedirs(folder_path)
        print(f"Folder didn't exist, created: {folder_path}")
    except Exception as e:
        print(f"Error: {e}")


def upload_audio( fields):
        audio_data = fields.get("audio", {}).get("content")
        sentence_id = int(fields.get('id'))
        dataset = fields.get('dataset')
        subset= fields.get('subset')

        file = fields.get('file')
        filename = PROJECTS_DIR  +"/" + dataset + "/" + subset + "/audio/"  + file
        with open(filename, "wb") as audio_file:
            audio_file.write(audio_data)

        db.flag('sentence', 1, sentence_id)
        json_data = db.read_by_key('sentence', 'id', sentence_id)
        return (json_data).encode()


def import_transcriptions(fields):
    transcription = fields.get('transcription')
    sub_dataset = fields.get('sub_dataset')
    dataset = int(fields.get('dataset'))

    transcription_json = json.loads(transcription)
    db.save_json_data('sentence', transcription_json, dataset, sub_dataset)
    return True

def add_dataset(fields):
    name = fields.get('dataset')
    my_dict = {
        "name": name
    }
    db.insert('dataset',my_dict)
    return True


def createFolder(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        print(f"The folder {folder_path} exists.")
    else:
        print(f"The folder {folder_path} does not exist. creating")
        os.makedirs(folder_path)

def createProjectStructure(dataset_name):
    train_folder_path = PROJECTS_DIR + "/"  + dataset_name  + "/train" + "/audio/"
    createFolder(train_folder_path)
    test_folder_path = PROJECTS_DIR + "/"  + dataset_name  + "/test" + "/audio/"
    createFolder(test_folder_path)
    validation_folder_path = PROJECTS_DIR + "/"  + dataset_name  + "/validation" + "/audio/"
    createFolder(validation_folder_path)



def delete_transcriptions(fields):
    transcription = fields.get('transcription')
    sub_dataset = fields.get('subset')
    dataset = fields.get('dataset')

    transcriptions =transcription.split(',')
    for id in transcriptions:
        print(id)
        row = db.read_by_key('sentence', 'id', int(id))
        row_dict = json.loads(row)
        file_name= row_dict['file']

        file_path = PROJECTS_DIR + "/"  + dataset  + "/" +sub_dataset+ "/audio/" + "/" + file_name
        if delete_file(file_path):
            db.delete('sentence', 'id', int(id))
    return True

def removeRecording(fields):
    sentence_id = int(fields.get('id'))
    file = fields.get('file')
    sub_dataset = fields.get('subset')
    dataset = fields.get('dataset')

    # Attempt to delete the file and respond with success or failure
    file_path = PROJECTS_DIR + "/"  + dataset+ "/" + sub_dataset + "/audio/"  + "/" + file
    if delete_file(file_path):
        db.flag('sentence', 0, sentence_id)

def deleteDataset(fields):
    dataset_id = int(fields.get('datasetId'))
    dataset_name = fields.get('datasetName')
    db.delete('dataset', 'id', dataset_id)

    # Attempt to delete the file and respond with success or failure
    # Example usage
    folder_path = PROJECTS_DIR + "/"  + dataset_name
    # Delete the folder and its contents
    shutil.rmtree(folder_path)
    return True

def deleteSubDataset(fields):
    dataset = fields.get('dataset')
    sub_dataset = fields.get('sub_dataset')
    db.delete_sub_data_set('sentence', 'dataset', dataset, 'sub_dataset', sub_dataset)

    # Attempt to delete the file and respond with success or failure
    # Example usage
    file_path = PROJECTS_DIR + "/"  + dataset+ "/" + sub_dataset + "/audio/"
    delete_file(file_path)
    return True



def get_content_type(self, file_path):
    """Determine the content type based on file extension"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.html':
        return 'text/html'
    elif ext == '.js':
        return 'application/javascript'
    elif ext == '.css':
        return 'text/css'
    elif ext == '.json':
        return 'application/json'
    elif ext == '.woff2':
        return 'font/woff2'
    elif ext == '.mp3':
        return 'audio/mpeg'  # MIME type for MP3 files
    elif ext == '.wav':
        return 'audio/wav'   # MIME type for WAV files
    else:
        return 'application/octet-stream'