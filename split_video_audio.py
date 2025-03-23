import os
import subprocess

def split_video_audio(input_file, output_dir=None):
    """
    Split a video file into separate video and audio files.
    
    Args:
        input_file (str): Path to the input MP4 file
        output_dir (str, optional): Directory to save output files. Defaults to same directory as input file.
    
    Returns:
        tuple: Paths to the output video and audio files
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Get file name without extension
    input_path, input_filename = os.path.split(input_file)
    filename_without_ext = os.path.splitext(input_filename)[0]
    
    # Set output directory
    if not output_dir:
        output_dir = input_path
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Define output file paths
    video_output = os.path.join(output_dir, f"{filename_without_ext}_video.mp4")
    audio_output = os.path.join(output_dir, f"{filename_without_ext}_audio.wav")
    
    # Extract video (no audio)
    video_cmd = [
        'ffmpeg', '-i', input_file, 
        '-c:v', 'copy', '-an',
        video_output
    ]
    
    # Extract audio
    audio_cmd = [
        'ffmpeg', '-i', input_file,
        '-vn', '-acodec', 'pcm_s16le',
        audio_output
    ]
    
    print(f"Extracting video to {video_output}...")
    subprocess.run(video_cmd, check=True)
    
    print(f"Extracting audio to {audio_output}...")
    subprocess.run(audio_cmd, check=True)
    
    print("Extraction complete!")
    return video_output, audio_output

def process_directory_recursively(input_dir, output_base_dir):
    """
    Recursively process all video files in the input directory and its subdirectories.
    
    Args:
        input_dir (str): Path to the directory containing video files
        output_base_dir (str): Base directory for output files
    
    Returns:
        int: Number of files processed
    """
    processed_count = 0
    
    # Walk through the directory tree
    for root, _, files in os.walk(input_dir):
        # Get the relative path from input_dir
        rel_path = os.path.relpath(root, input_dir)
        
        # Create the corresponding output directory
        if rel_path == '.':
            current_output_dir = output_base_dir
        else:
            current_output_dir = os.path.join(output_base_dir, rel_path)
        
        # Process all mp4 files in the current directory
        for file in files:
            if file.lower().endswith('.mp4'):
                input_file = os.path.join(root, file)
                try:
                    video_file, audio_file = split_video_audio(input_file, current_output_dir)
                    print(f"Processed: {input_file}")
                    processed_count += 1
                except Exception as e:
                    print(f"Error processing {input_file}: {e}")
    
    return processed_count

if __name__ == "__main__":
    input_dir = "dataset/Audio-Visual/VA test videos-20241101T063102Z-002/VA test videos/Laptop camera"
    output_dir = "dataset/Audio-Visual/Split_test"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        print(f"Starting recursive processing of videos in {input_dir}")
        count = process_directory_recursively(input_dir, output_dir)
        print(f"Finished processing {count} video files")
    except Exception as e:
        print(f"Error: {e}")
