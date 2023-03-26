import threading  # for creating a worker thread
import io  # for handling binary data
import json
import os  # for directory management
import PySimpleGUI as sg  # for creating a GUI
from PIL import Image  # for image processing
import booru_scraper as bs  # for scraping image data from websites


def get_directory_path():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)['download_directory']
    except:
        return ''

download_directory = get_directory_path()

# number of downloaded images, initialized from the scraper module
try:
    downloaded_soyjaks = bs.number_to_start_with(download_directory)
except:
    downloaded_soyjaks = 0

# total number of available images, initialized from the scraper module
max_online_soyjaks = bs.max_online_soyjaks()

# Layout of the GUI
sg.theme('DarkGray15')

# LEFT COLUMN (download controls)
left_column = [
    [sg.Text(f'Downloaded: {downloaded_soyjaks:,d}',
             key='-DOWNLOADED_SOYJAKS-')],
    [sg.Text(
        f'Available Online: {max_online_soyjaks:,d}', key='-ONLINE_SOYJAKS-')],
    [sg.FolderBrowse('Download Directory'),
     sg.Input(f'{get_directory_path()}', key='-DOWNLOAD_DIR-', size=(10, 1))],
    [sg.Button('Start', key='-START-'), sg.Button('Stop', key='-STOP-')],
]
left_col = sg.Column(left_column, element_justification='l', size=(250, None))

# RIGHT COLUMN (image thumbnail)
right_column = [[sg.Image(filename='', key='-THUMB-')]]
right_col = sg.Column(
    right_column, element_justification='r', size=(300, None))

# Combine the columns into a layout
layout = [[left_col, right_col]]

# Create the window
window = sg.Window('Soyjak Downloader GUI', layout, size=(
    600, 300), resizable=False, finalize=True)


# Function for the download worker thread
def download_worker(download_directory):
    global downloaded_soyjaks

    while downloaded_soyjaks < max_online_soyjaks:

        # Download the image
        downloaded_soyjaks += 1
        post = bs.BooruPost(downloaded_soyjaks)
        post.download(download_directory)

        # Update the downloaded image count
        window['-DOWNLOADED_SOYJAKS-'].update(
            f'Downloaded: {downloaded_soyjaks:,d}')

        # Update the thumbnail image in the GUI
        if post.file_ext in ['jpg', 'jpeg', 'png', 'gif']:
            recent_image = f'{download_directory}/Soyjak #{downloaded_soyjaks}.{post.file_ext}'
            img = Image.open(recent_image)
            img.thumbnail((300, 300))
            resized_img_bytes = io.BytesIO()
            img.save(resized_img_bytes, format=f'{post.file_ext.upper()}')
            window.write_event_value(
                '-UPDATE_THUMB-', resized_img_bytes.getvalue())


# Save the user's download directory
def save_directory_path(download_directory):
    with open('config.json', 'w') as f:
        json.dump({'download_directory': download_directory}, f)


# Program start
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break

    elif event == '-START-':
        # Check if user has previous download directory, if not, save current one.
        save_directory_path(values['-DOWNLOAD_DIR-'])
        download_directory = get_directory_path()
        if download_directory == '':
            sg.popup('Please select a download directory.')
            continue

        # Start the download worker thread
        thread = threading.Thread(
            target=download_worker, args=(download_directory,))
        thread.start()

    elif event == '-UPDATE_THUMB-':

        # Update the thumbnail image in the GUI
        window['-THUMB-'].update(data=values[event])

    elif event == '-STOP-':

        # Stop the download worker thread
        thread.join()

# Close the window
window.close
