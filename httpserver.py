import os
import re
import sys
sys.path.insert(0, os.path.dirname(__file__))
from urllib.parse import urlparse
from lib.tools import PROJECTS_DIR, add_dataset, createProjectStructure, delete_transcriptions, deleteDataset, deleteSubDataset, export_table_to_csv, get_content_type, get_db, get_project_dir, import_transcriptions, list_directories, removeRecording, upload_audio
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
#import cgi

PORT = 8080
CSV_FILE = PROJECTS_DIR + 'metadata.csv'
static_dir = 'webapp/build'


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_cors_headers()
        if self.path == '/':
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(f"{static_dir}/200.html", 'rb') as file:
                self.wfile.write(file.read())
        elif self.path .startswith('/_app/'):
            file_path = os.path.join(f"{os.getcwd()}/{static_dir}", self.path.lstrip('/'))
            if os.path.exists(file_path):
                content_type = get_content_type(file_path)
                self.serve_file(file_path, content_type)
            else:
                self.send_error(404, f"File not found: {self.path} {os.getcwd()}/{static_dir}")
        elif self.path.endswith('/.wav/'):
            file_path = get_project_dir() +"/" + os.path.join(f"{os.getcwd()}", self.path.lstrip('/'))
            if os.path.exists(file_path):
                content_type = get_content_type(file_path)
                self.serve_file(file_path, content_type)
            else:
                self.send_error(404, f"File not found: {self.path} {os.getcwd()}/{static_dir}")
        elif self.path.startswith('/get_sentences'):
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            parsed_path = urlparse(self.path)
            path_parts = parsed_path.path.strip('/').split('/')
            recorded = -1
            page = 1
            size = 10
            dataset = -1
            sub_dataset = ""
            try:
                recorded = int(path_parts[1])
                page = int(path_parts[2])
                size = int(path_parts[3])
                dataset = int(path_parts[4])
                sub_dataset = (path_parts[5])
            except ValueError:
                recorded = -1

            count = get_db().count_sentences('sentence', recorded, dataset, sub_dataset)
            json_data =get_db().read_sentences('sentence', recorded, dataset, sub_dataset, page, size)
           
            response = {
               "count": count,
               "subDataSet": sub_dataset,
               "sentence": json.loads(json_data)
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

        elif self.path == '/get_datasets':
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            count = get_db().count('dataset', -1)
            json_data =get_db().read_paginated_data('dataset', -1, 1)
           
            loaded_json = json.loads(json_data)
            for dataset in loaded_json:
                createProjectStructure(dataset['name'])

            response = {
               "count": count,
               "dataset": loaded_json
            }

            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
        
        else:
            self.send_error(404, "Endpoint not found")
        
    def do_OPTIONS(self):
        """Handle preflight CORS requests for non-simple requests like POST, PUT, DELETE."""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def serve_file(self, file_path, content_type):
        """Helper function to serve files"""
        with open(file_path, 'rb') as file:
            file_content = file.read()
            
        # Set the response headers
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Content-length', str(len(file_content)))
        self.send_cors_headers()  # Add CORS headers to each response
        self.end_headers()

        # Write the content to the response
        self.wfile.write(file_content)

    def send_cors_headers(self):
        """Helper function to add CORS headers to the response."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_POST(self):
        # Step 1: Read the Content-Length and the entire body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        # Step 2: Get the boundary from Content-Type header
        content_type = self.headers.get('Content-Type')
        boundary = content_type.split("boundary=")[-1]
        boundary_bytes = ("--" + boundary).encode("utf-8")
        content_type = content_type.split("; boundary=")[0]
        # Step 3: Split the body by the boundary
        parts = body.split(boundary_bytes)
        fields = {}

        for part in parts:
            if not part or part == b'--\r\n':  # Ignore the empty or end boundary part
                continue

            # Step 4: Split headers and content
            headers, content = part.split(b"\r\n\r\n", 1)
            headers = headers.decode("utf-8")
            content = content.rstrip(b"\r\n")  # Trim the trailing newline

            # Step 5: Parse Content-Disposition for field name and filename
            disposition = re.search(r'Content-Disposition:.*? name="([^"]+)"(?:; filename="([^"]+)")?', headers)
            if disposition:
                name = disposition.group(1)
                filename = disposition.group(2)

                if filename:  # If it's a file
                    fields[name] = {
                        'filename': filename,
                        'content': content  # File content as bytes
                    }
                else:  # If it's a regular field
                    fields[name] = content.decode("utf-8")  # Decode content to string

        if content_type == 'multipart/form-data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            if self.path == '/upload_audio':
                try:
                    upload_audio(fields)
                    self.wfile.write(json.dumps({"status": "success", "message": "Audio saved"}).encode())
                except Exception as e:
                    print(e)
                    self.wfile.write(json.dumps({"status": "failed", "message": "Audio not saved"}).encode())
            elif self.path == '/removeRecording':
                try:
                    removeRecording(fields)
                    self.wfile.write(b'{"status": "success", "message": "File deleted"}')
                except Exception as e:
                    print(e)
                    self.wfile.write(b'{"status": "Failed", "message": "File not deleted"}')
            elif self.path == '/delete_dataset':
                try:
                    deleteDataset(fields)
                    self.wfile.write(b'{"status": "success", "message": "Dataset deleted"}')
                except Exception as e:
                    print(e)
                    self.wfile.write(b'{"status": "Failed", "message": "Dataset not deleted"}')
            elif self.path == '/delete_sub_dataset':
                try:
                    deleteSubDataset(fields)
                    self.wfile.write(b'{"status": "success", "message": "Dataset deleted"}')
                except Exception as e:
                    print(e)
                    self.wfile.write(b'{"status": "Failed", "message": "Dataset not deleted"}')
            elif self.path == '/import_transcriptions':
                try:
                    import_transcriptions(fields)
                    self.wfile.write(b'{"status": "success", "message": "File imported"}')
                except Exception as e:
                    print(e)
                    self.wfile.write(b'{"status": "Failed", "message": "File not imported"}')
            elif self.path == '/delete_transcriptions':
                try:
                    delete_transcriptions(fields)
                    self.wfile.write(b'{"status": "success", "message": "transcription deleted"}')
                except Exception as e:
                    print(e)
                    self.wfile.write(b'{"status": "Failed", "message": "transcription not deleted"}')
            elif self.path == '/add_dataset':
                try:
                    add_dataset(fields)
                    self.wfile.write(b'{"status": "success", "message": "dataset added"}')
                except Exception as e:
                    print(e)
                    self.wfile.write(b'{"status": "Failed", "message": "dataset not add"}')       
            elif self.path == '/export_dataset':
                try:
                    export_table_to_csv(fields)
                    self.wfile.write(b'{"status": "success", "message": "dataset exported"}')
                except Exception as e:
                    print(e)
                    self.wfile.write(b'{"status": "Failed", "message": "dataset not exported"}')       
            else:
                self.send_response(400)
                self.send_cors_headers()  # Add CORS headers to each response
                self.end_headers()


def run(server_class=HTTPServer, handler_class=SimpleHandler):
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    print(f"Server started on port {PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
        # Change the current directory to serve static files
    run()
