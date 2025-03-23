import os
import json
from tqdm import tqdm
import whisper


def transcribe_audio_with_whisper(audio_file, language="en"):
    """
    Transcribe an audio file to text using OpenAI's Whisper model locally.
    
    Args:
        audio_file (str): Path to the audio file
        language (str): Language code for transcription (default: en)
        
    Returns:
        str: Transcribed text
    """
    print(f"Processing: {audio_file}")
    
    try:
        # Check if audio file exists
        if not os.path.exists(audio_file):
            print(f"Error: Audio file {audio_file} not found")
            return ""
        
        # Load the model (will download on first run)
        print("Loading Whisper model (may download if first run)...")
        model = whisper.load_model("tiny")
        
        # Transcribe audio
        print(f"Transcribing {audio_file}...")
        result = model.transcribe(audio_file, language=language)
        
        transcription = result["text"]
        print(f"Transcription successful: {transcription[:50]}...")
        return transcription
            
    except Exception as e:
        print(f"Unexpected error during transcription: {e}")
        return ""

def process_audio_directory(input_dir, output_dir):
    """
    Process all audio files in a directory and save transcriptions.
    
    Args:
        input_dir (str): Directory containing audio files
        output_dir (str): Directory to save transcription files
        
    Returns:
        int: Number of files processed
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    processed_count = 0
    
    # Find all audio files in the directory
    audio_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('_audio.wav', '.mp3', '.aac', '.flac')):
                audio_files.append((root, file))
    
    print(f"Found {len(audio_files)} audio files to process")
    
    # Process all audio files with progress bar
    for root, file in tqdm(audio_files, desc="Transcribing"):
        rel_path = os.path.relpath(root, input_dir)
        
        # Create corresponding output directory
        if rel_path == '.':
            current_output_dir = output_dir
        else:
            current_output_dir = os.path.join(output_dir, rel_path)
            
        if not os.path.exists(current_output_dir):
            os.makedirs(current_output_dir)
        
        input_file = os.path.join(root, file)
        
        # Get filename without extension
        filename_without_ext = os.path.splitext(file)[0]
        output_file = os.path.join(current_output_dir, f"{filename_without_ext}.txt")
        
        try:
            # Skip if already transcribed
            if os.path.exists(output_file):
                print(f"Skipping {input_file} (already transcribed)")
                processed_count += 1
                continue
                
            # Transcribe audio to text
            transcription = transcribe_audio_with_whisper(input_file)
            
            if transcription:
                # Save transcription to file
                with open(output_file, 'w') as f:
                    f.write(transcription)
                
                # Also save as JSON for additional metadata
                json_output = os.path.join(current_output_dir, f"{filename_without_ext}.json")
                with open(json_output, 'w') as f:
                    json.dump({
                        'audio_file': input_file,
                        'transcription': transcription,
                        'language': 'en'
                    }, f, indent=2)
                
                processed_count += 1
                
        except Exception as e:
            print(f"Error processing {input_file}: {e}")
    
    return processed_count

if __name__ == "__main__":
    # Directory containing audio files (could be the output from split_video_audio.py)
    input_dir = "dataset/Audio-Visual/Split_train"
    output_dir = input_dir
    
    print(f"Starting transcription of audio files in {input_dir}")
    count = process_audio_directory(input_dir, output_dir)
    print(f"Finished transcribing {count} audio files")
