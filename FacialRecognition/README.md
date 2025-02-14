# Face Recognition POC

This is a POC (Proof of Concept) for a facial authentication system built with Python that allows users to register and login using facial recognition. The system supports both dlib and face_recognition libraries for facial detection and recognition.
## Prerequisites

- Python 3.7+ 
- pip (Python package manager)
- CMake (required for dlib)

## Installation Prerequisites

### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install python3-pip cmake
```

### On Windows:
1. Install Python from python.org
2. Install CMake from cmake.org

## Environment Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
```

2. Activate the virtual environment:
* On Windows:
```bash
.\venv\Scripts\activate
```

* On Unix or MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place the images you want to analyze in the `images/` folder
2. Run the script:
```bash
python face_recognition_poc.py
```

## Notes
* Make sure your webcam is working properly
* Good lighting conditions will improve recognition accuracy
* User data and images are stored locally

#### By Axel Ayala Siles