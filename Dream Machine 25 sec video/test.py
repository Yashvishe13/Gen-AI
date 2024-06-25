import requests
import cv2


# url = 'https://storage.cdn-luma.com/lit_lite_inference_im2vid_v1.0/33f2e3eb-8ba7-4270-85b3-13102b50954d/watermarked_video0740a743206c345f6b7ccbef067c91d82.mp4'

# def download_video(url, output_path):
#     response = requests.get(url, stream=True)
#     if response.status_code == 200:
#         with open(output_path, 'wb') as file:
#             for chunk in response.iter_content(chunk_size=8192):
#                 file.write(chunk)
#         print(f"Download complete: {output_path}")
#     else:
#         print(f"Failed to download video. Status code: {response.status_code}")


# def get_last_frame(video_path, output_image_path):
#     # Open the video file
#     cap = cv2.VideoCapture(video_path)

#     # Get the total number of frames
#     total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

#     # Set the position of the last frame
#     cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)

#     # Read the last frame
#     ret, frame = cap.read()
#     if ret:
#         # Save the last frame as an image
#         cv2.imwrite(output_image_path, frame)
#         print(f"Last frame saved as: {output_image_path}")
#     else:
#         print("Failed to read the last frame.")

#     # Release the video capture object
#     cap.release()

from moviepy.editor import VideoFileClip, concatenate_videoclips

def merge_videos(video1_path, video2_path, output_path):
    # Load the video files
    clip1 = VideoFileClip(video1_path)
    clip2 = VideoFileClip(video2_path)

    # Concatenate the video clips
    final_clip = concatenate_videoclips([clip1, clip2])

    # Write the result to a file
    final_clip.write_videofile(output_path, codec='libx264')

import time
# Example usage
video1_path = 'videos/downloaded_video_1.mp4'
video2_path = 'videos/downloaded_video_2.mp4'
output_path = 'new_merged_video.mp4'
merge_videos(video1_path, video2_path, output_path)
for i in range(2,5):
    video2_path = 'videos/downloaded_video_'+str(i) + ".mp4"
    print(f"merging {output_path} and {video2_path}")
    merge_videos(video1_path, video2_path, output_path)
    video1_path = output_path
    output_path = 'new_merged_video_' + str(i) + ".mp4"
    time.sleep(10)


# # Example usage
# download_video(url, 'downloaded_video.mp4')
# video_path = 'downloaded_video.mp4'
# output_image_path = 'last_frame.png'
# get_last_frame(url, output_image_path)