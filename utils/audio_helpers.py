import os
import tempfile
import numpy as np
from pydub import AudioSegment
import streamlit as st

# Audio processing utilities for StudyMateZ

def save_uploaded_audio(uploaded_file):
    """Save an uploaded audio file to a temporary location and return the path.
    
    Args:
        uploaded_file: The uploaded audio file from Streamlit's file_uploader
        
    Returns:
        str: Path to the saved temporary file
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    
    # Save the uploaded file
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return temp_path

def convert_audio_format(input_path, output_format="wav"):
    """Convert audio to the specified format.
    
    Args:
        input_path: Path to the input audio file
        output_format: Target format (default: wav)
        
    Returns:
        str: Path to the converted audio file
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_file(input_path)
        
        # Create output path
        output_path = os.path.splitext(input_path)[0] + "." + output_format
        
        # Export in the target format
        audio.export(output_path, format=output_format)
        
        return output_path
    except Exception as e:
        st.error(f"Error converting audio format: {str(e)}")
        return input_path

def normalize_audio(input_path):
    """Normalize audio volume.
    
    Args:
        input_path: Path to the input audio file
        
    Returns:
        str: Path to the normalized audio file
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_file(input_path)
        
        # Normalize to -20dB
        normalized_audio = audio.normalize(headroom=-20.0)
        
        # Create output path
        output_path = os.path.splitext(input_path)[0] + "_normalized" + os.path.splitext(input_path)[1]
        
        # Export normalized audio
        normalized_audio.export(output_path, format=os.path.splitext(input_path)[1][1:])
        
        return output_path
    except Exception as e:
        st.error(f"Error normalizing audio: {str(e)}")
        return input_path

def trim_silence(input_path, silence_threshold=-50.0, min_silence_len=500):
    """Trim silence from the beginning and end of an audio file.
    
    Args:
        input_path: Path to the input audio file
        silence_threshold: Silence threshold in dB (default: -50.0)
        min_silence_len: Minimum silence length in ms (default: 500)
        
    Returns:
        str: Path to the trimmed audio file
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_file(input_path)
        
        # Trim silence
        start_trim = detect_leading_silence(audio, silence_threshold)
        end_trim = detect_leading_silence(audio.reverse(), silence_threshold)
        
        duration = len(audio)
        trimmed_audio = audio[start_trim:duration-end_trim]
        
        # Create output path
        output_path = os.path.splitext(input_path)[0] + "_trimmed" + os.path.splitext(input_path)[1]
        
        # Export trimmed audio
        trimmed_audio.export(output_path, format=os.path.splitext(input_path)[1][1:])
        
        return output_path
    except Exception as e:
        st.error(f"Error trimming silence: {str(e)}")
        return input_path

def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    """Detect leading silence in an audio segment.
    
    Args:
        sound: AudioSegment to analyze
        silence_threshold: Silence threshold in dB (default: -50.0)
        chunk_size: Size of chunks to analyze in ms (default: 10)
        
    Returns:
        int: Trim amount in ms
    """
    trim_ms = 0
    while trim_ms < len(sound) and sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold:
        trim_ms += chunk_size
    return trim_ms

def get_audio_duration(input_path):
    """Get the duration of an audio file in seconds.
    
    Args:
        input_path: Path to the audio file
        
    Returns:
        float: Duration in seconds
    """
    try:
        audio = AudioSegment.from_file(input_path)
        return len(audio) / 1000.0  # Convert ms to seconds
    except Exception as e:
        st.error(f"Error getting audio duration: {str(e)}")
        return 0.0

def create_audio_player(audio_path, format="audio/wav"):
    """Create an HTML audio player for the given audio file.
    
    Args:
        audio_path: Path to the audio file
        format: MIME type of the audio (default: audio/wav)
        
    Returns:
        str: HTML audio player code
    """
    try:
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        
        return st.audio(audio_bytes, format=format)
    except Exception as e:
        st.error(f"Error creating audio player: {str(e)}")
        return None