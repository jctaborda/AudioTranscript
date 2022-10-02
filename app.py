import os.path
from flask import Flask, request, redirect, jsonify, url_for
from werkzeug.utils import secure_filename
import logging
import speech_recognition as sr
from pydub import AudioSegment
from google.cloud import speech, storage
from google.oauth2 import service_account



UPLOAD_FOLDER = 'files'
ALLOWED_EXTENSIONS = {'mp3'}
GOOGLE_BUCKET_NAME = 'audiotranscript_audiofiles'
google_credentials = service_account.Credentials.from_service_account_file('storage-key.json')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

logging.basicConfig(filename='api.log', level=logging.DEBUG, format=f'%(asctime)s - %(levelname)s - %(name)s : %(message)s')


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = '!"$@#½¬Technical-Interview-Code-Challenge-ASDFasdf34535'



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to Google bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client(credentials=google_credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name, timeout=10000)

    app.logger.debug(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )

@app.route('/')
@app.route('/api/v1')
def main():
    return '''This is API v1 to get the desired words from an mp3 file transcript. 
            Limitations = File size < 10 Mb and length < 60 secs 

            Example usage of the API:
'''
        #     <!doctype html>
        #     <title>Upload new File</title>
        #     <h1>Upload new File</h1>
        #     <form method=post enctype=multipart/form-data>
        #         <input type=text name=search_word>
        #         <input type=file name=file>
        #         <input type=submit value=Upload>
        #     </form>
        # '''

@app.route('/api/v1/get_all_info', methods=["GET", "POST"])
def get_all_info():

    if request.method == 'POST':
        # Check if the post method has a file

        if 'file' not in request.files:
            return 'No file part in request'
        file = request.files['file']

        if file.filename == '':
            return 'No selected file'
        if not allowed_file(file.filename):
            return 'File type not allowed'

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            mp3_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(mp3_file)

            r = sr.Recognizer()

            wav_file = mp3_file.replace('.mp3', '.wav')
            app.logger.debug("sound.export mp3 -> wav")
            AudioSegment.from_mp3(mp3_file).set_channels(1).export(wav_file, format='wav') # Convert mp3 to wav

            google_credentials = service_account.Credentials.from_service_account_file('key.json')
            client = speech.SpeechClient(credentials=google_credentials)

            with open(wav_file, 'rb') as audio_file:
                audio = audio_file.read()

            audio = speech.RecognitionAudio(content=audio)
            config = speech.RecognitionConfig(
                language_code='en-US',
                enable_word_time_offsets=True)

            response_from_google = client.recognize(config=config, audio=audio)
            app.logger.debug('******************* Response from Google')

            transcript = ''
            word_count = 0
            search_word = request.form['search_word']
            search_word_count = 0
            search_word_time_list = []

            for result in response_from_google.results:
                best_alternative = result.alternatives[0]
                app.logger.debug('Transcript: {}'.format(best_alternative.transcript))
                transcript += best_alternative.transcript

                for word_info in best_alternative.words:
                    word_count += 1
                    word = word_info.word
                    start_time = word_info.start_time.total_seconds()
                    if word == search_word:
                        search_word_count += 1
                        search_word_time_list.append(str(start_time))
                    #app.logger.info(f'Word Info: {word} - Start time: {start_time} - End time: {end_time}')

            app.logger.info(f'** Transcript: {transcript}')
            app.logger.info(f'** Total word count: {word_count}')
            app.logger.info(f'** Search word: {search_word}')
            app.logger.info(f'** Searched word count: {search_word_count}')
            app.logger.info(f'** Timestamp: {search_word_time_list}')

            result = {'transcript': transcript, 'total_word_count': word_count, 'searched_word': search_word, 'searched_word_count': search_word_count, 'timestamp': search_word_time_list}
            return jsonify(result)

    return redirect('/api/v1')


@app.route('/api/v1/get_logs', methods=['GET'])
@app.route('/api/v2/get_logs', methods=['GET'])
def get_logs():
    with open('api.log', 'r') as log:
        app_log = log.read()
    return app_log

@app.route('/api/v2/get_all_info', methods=["GET", "POST"])
def get_all_info_full():

    if request.method == 'POST':
        # Check if the post method has a file
        if 'file' not in request.files:
            return 'No file part in request'
        file = request.files['file']

        if file.filename == '':
            return 'No selected file'
        if not allowed_file(file.filename):
            return 'File type not allowed'

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            mp3_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(mp3_file)

            r = sr.Recognizer()

            wav_file = mp3_file.replace('.mp3', '.wav')
            app.logger.debug("sound.export mp3 -> wav")
            AudioSegment.from_mp3(mp3_file).set_channels(1).export(wav_file, format='wav') # Convert mp3 to wav

            google_credentials = service_account.Credentials.from_service_account_file('storage-key.json')
            client = speech.SpeechClient(credentials=google_credentials)

            # Send file to google cloud bucket
            destination_blob_name = filename.replace('.mp3','.wav')
            app.logger.debug('********** Upload_blob....')
            upload_blob(GOOGLE_BUCKET_NAME, wav_file, destination_blob_name)
            #gcs_uri = 'gs://audiotranscript_audiofiles/A_Time_for_Choosing.wav'
            gcs_uri = 'gs://' + GOOGLE_BUCKET_NAME + '/' + destination_blob_name
            app.logger.debug(gcs_uri)

            audio = speech.RecognitionAudio(uri=gcs_uri)
            config = speech.RecognitionConfig(
                language_code='en-US',
                enable_word_time_offsets=True)

            # Wait for operation to finish
            app.logger.debug('*********** Client long_running.....')
            operation = client.long_running_recognize(config=config, audio=audio, timeout=10000)
            response_from_google = operation.result(timeout=10000)
            app.logger.debug('******************* Response from Google')
            #delete_blob(bucket_name, destination_blob_name)

            transcript = ''
            word_count = 0
            search_word = request.form['search_word']
            search_word_count = 0
            search_word_time_list = []

            for result in response_from_google.results:
                best_alternative = result.alternatives[0]
                app.logger.debug('Transcript: {}'.format(best_alternative.transcript))
                transcript += best_alternative.transcript

                for word_info in best_alternative.words:
                    word_count += 1
                    word = word_info.word
                    start_time = word_info.start_time.total_seconds()
                    if word == search_word:
                        search_word_count += 1
                        search_word_time_list.append(str(start_time))
                    #app.logger.info(f'Word Info: {word} - Start time: {start_time} - End time: {end_time}')

            app.logger.info(f'** Transcript: {transcript}')
            app.logger.info(f'** Total word count: {word_count}')
            app.logger.info(f'** Search word: {search_word}')
            app.logger.info(f'** Searched word count: {search_word_count}')
            app.logger.info(f'** Timestamp: {search_word_time_list}')

            result = {'transcript': transcript, 'total_word_count': word_count, 'searched_word': search_word, 'searched_word_count': search_word_count, 'timestamp': search_word_time_list}
            return jsonify(result)

    return redirect('/api/v1')

