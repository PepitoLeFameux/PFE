from moviepy import *  # import everythings (variables, classes, methods...) inside moviepy.editor
from PIL import Image
from conf import THUMBNAIL_FOLDER, RESIZED_FOLDER, JSON_LOCATION
import json
from api_files import upload_file, delete_file, delete_all_files
from api import get_client
import google.generativeai as genai
import cv2
import os
from conf import RESIZED_FOLDER
from api import generate_content


class VideoManager:
    def __init__(self):
        self.client = get_client()
        self.videos = []
        self.load_videos()
        self.update_local_video_data()

    def update_local_video_data(self):
        video_upload_names = [video['upload_name'] for video in self.videos]
        for video in self.read_json():
            if video['upload_name'] not in video_upload_names:
                self.remove_video(video['upload_name'])

    def load_videos(self):
        files = genai.list_files()
        for file in files:
            if file.mime_type == 'video/mp4':
                self.videos.append({
                    'upload_name': file.name,
                    'thumbnail_filename': os.path.join(THUMBNAIL_FOLDER, os.path.split(file.name)[-1]) + ".jpg"
                })

    def read_json(self):
        if not os.path.exists(JSON_LOCATION):
            with open(JSON_LOCATION, mode='w') as json_file:
                json.dump([], json_file)

        with open(JSON_LOCATION, mode='r') as json_file:
            return json.load(json_file)

    def update_json(self):
        with open(JSON_LOCATION, mode='w') as json_file:
            json_file.write(json.dumps(self.videos, indent=2))

    def upload_video(self, filename):
        fps, n_frames, duration = get_video_stats(filename)
        with open(JSON_LOCATION, 'r') as f:
            self.videos = list(json.load(f))

        resized_filename = resize_video(filename, os.path.join(RESIZED_FOLDER, "temp_resized.mp4"))

        print(os.path.join(RESIZED_FOLDER, '.'.join(os.path.split(filename)[1].split('.')[:-1])) + ".mp4")
        upload_name = upload_file(self.client, resized_filename)
        generate_thumbnail(resized_filename, os.path.join(THUMBNAIL_FOLDER, os.path.split(upload_name)[-1]) + ".jpg")

        self.load_videos()
        self.update_json()

        print(f"Video {filename} uploaded with name {upload_name}")

    def remove_video(self, online_filename):
        for i, video in enumerate(self.videos):
            if video['upload_name'] == online_filename:
                print(video['thumbnail_filename'])
                remove_thumbnail(video['thumbnail_filename'])
                delete_file(self.client, video['upload_name'])
                self.videos.pop(i)
                print(f"Video {video['upload_name']} removed successfully")
        self.update_json()

    def remove_video_by_idx(self, idx):
        upload_name = self.videos[idx]['upload_name']
        self.remove_video(upload_name)

    def remove_all_videos(self):
        for video in self.videos:
            remove_thumbnail(video['thumbnail_filename'])
            delete_file(self.client, video['upload_name'])
            print(f"Video {video['upload_name']} removed successfully")
        self.update_json()

    def get_nth_video_upload_name(self, n):
        return self.videos[n]['upload_name']

    def show_all_videos(self):
        for i, video in enumerate(self.videos):
            print(f"Video {i}:", json.dumps(video, indent=3))

    def get_video_info(self, idx):
        return self.videos[idx]

    def generate_content_nth_video(self, n, task, custom_prompt=''):
        video_file_name = self.get_nth_video_upload_name(n)
        return generate_content(self.client, video_file_name, task, custom_prompt='')


def get_video_stats(filename):
    clip = VideoFileClip(filename)

    fbs = clip.reader.fps  # return number of frame per second
    n_frames = clip.reader.n_frames  # return number of frame in the video
    duration = clip.duration  # return duration of the video in second

    clip.close()

    return fbs, n_frames, duration


def generate_thumbnail(video_filename, new_filename):
    in_filename = video_filename
    thumbnail_folder = THUMBNAIL_FOLDER

    if not os.path.exists(thumbnail_folder):
        os.makedirs(thumbnail_folder)

    clip = VideoFileClip(in_filename)

    frame_at_second = int(clip.duration / 2)
    frame = clip.get_frame(frame_at_second)
    new_image_filepath = new_filename
    new_image = Image.fromarray(frame)
    new_image.save(new_image_filepath)
    clip.close()
    return new_image_filepath


def remove_thumbnail(filename):
    try:
        os.remove(filename)
    except OSError:
        print("Thumbnail not found")
        pass


def resize_video(input_path, output_path, width=None, height=480):
    if not os.path.exists(RESIZED_FOLDER):
        os.makedirs(RESIZED_FOLDER)

    # Open the video file
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {input_path}")
        return

    # Get original dimensions and frame rate
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    cap.release()

    print(f"Original video size: {original_width}x{original_height}, FPS: {fps}")

    if height is not None and original_height < height:
        print(f"Original height ({original_height}) is smaller than target height ({height}). Copying file instead...")
        import shutil
        shutil.copy(input_path, output_path)
        print(f"Video copied successfully. Saved as '{output_path}'.")
        return output_path

    # Determine new size while maintaining aspect ratio if needed
    if width is None and height is None:
        new_width, new_height = original_width, original_height
    elif width is None:
        new_width = int(original_width * (height / original_height))
        new_height = height
    elif height is None:
        new_height = int(original_height * (width / original_width))
        new_width = width
    else:
        new_width, new_height = width, height

    print(f"Resized video size: {new_width}x{new_height}")

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
    out = cv2.VideoWriter(output_path, fourcc, fps, (new_width, new_height))

    # Process each frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize the frame
        resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # Write the resized frame
        out.write(resized_frame)

    # Release resources
    cap.release()
    out.release()
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        print(f"Video resized successfully. Saved as '{output_path}'.")
        return output_path
    else:
        print(f"Error: Failed to create valid output video at '{output_path}'.")
        return None



def remove_resized_video(video_path):
    os.remove(video_path)

# manager = VideoManager()
# manager.remove_all_videos()
# manager.upload_video("videos/PostsOfCats-1888852858608521343-01.mp4")
# name = manager.get_nth_video_upload_name(0)
# manager.show_all_videos()
# manager.remove_video(name)
# manager.show_all_videos()
