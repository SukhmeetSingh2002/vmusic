import platform
import numpy as np
import time
import librosa
import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame  # noqa

# Constants
CHUNK = 1024
RATE = 44100


def initialize_pygame(filename):
    # Initialize Pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(filename)


def get_initial_brightness():
    brightness_path = "/sys/class/leds/dell::kbd_backlight/brightness"
    caplock_path = "/sys/class/leds/input3::capslock/brightness"
    screen_path = "/sys/class/backlight/intel_backlight/brightness"

    # Read the initial brightness values
    with open(brightness_path, "r") as f:
        initial_backlight = int(f.read().strip())
    with open(caplock_path, "r") as f:
        initial_caplock = int(f.read().strip())
    with open(screen_path, "r") as f:
        initial_screen = int(f.read().strip())

    return initial_backlight, initial_caplock, initial_screen


def set_backlight_brightness(
    backlight_level, caplock_level, screen_level, change_screen
):
    # Check if the current operating system is Linux
    if platform.system() != "Linux":
        # print("Brightness change is not supported on this operating system.")
        return

    brightness_path = "/sys/class/leds/dell::kbd_backlight/brightness"
    caplock_path = "/sys/class/leds/input3::capslock/brightness"
    screen_path = "/sys/class/backlight/intel_backlight/brightness"

    # Check if the files exist
    if not os.path.exists(brightness_path):
        print(f"The file {brightness_path} does not exist.")
        return
    if not os.path.exists(caplock_path):
        print(f"The file {caplock_path} does not exist.")
        return
    if change_screen and not os.path.exists(screen_path):
        print(f"The file {screen_path} does not exist.")
        return

    os.system(f"echo {backlight_level} | sudo tee {brightness_path} > /dev/null &")
    os.system(f"echo {caplock_level} | sudo tee {caplock_path} > /dev/null &")
    if change_screen:
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


def process_audio(filename, change_screen):
    # Get the initial brightness values
    initial_backlight, initial_caplock, initial_screen = get_initial_brightness()

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
            set_backlight_brightness(
                backlight_level, caplock_level, screen_level, change_screen
            )
            end_time_backlight_update = time.time()
            print(
                f"Time: {timer:.2f}, Energy: {rms[i]:.4f}, Time taken to update:",
                f"{end_time_backlight_update - start_time_backlight_update:.4f} seconds",
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

        # Reset the brightness values to their initial state
        print("Reseting brightness values")
        set_backlight_brightness(
            initial_backlight, initial_caplock, initial_screen, change_screen
        )


def run_visualizer(filename, change_screen):
    print(f"Running visualizer for {filename}")
    initialize_pygame(filename)
    process_audio(filename, change_screen)
