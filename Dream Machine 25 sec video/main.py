import asyncio

from util import dreamMachineMake, refreshDreamMachine
from moviepy.editor import VideoFileClip, concatenate_videoclips

import requests
import cv2

def download_video(url, output_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Download complete: {output_path}")
    else:
        print(f"Failed to download video. Status code: {response.status_code}")

def get_last_frame(video_path, output_image_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Get the total number of frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Set the position of the last frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)

    # Read the last frame
    ret, frame = cap.read()
    if ret:
        # Save the last frame as an image
        cv2.imwrite(output_image_path, frame)
        print(f"Last frame saved as: {output_image_path}")
    else:
        print("Failed to read the last frame.")

    # Release the video capture object
    cap.release()

def merge_videos(video1_path, video2_path, output_path):
    # Load the video files
    clip1 = VideoFileClip(video1_path)
    clip2 = VideoFileClip(video2_path)

    # Concatenate the video clips
    final_clip = concatenate_videoclips([clip1, clip2])

    # Write the result to a file
    final_clip.write_videofile(output_path, codec='libx264')

# Your access_token
# iterations = 1
# image_file = "img/meinv.png"

def generate_video(image_file):
    access_token = ""
    prompt = ""
    # The image path can be empty
    make_json = dreamMachineMake(prompt, access_token, image_file)
    print(make_json)
    task_id = make_json[0]["id"]
    while True:
        response_json = refreshDreamMachine(access_token)

        for it in response_json:
            if it["id"] == task_id:
                print(f"proceeding state {it['state']}")
                if it['video']:
                    video_link = it['video']['url']
                    print(f"New video link: {video_link}")
                    if video_link != None:
                        return video_link

iterations = 1
image_file = "img/meme.jpg"
link = generate_video(image_file)
while iterations < 5:
    video_output = "videos/downloaded_video_" + str(iterations) + ".mp4"
    output_image_path = "last_frames/last_frame_" + str(iterations) + ".png"
    print("downloading_video...")
    download_video(link, video_output)
    print("saving_last_frame...")
    get_last_frame(video_output, output_image_path)
    print("generating new video...")
    link = generate_video(output_image_path)
    iterations += 1