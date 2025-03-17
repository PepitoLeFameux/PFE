from moviepy import *  # import everythings (variables, classes, methods...) inside moviepy.editor
from PIL import Image
import json
from api_files import upload_file, delete_file, delete_all_files
from api import get_client
import cv2
import os
from conf import RESIZED_FOLDER
from api import generate_content


class VideoManager:
    def __init__(self):
        self.client = get_client()

    def resize_video(self, filename):
        return resize_video(filename, os.path.join(RESIZED_FOLDER, "temp_resized.mp4"))

    def upload_video(self, filename):
        upload_name = upload_file(self.client, filename)

        print(f"Video {filename} uploaded with name {upload_name}")
        return upload_name

    def remove_uploaded_video(self, online_filename):
        delete_file(self.client, online_filename)
        print(f"Video {online_filename} removed successfully")

    def remove_resized_video(self, resized_filename):
        remove_resized_video(resized_filename)

    def generate_content(self, upload_name, task, custom_prompt=''):
        return generate_content(self.client, upload_name, task, custom_prompt)

    def generate_content_from_uri(self, video_uri, task, custom_prompt=''):
        upload_name = self.upload_video(video_uri)
        content = generate_content(self.client, upload_name, task, custom_prompt)
        self.remove_video(upload_name)
        return content




def resize_video(input_path, output_path, width=None, height=480, target_fps=30):
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
    original_fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Original video size: {original_width}x{original_height}, FPS: {original_fps}")

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

    print(f"Resized video size: {new_width}x{new_height}, Target FPS: {target_fps}")

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
    out = cv2.VideoWriter(output_path, fourcc, target_fps, (new_width, new_height))

    # Process each frame while limiting FPS
    frame_interval = max(1, original_fps // target_fps)  # Skip frames if needed
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:  # Write only necessary frames
            resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            out.write(resized_frame)

        frame_count += 1

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
