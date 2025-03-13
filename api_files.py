from google import genai
import time
import os


def upload_file(client, filename):
    print("Uploading file...")
    video_file = client.files.upload(file=filename)
    print(f"Completed upload: {video_file.uri}")

    # Check whether the file is ready to be used.
    while video_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(1)
        video_file = client.files.get(name=video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)

    print('Done')
    print('Video name:', video_file.name)
    return video_file.name


def delete_file(client, filename):
    client.files.delete(name=filename)


def delete_all_files(client):
    print('My files:')
    for f in client.files.list():
        print(" ", f'{f.name}: {f.uri}', end='')
        client.files.delete(name=f.name)
        print(" DELETED")
