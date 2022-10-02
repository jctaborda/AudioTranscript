# AudioTranscript

This project implements an API to get the transcript form mp3 files. In its first version it is able to transcribe small files and with version2 you can get transcriptions of big files using Google services.


## Features

- Import a mp3 file and get full text transcription
- Returns the total amount of words in the file
- You can send a word to search in the audio
- Returns how many times that word is in the file and the timestamps where the word appears


## Tech

AudioTranscript uses technology like:

- Python
- Flask
- Google Speech
- Google Storage

## Installation

- clone repository
- pip install requirements.txt
- create a Google service account for your project and a storage account.
- create two files (key.json and storage-key.jcon) with your information (templates provided)


## Usage
Method POST http://YOUR-SERVER/api/v2/get_all_info
Request example:

            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File</h1>
            <form method=post enctype=multipart/form-data>
                <input type=file name=file>
                <input type=submit value=Upload>
            </form>

Response:

    {
    'transcript': transcript, 
    'total_word_count': word_count, 
    'searched_word': search_word, 
    'searched_word_count': search_word_count, 
    'timestamp': search_word_time_list
        
    }


## Warning
This code uploads the mp3 file to the server and converts it to a wav file before sending it to google for transcription but it never deletes this files. You will need to change the code if you want to delete them.