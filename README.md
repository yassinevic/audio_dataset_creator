
# Audio Dataset Creator

**Audio Dataset Creator** Audio Dataset Creator is a user-friendly tool designed to facilitate the creation and management of audio datasets for machine learning and speech recognition projects. It allows users to record, organize, and annotate audio files efficiently, ensuring datasets are structured and easy to use. Ideal for building training and testing datasets, the tool streamlines the process of preparing audio data for various applications..


![image](https://github.com/user-attachments/assets/43c0d338-d941-4c84-879f-b4f2e8af6f46)



## Features

- Record and manage audio files.
- Save transcription data to an SQLite database.
- Intuitive UI for easy annotation and dataset management.
- Open-source and easy to set up.

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Node.js and npm

### Clone the Repository
```bash
git clone https://github.com/yassinevic/audio_dataset_creator.git
cd audio_dataset_creator
```

---

## Usage

### 1. Start the Backend Server
The backend is built using Python. Start the server with:
```bash
python httpserver.py
```

This serves the backend for audio file management and database operations.

### 2. Start the Frontend
Navigate to the `webapp` folder to run the UI:
```bash
cd webapp
npm install
npm run dev
```

The frontend will launch on `http://localhost:5173` (default port). You can interact with the UI for recording and transcription management.

### 3. File Management
- **Audio Files**: Stored in the `projects` folder.
- **Transcriptions**: Saved in an SQLite database located in the project root.

---

## Folder Structure

```plaintext
audio_dataset_creator/
├── httpserver.py       # Backend server script
├── projects/           # Directory for audio files
├── webapp/             # Frontend application
│   ├── src/            # UI source code
│   ├── public/         # Static assets
│   └── package.json    # Node.js dependencies
├── db/             	# Frontend application
│   ├── database.db     # SQLite database for transcriptions  
└── README.md           # Project documentation
```

---

## Contributing

We welcome contributions! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add feature-name'`).
4. Push to your branch (`git push origin feature-name`).
5. Submit a pull request.

---

## License

This project is licensed under the MIT License. See `LICENSE` for more details.

---

## Contact

For questions or support, open an issue or contact the maintainer at [yassinevic@gmail.com].
