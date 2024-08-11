# from fastapi import FastAPI
# import datetime
# import webvtt
# from webvtt import Caption, WebVTT

# app = FastAPI()


# @app.post("/get_sync_subs")
# def get_sync(json: dict):
#     data = json
#     # Extract subtitles and language names from the JSON payload
#     sub_one_req = data.get("primary_subtitle")
#     sub_two_req = data.get("secondary_subtitle")
#     sub_one_name = data.get("primary_language")
#     sub_two_name = data.get("secondary_language")
#     # Validate that all required fields are present
#     if sub_one_req is None or sub_two_req is None or sub_one_name is None or sub_two_name is None:
#         raise ValueError(
#             "Missing one or more required fields in the input JSON")
#     # Convert subtitle text to WebVTT objects
#     sub_one = json_to_vtt(sub_one_req)
#     sub_two = json_to_vtt(sub_two_req)
#     # Synchronize the subtitles
#     synced_subs = get_sync_subs(sub_one, sub_two)
#     # Convert the synchronized subtitles back to string format
#     data["primary_subtitle"] = conver_vtt_to_str(synced_subs[0])
#     data["secondary_subtitle"] = conver_vtt_to_str(synced_subs[1])
#     data["status"] = "synchronized"
#     return data


# # Convert subtitle string to WebVTT object
# def json_to_vtt(subtitle_content):
#     vtt = WebVTT()
#     captions = subtitle_content.splitlines()
#     start_time = None
#     end_time = None
#     text_lines = []

#     for line in captions:
#         if '-->' in line:
#             if start_time and end_time:
#                 vtt.captions.append(
#                     Caption(start_time, end_time, "\n".join(text_lines)))
#             start_time, end_time = line.split(' --> ')
#             start_time = start_time.strip() + ".000"
#             end_time = end_time.strip() + ".000"
#             text_lines = []
#         else:
#             text_lines.append(line.strip())

#     if start_time and end_time:
#         vtt.captions.append(
#             Caption(start_time, end_time, "\n".join(text_lines)))

#     return vtt


# # Check if time_b is within the range of time_a
# def inside(time_a, time_b):
#     return time_a[0] <= (time_b[0] + time_b[1]) / 2 <= time_a[1]


# # Synchronize subtitle timings between two lists
# def sync(texts_a, texts_b, times_a, times_b):
#     a = 0
#     while a < len(texts_a):
#         b = 0
#         while b < len(texts_b):
#             if times_b[b][0] > times_a[a][1]:
#                 break
#             if inside(times_a[a], times_b[b]):
#                 if abs(times_a[a][0] - times_a[a][1]) > abs(times_b[b][0] - times_b[b][1]):
#                     times_b[b] = times_a[a]
#                 else:
#                     times_a[a] = times_b[b]
#             b += 1
#         a += 1


# # Convert timestamp string to a float representing seconds
# def make_time_float(x):
#     parts = x.split(":")
#     data = float(parts[0]) * 3600 + float(parts[1]) * \
#         60 + float(parts[2].split('.')[0])
#     return data


# # Extract texts and timings from WebVTT object
# def parse(sub_vtt, texts, times):
#     for caption in sub_vtt:
#         times.append([make_time_float(caption.start),
#                      make_time_float(caption.end)])
#         texts.append(caption.raw_text)


# # Create WebVTT object from texts and timings
# def make_subtitle(texts, times):
#     vtt = WebVTT()
#     for i in range(len(times)):
#         caption = Caption(
#             str(datetime.timedelta(seconds=times[i][0])),
#             str(datetime.timedelta(seconds=times[i][1])),
#             texts[i],
#         )
#         vtt.captions.append(caption)
#     return vtt


# # Synchronize two WebVTT subtitle files
# def get_sync_subs(first_sub, second_sub):
#     texts_a = []
#     texts_b = []
#     times_a = []
#     times_b = []
#     parse(first_sub, texts_a, times_a)
#     parse(second_sub, texts_b, times_b)
#     sync(texts_a, texts_b, times_a, times_b)
#     sync(texts_b, texts_a, times_b, times_a)
#     result_1 = make_subtitle(texts_a, times_a)
#     result_2 = make_subtitle(texts_b, times_b)
#     return [result_1, result_2]


# # Convert WebVTT object to string
# def conver_vtt_to_str(vtt_sub) -> str:
#     output = ["WEBVTT"]
#     counter = 1
#     for caption in vtt_sub:
#         output.append("")
#         output.append(
#             "{}\n{} --> {}".format(counter, caption.start, caption.end)
#         )
#         output.extend(caption.lines)
#         counter += 1

#     return "\n".join(output)



from fastapi import FastAPI
import datetime
import io
import webvtt
from webvtt import Caption, WebVTT

app = FastAPI()

@app.post("/get_sync_subs")
def get_sync(json: dict):
    # Extract subtitle data from the incoming JSON request
    sub_one_req = json["primary_subtitle"]
    sub_two_req = json["secondary_subtitle"]

    # Process subtitle data to VTT format in memory
    sub_one = json_to_vtt(sub_one_req)
    sub_two = json_to_vtt(sub_two_req)

    # Synchronize the two subtitle tracks
    synced_subs = get_sync_subs(sub_one, sub_two)

    # Convert the synchronized subtitles back to string format
    response = {
        "primary_subtitle": convert_vtt_to_str(synced_subs[0]),
        "secondary_subtitle": convert_vtt_to_str(synced_subs[1]),
        "status": "synchronized"
    }
    return response

def json_to_vtt(json_value):
    # Create a file-like object from the subtitle JSON data
    file_like_object = io.StringIO(json_value)
    # Read the subtitles from the in-memory file-like object
    vtt = webvtt.read(file_like_object)
    return vtt

def inside(time_a, time_b):
    # Check if the midpoint of time_b is inside time_a
    return time_a[0] <= (time_b[0] + time_b[1]) / 2 <= time_a[1]

def sync(texts_a, texts_b, times_a, times_b):
    # Synchronize two lists of subtitles based on their timings
    a = 0
    while a < len(texts_a):
        b = 0
        while b < len(texts_b):
            if times_b[b][0] > times_a[a][1]:
                break
            if inside(times_a[a], times_b[b]):
                if abs(times_a[a][0] - times_a[a][1]) > abs(times_b[b][0] - times_b[b][1]):
                    times_b[b] = times_a[a]
                else:
                    times_a[a] = times_b[b]
            b += 1
        a += 1

def make_time_float(x):
    # Convert subtitle time string to float seconds
    parts = x.split(":")
    data = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return data

def parse(sub_vtt, texts, times):
    # Parse the VTT subtitle object to extract text and timing
    for caption in sub_vtt:
        times.append([make_time_float(caption.start), make_time_float(caption.end)])
        texts.append(caption.raw_text)

def make_subtitle(texts, times):
    # Create a WebVTT object from the text and timing data
    vtt = WebVTT()
    for i in range(len(times)):
        caption = Caption(
            str(datetime.timedelta(seconds=times[i][0])) + ".000",
            str(datetime.timedelta(seconds=times[i][1])) + ".000",
            texts[i],
        )
        vtt.captions.append(caption)
    return vtt

def get_sync_subs(first_sub, second_sub):
    # Get synchronized subtitles from two VTT subtitle objects
    texts_a = []
    texts_b = []
    times_a = []
    times_b = []
    parse(first_sub, texts_a, times_a)
    parse(second_sub, texts_b, times_b)
    sync(texts_a, texts_b, times_a, times_b)
    sync(texts_b, texts_a, times_b, times_a)
    result_1 = make_subtitle(texts_a, times_a)
    result_2 = make_subtitle(texts_b, times_b)
    return [result_1, result_2]

def convert_vtt_to_str(vtt_sub) -> str:
    # Convert WebVTT object to a string format
    output = ["WEBVTT"]
    counter = 1
    for caption in vtt_sub:
        output.append("")
        output.append(f"{counter}\n{caption.start} --> {caption.end}")
        output.extend(caption.lines)
        counter += 1
    return "\n".join(output)
