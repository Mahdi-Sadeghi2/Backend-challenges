import webvtt
import pandas as pd
from datetime import timedelta


def to_timedelta(time_str):
    """Convert a webvtt time string to a timedelta object."""
    hours, minutes, seconds_milliseconds = time_str.split(':')
    seconds, milliseconds = seconds_milliseconds.split('.')
    return timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds), milliseconds=int(milliseconds))


def to_vtt_timestamp(td):
    """Convert a timedelta object back to a webvtt timestamp string."""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"


def sync_subtitles_to_csv(base_file, target_file, output_csv):
    base_vtt = webvtt.read(base_file)
    target_vtt = webvtt.read(target_file)

    # Prepare a list to hold the synchronized data
    synced_data = []

    # Assuming both files have the same number of captions
    for base_caption, target_caption in zip(base_vtt, target_vtt):
        # Calculate the shift based on the target caption's start time
        shift = to_timedelta(target_caption.start) - \
            to_timedelta(base_caption.start)

        # Apply the shift to the base caption
        new_start = to_timedelta(base_caption.start) + shift

        # Append the synchronized caption to the list
        synced_data.append({
            'start': to_vtt_timestamp(new_start),
            'english_subtitle': base_caption.text,
            'translation': target_caption.text
        })

    # Create a DataFrame and save to CSV
    df = pd.DataFrame(synced_data)
    df.to_csv(output_csv, index=False, columns=[
              'start', 'english_subtitle', 'translation'])


if __name__ == "__main__":
    base_vtt_file = 'en_70105212.vtt'  # The subtitle you want to adjust
    target_vtt_file = 'de_70105212.vtt'  # The reference subtitle
    output_csv_file = 'synchronized_subtitles.csv'  # The finla CSV file

    sync_subtitles_to_csv(base_vtt_file, target_vtt_file, output_csv_file)
