from pydub import AudioSegment
import os


def trim_audio(filename, start_sec, end_sec):
    # Load the audio file
    audio = AudioSegment.from_file(filename)

    # Trim the audio to the specified start and end seconds
    trimmed_audio = audio[
        start_sec * 1000 : end_sec * 1000
    ]  # convert seconds to milliseconds

    # Save the trimmed audio to a new file in the specified directory
    trimmed_filename = os.path.join(
        "/home/sukhmeet/tests/vmusic/trimmed_music",
        f"trimmed_{os.path.basename(filename)}",
    )
    trimmed_audio.export(trimmed_filename, format="mp3")

    return trimmed_filename
