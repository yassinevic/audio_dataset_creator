
import csv
import json
import os
import platform
import shutil
import subprocess
import sys
import wave
from lib.sqlite_db import SQLiteDBHelper

sys.path.insert(0, os.path.dirname(__file__))

PROJECTS_DIR = "projects"

DB_FILE = os.path.join(f"{os.getcwd()}/db/data.db").replace('\\', '/')
SQL_FILE = os.path.join(f"{os.getcwd()}/tables.sql").replace('\\', '/')

# Initialize the database
db = SQLiteDBHelper(DB_FILE, SQL_FILE)

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
        #audio_data = fields.get("audio", {}).get("content")
        audio_field = fields.get("audio")
        audio_data = audio_field.get("content")
        sentence_id = int(fields.get('id'))
        dataset = fields.get('dataset')
        subset= fields.get('subset')

        file = fields.get('file')
        file_path_webm = PROJECTS_DIR  +"/" + dataset + "/" + subset + "/audio/"  + file+".webm"
        with open(file_path_webm, "wb") as audio_file:
            audio_file.write(audio_data)

        file_path_wav = PROJECTS_DIR  +"/" + dataset + "/" + subset + "/audio/"  + file
        convert_webm_to_wav(file_path_webm,file_path_wav)
        delete_file(file_path_webm)

        duration = get_wav_duration(file_path_wav)
        print(f"The duration of the WAV file is {duration:.2f} seconds.")

        """   "start_time": 0.0,
        "end_time": duration,
        "speaker": "Speaker 1",
        "emotion": "neutral" """

        db.update(
        table="sentence",
        data={
            "recorded": 1,
            "start_time": 0,
            "end_time": duration,
        },
        condition="id = ?",
        condition_params=(sentence_id,))

        json_data = db.read_by_key('sentence', 'id', sentence_id)
        return (json_data).encode()

def convert_webm_to_wav(input_file, output_file):

    # Check if the output file already exists, and delete it if so
    if os.path.isfile(output_file):
        print(f"Warning: {output_file} already exists. Overwriting the file.")
        os.remove(output_file)  # Remove the existing file

    # Run FFmpeg command to convert webm to wav
    ffmpeg = 'tools/ffmpeg'
    command = [ffmpeg, '-i', input_file, output_file]
    
    try:
        subprocess.run(command, check=False)
        print(f"Conversion successful: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")

def import_transcriptions(fields):
    transcription = fields.get('transcription')
    sub_dataset = fields.get('sub_dataset')
    dataset = int(fields.get('dataset'))

    transcription_json = json.loads(transcription)
    db.save_json_data('sentence', transcription_json, dataset, sub_dataset)
    return True

def add_dataset(fields):
    name = fields.get('speaker')
    my_dict = {
        "name": name
    }
    db.insert('dataset',my_dict)
    return True

def add_speaker(fields):
    name = fields.get('speaker')
    my_dict = {
        "name": name
    }
    db.insert('speaker',my_dict)
    return True

def update_sentance(fields):
    speaker = fields.get('speaker')
    emotion = fields.get('emotion')
    transcription = fields.get('transcription')
    id = int(fields.get('id'))

    db.update(
    table="sentence",
    data={
        "speaker": speaker,
        "emotion": emotion,
        "transcription": transcription,
    },
    condition="id = ?",
    condition_params=(id,)
)
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

def export_table_to_csv(fields):
        sub_dataset = fields.get('subDataset')
        dataset_id = int(fields.get('datasetId'))
        dataset_name = fields.get('datasetName')
        # Query to fetch all data from the table
        query = f"SELECT 'audio/' || file AS file, transcription, end_time as duration, sp.name as speaker, emotion FROM sentence,speaker sp WHERE sp.id = speaker AND dataset = {dataset_id} AND sub_dataset = '{sub_dataset}' and recorded = 1"
        rs = db.execute_query(query)

        # Fetch column names
        columns = ["file", "transcription", "duration", "speaker", "emotion"]

        # Open the CSV file for writing
        output_folder = PROJECTS_DIR + "/"  + dataset_name  + "/" + sub_dataset
        output_csv = output_folder + "/metadata.csv"
        with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write the column headers
            writer.writerow(columns)

            # Write the rows
            writer.writerows(rs)

        open_folder(output_folder)

def delete_transcriptions(fields):
    transcription = fields.get('transcription')
    sub_dataset = fields.get('subset')
    dataset = fields.get('dataset')

    transcriptions =transcription.split(',')
    for id in transcriptions:
        row = db.read_by_key('sentence', 'id', int(id))
        row_dict = json.loads(row)
        file_name= row_dict['file']

        file_path = PROJECTS_DIR + "/"  + dataset  + "/" +sub_dataset+ "/audio/" + "/" + file_name
        if delete_file(file_path):
            db.delete('sentence', 'id', int(id))
    return True

def removeRecording(fields):
    id = int(fields.get('id'))
    file = fields.get('file')
    sub_dataset = fields.get('subset')
    dataset = fields.get('dataset')

    # Attempt to delete the file and respond with success or failure
    file_path = PROJECTS_DIR + "/"  + dataset+ "/" + sub_dataset + "/audio/"  + "/" + file
    if delete_file(file_path):
        db.update(
        table="sentence",
        data={
            "recorded": 1,
        },
        condition="id = ?",
        condition_params=(id,))

        

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

def deleteSpeaker(fields):
    id = int(fields.get('id'))
    db.delete('speaker', 'id', id)
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

def open_folder(path):
    """
    Open a folder in the system's file explorer.

    Parameters:
    - path (str): Path to the folder to open.
    """
    # Get the directory of the current Python script
    win_path = path.replace("/", "\\")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir= script_dir.replace("/lib", "")
    # Construct the full path to the folder
    folder_path = os.path.join(script_dir, win_path)
    try:
        if platform.system() == "Windows":  # For Windows
            script_dir= script_dir.replace("\\lib", "")
            folder_path = os.path.join(script_dir, win_path)
            os.startfile(folder_path)
        elif platform.system() == "Darwin":  # For macOS
            subprocess.run(["open", folder_path])
        elif platform.system() == "Linux":  # For Linux
            subprocess.run(["xdg-open", folder_path])
        else:
            print("Unsupported OS")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_wav_duration(file_path):
    # Check if file exists
    if not os.path.isfile(file_path):
        print(f"Error: The file {file_path} does not exist.")
        return None

    try:
        # Attempt to open the WAV file
        with wave.open(file_path, 'rb') as wav_file:
            # Check if it's a valid WAV file by looking for the "RIFF" format
            if wav_file.getcomptype() != 'NONE':  # Not PCM format
                print(f"Error: The file {file_path} is not a valid uncompressed WAV file.")
                return None

            # Get the number of frames and frame rate (sample rate)
            num_frames = wav_file.getnframes()
            frame_rate = wav_file.getframerate()
            
            if frame_rate == 0:
                print(f"Error: Invalid frame rate in the file {file_path}.")
                return None

            # Calculate and return the duration
            duration = num_frames / float(frame_rate)
            return duration

    except wave.Error as e:
        # Handle wave-related errors (e.g., file is not a valid WAV)
        print(f"Error: Failed to read the WAV file {file_path}. Details: {e}")
        return None
    except Exception as e:
        # General exception handling
        print(f"Error: An unexpected error occurred while processing the file {file_path}. Details: {e}")
        return None


    
def get_content_type( file_path):
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