import numpy as np
import pygame
import time
import threading
import librosa
import os

# Constants
CHUNK = 1024
RATE = 44100


def initialize_pygame(filename):
    # Initialize Pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(filename)


def set_backlight_brightness(backlight_level, caplock_level, screen_level):
    brightness_path = "/sys/class/leds/dell::kbd_backlight/brightness"
    caplock_path = "/sys/class/leds/input3::capslock/brightness"
    screen_path = "/sys/class/backlight/intel_backlight/brightness"

    os.system(f"echo {backlight_level} | sudo tee {brightness_path} > /dev/null &")
    os.system(f"echo {caplock_level} | sudo tee {caplock_path} > /dev/null &")
    os.system(f"echo {screen_level} | sudo tee {screen_path} > /dev/null &")


def load_audio_file(filename):
    # Load the audio file with librosa
    y, sr = librosa.load(filename)

    # Compute RMS energy
    rms = librosa.feature.rms(y=y, frame_length=CHUNK, hop_length=CHUNK)[0]
    times = librosa.times_like(rms, sr=sr, hop_length=CHUNK)

    # Get the total duration of the music file
    total_duration = librosa.get_duration(y=y, sr=sr)

    return y, sr, rms, times, total_duration


def play_music():
    pygame.mixer.music.play()


def stop_music():
    pygame.mixer.music.stop()
    pygame.mixer.quit()


def process_audio(filename):
    y, sr, rms, times, total_duration = load_audio_file(filename)

    # Create a timer that triggers at regular intervals
    timer_interval = total_duration / len(times)
    timer = 0
    print(f"Total duration: {total_duration:.2f} seconds")
    print(f"times: {times}")

    try:
        # Play music
        play_music()

        print("Listening to music...")

        start_time = time.time()
        count_of_updates = 0

        for i in range(len(times)):
            # Map RMS energy to brightness
            backlight_level = int(np.interp(rms[i], [rms.min(), rms.max()], [0, 2]))
            caplock_level = int(np.interp(rms[i], [rms.min(), rms.max()], [0, 2]))
            screen_level = int(np.interp(rms[i], [rms.min(), rms.max()], [960, 96000]))

            # Set backlight brightness
            start_time_backlight_update = time.time()
            set_backlight_brightness(backlight_level, caplock_level, screen_level)
            end_time_backlight_update = time.time()
            print(
                f"Time: {timer:.2f}, timer_interval: {timer_interval:.2f}, \
                Energy: {rms[i]:.4f}, Time taken to update backlight: \
                {end_time_backlight_update - start_time_backlight_update:.4f} seconds",
                "count_of_updates: ",
                count_of_updates,
                end="\r",
            )

            time_taken_to_update_backlight = (
                end_time_backlight_update - start_time_backlight_update
            )
            if i < len(times) - 1:
                timer_interval = times[i + 1] - times[i]

            time_to_sleep = timer_interval - time_taken_to_update_backlight

            if time_to_sleep < 0:
                print(f"Time to sleep is negative: {time_to_sleep:.4f} seconds")
                time_to_sleep = 0

            # Wait for the next timer interval
            time.sleep(time_to_sleep)

            # Update the timer
            timer += time_to_sleep
            count_of_updates += 1

        end_time = time.time()

        print(f"Total time: {end_time - start_time:.2f} seconds")

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        # Clean up
        stop_music()


def run_visualizer(filename):
    print(f"Running visualizer for {filename}")
    initialize_pygame(filename)
    # Create and start a new thread for the audio processing
    audio_thread = threading.Thread(target=process_audio, args=(filename,))
    audio_thread.start()
    audio_thread.join()
