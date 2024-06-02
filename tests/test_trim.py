import os
from pydub import AudioSegment
from vmusic.trim import trim_audio


def test_trim_audio():
    # Create a 5-second silent audio file for testing
    test_audio = AudioSegment.silent(duration=5000)  # duration in milliseconds
    test_filename = "test_audio.mp3"
    test_audio.export(test_filename, format="mp3")

    # Trim the test audio file to the first 2 seconds
    trimmed_filename = trim_audio(test_filename, 0, 2)

    # Load the trimmed audio file
    trimmed_audio = AudioSegment.from_file(trimmed_filename)

    # Check that the duration of the trimmed audio file is 2 seconds
    assert len(trimmed_audio) == 2000  # duration in milliseconds

    # Clean up the test and trimmed audio files
    os.remove(test_filename)
    os.remove(trimmed_filename)
