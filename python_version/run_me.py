import pandas as pd
import subprocess
import os
import shutil
import timeit
import threading


def cut_video(data: pd.Series, tmp_dir: str):
    """
    A function that cuts video according to pd.Series values.
    This function will execute following command using subprocess.
    ffmpeg -ss 00:01:00 -to 00:02:00  -i input.mp4 -c copy output.mp4

    :param data: a pandas.Series that represents the data of current video clip
    :param tmp_dir: a string that represents tmp_dir
    """
    start_str = data['start']
    end_str = data['end']
    save_name = data['save_name']
    out_file_name = os.path.join(tmp_dir, save_name)
    subprocess.check_output([
        "ffmpeg",
        "-ss",
        start_str,
        "-to",
        end_str,
        "-i",
        "../OriginalVideo.mp4",
        "-c",
        "copy",
        out_file_name, "-y"],
        stderr=subprocess.STDOUT)


def change_video_speed(video_name: str, speed: float):
    """
A function that changes video speed into designated speed.
    This will generate a video with %03ds.mp4.
    Example, if 000.mp4 was processed, it will be saved as 000s.mp4.

    The problem with ffmpeg is that ffmpeg can only go as low as 0.5.
    So in order for us to achieve lower speed than 0.5,
    it means we have to process it multiple times.
    For example, we have 0.123 as speed.

    This means the following: 0.123 = 0.5 * 0.5 * 0.5 * 0.984.
    So, the original video should go 0.5, then 0.5 of 0.5, and so on...

    This function will execute following command using subprocess.
    ffmpeg -i Break0.mp4 -vf "setpts=(PTS-STARTPTS)/2.5" -af atempo=2.5 a.mp4

    :param video_name: a string that represents video's name to process.
    :param speed: a float value that represents how fast the video should go.
    """
    if speed < 0.5:  # if speed was 0.5, we need to slow it multiple times
        cur_speed = speed
        # for storing all numbers that it needed for making the wanted speed
        multiplier_list = list()
        while (cur_speed < 0.5):
            cur_speed = cur_speed / 0.5
            multiplier_list.append(0.5)
        multiplier_list.append(cur_speed)
        # The formula will be like this
        # 1. Make 0.5 times slower and name it s_0.mp4
        # 2. s_i would be s_i-1 slowed in the speed_i
        # 3. Iterate it over and over

        operation_count = 0  # count operations
        # Make s_0.mp4 from original video
        subprocess.check_output([
            "ffmpeg",
            "-i",
            video_name,
            "-vf",
            "setpts=(PTS-STARTPTS)/%f" % 0.5,
            "-af",
            "atempo=%f" % 0.5,
            video_name.replace(".mp4", "s_0.mp4"),
            "-y"],
            stderr=subprocess.STDOUT)
        operation_count += 1

        for speed in multiplier_list[1:]:  # iterate and slow s_i-1
            subprocess.check_output([
                "ffmpeg",
                "-i",
                video_name.replace(".mp4", "s_%d.mp4" % (operation_count - 1)),
                "-vf",
                "setpts=(PTS-STARTPTS)/%f" % speed,
                "-af",
                "atempo=%f" % speed,
                video_name.replace(".mp4", "s_%d.mp4" % operation_count),
                "-y"],
                stderr=subprocess.STDOUT)
            operation_count += 1
            # When done slowing, delete the old version s_i-1
        # Save the final video as s.mp4
        os.rename(video_name.replace(".mp4", "s_%d.mp4" %
                                     (operation_count - 1)),
                  video_name.replace(".mp4", "s.mp4"))
    else:  # if speed was faster than 0.5, just apply the speed
        subprocess.check_output([
        "ffmpeg",
        "-i",
        video_name,
        "-vf",
        "setpts=(PTS-STARTPTS)/%f" % speed,
        "-af",
        "atempo=%f" %speed,
        video_name.replace(".mp4", "s.mp4"),
        "-y"],
        stderr=subprocess.STDOUT)


def add_caption(video_name: str, country_name: str, value: str,
                font_dir: str, font_color: str, font_size: int,
                box_enabled: bool, box_opacity: float, box_color: str,
                box_padding: int, text_position: tuple):
    """
    A function that adds caption to the video.
    This will generate a video with %03df.mp4.
    Example, if 000s.mp4 was processed, it will be saved as 000f.mp4.

    This function will execute following command using subprocess.
    ffmpeg -i 000s.mp4 -vf "drawtext=fontfile=/path/to/font.ttf:text='Stack Overflow':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=(h-text_h)/2" -codec:a copy 000f.mp4

    :param video_name: a string that represents video's name to process.
    :param country_name: a string that represents country's name.
    :param value: a string that represents value of that country.
    :param font_dir: a string that represents directory that leads to
                     the font that current caption will be using.
    :param font_color: a string that represents color Ex) white.
    :param font_size: a int value that represents font size.
    :param box_enabled: a boolean that decides  whether or not to use textbox.
    :param box_opacity: a float that sets box's opacity:
                        0 means it is it is not transparent at all.
    :param box_color: a string that represents box's color.
    :param box_padding: a string that adds padding to the text box.
    :param text_position: a tuple of text that represents where to place texts.
    """

    text = country_name + "  " + value
    text_position_x = ""
    text_position_y = ""

    # if this was just a break, not country name, then set empty string
    if "Break" in country_name:
        text = " "

    # set text_position_x using three options
    if text_position[0] == "center":  # when x position was center
        text_position_x = "(w-text_w)/2"
    elif text_position[0] == "left":  # when x position was left
        text_position_x = "(%d)" % box_padding
    elif text_position[0] == "right":  # when x position was right
        text_position_x = "(w-text_w-%d)" % box_padding
    else:  # if value was other than this, raise ValueError
        raise ValueError

    # set text_position_y using three options
    if text_position[1] == "center":  # when y position was center
        text_position_y = "(h-text_h)/2"
    elif text_position[1] == "up":  # when y position was up
        text_position_y = "(%d)" % box_padding
    elif text_position[1] == "down":  # when y position was down
        text_position_y = "(h-text_h-%d)" % box_padding
    else:  # if value was other than this, raise ValueError
        raise ValueError
    subprocess.check_output([
                            "ffmpeg",
                            "-i",
                            video_name,
                            "-vf",
                            "drawtext=fontfile=/%s:text='%s':fontcolor=%s:fontsize=%d:box=%d:boxcolor=%s@%f:boxborderw=5:x=%s:y=%s"
                            % (font_dir, text, font_color, font_size, box_enabled, box_color, box_opacity, text_position_x, text_position_y),
                            "-codec:a",
                            "copy",
                            video_name.replace("s.mp4", "f.mp4"),
                            "-y"],
                            stderr=subprocess.STDOUT)


def calculate_play_speed(cur_value, avg, bigger_the_faster: bool):
    """
    A simple function that calculates playspeed of current segment of video.
    This will range speed from 0.xx to 2.0
    :param cur_value: the current value of this segment
    :param avg: the average value of total segments
    :param bigger_the_faster: if true it will be bigger the faster
    """
    return (1 + (-1) ** (not bigger_the_faster) * ((cur_value - avg) / avg))


def process_country(**kwargs):
    """
    A function that process a single country.
    This function does following things
    1. Cut video clip according to the timings.
    2. Calculate playspeed.
    3. Set playspeed into the video.
    4. Add caption.
    :param data: a pandas.Series that represents the data of current video clip
    :param cur_value: value that representes current country's value
    :param playspeed: value that represents manual playspeed
    :param tmp_dir: a string that represents tmp_dir
    :param auto_calculate_speed: a boolean that decides
                                 whether or not to calculate speed.
    :param bigger_the_faster: a boolean that decides
                              bigger the faster for playspeed calculation
    :param avg: a value that is for average of all countries.
    :param font_dir: a string that represents directory
                     that leads to the font that current caption will be using.
    :param font_color: a string that represents color Ex) white.
    :param font_size: a int value that represents font's size.
    :param box_enabled: a boolean that represents
                        whether or not to use text boxes.
    :param box_opacity: a float that sets box's opacity:
                        0 means it is it is not transparent at all.
    :param box_color: a string that represents box's color.
    :param box_padding: a string that adds padding to the text box.
    :param text_position: a tuple of text that represents where to place texts.
    """
    data = kwargs['data']
    cur_value = kwargs['cur_value']
    playspeed = kwargs['playspeed']

    tmp_dir = kwargs['tmp_dir']
    auto_calculate_speed = kwargs['auto_calculate_speed']
    bigger_the_faster = kwargs['bigger_the_faster']
    avg = kwargs['avg']
    font_dir = kwargs['font_dir']
    font_color = kwargs['font_color']
    font_size = kwargs['font_size']
    box_enabled = kwargs['box_enabled']
    box_opacity = kwargs['box_opacity']
    box_color = kwargs['box_color']
    box_padding = kwargs['box_padding']
    text_position = kwargs['text_position']

    out_file_name = os.path.join(tmp_dir, data['save_name'])

    # if playspeed was -1, this will skip current country
    if (playspeed == -1):
        print("[+] Skipping " + data['name'])
        return
    else:
        cut_video(data, tmp_dir)
        # we do not want break to go fast or slow.
        if "Break" in data['name']:  # if current country was break
            if playspeed == 0:  # and was set as 0
                playspeed = 1  # it will play with speed 1
        else:
            if auto_calculate_speed:
                playspeed = calculate_play_speed(cur_value,
                                                 avg, bigger_the_faster)

        change_video_speed(out_file_name, playspeed)
        add_caption(video_name=out_file_name.replace(".mp4", "s.mp4"),
                    country_name=data['name'], value=str(cur_value),
                    font_dir=font_dir, font_color=font_color,
                    font_size=font_size, box_enabled=box_enabled,
                    box_opacity=box_opacity, box_color=box_color,
                    box_padding=box_padding,
                    text_position=text_position)
        print("[+] Processed " + data['name'] + " / Speed : " + str(playspeed))


def process_all(data: pd.DataFrame, clean_up=True, auto_calculate_speed=True,
                bigger_the_faster=True,
                font_dir="../fonts/comic.ttf", font_color="white",
                font_size=20, box_enabled=True, box_color="black",
                box_opacity=0.5, box_padding=10,
                text_position=("left", "down"),
                threading_enabled=False):
    """
    :param data: a pandas.DataFrame that represents all data
    :param clean_up: a boolean that decides
                     whether or not to clean up after processing video.
    :param auto_calculate_speed: a boolean that decides whether
                                 or not to automatically calculate speed.
    :param bigger_the_faster: a boolean that decides
                              bigger the faster for playspeed calculation
    :param font_dir: a string that represents directory
                     that leads to the font that current caption will be using.
    :param font_color: a string that represents color Ex) white.
    :param font_size: a int value that represents font's size.
    :param box_enabled: a boolean that represents
                        whether or not to use text boxes.
    :param box_opacity: a float that sets box's opacity:
                        0 means it is it is not transparent at all.
    :param box_color: a string that represents box's color.
    :param box_padding: a string that adds padding to the text box.
    :param text_position: a tuple of text that represents where to place texts.
    :param threading_enabled: a boolean that decides
                              whether or not to use threading.
                              This multithreading is poorly optimized.
                              So, unless you have a good CPU and plenty of RAM,
                              DO NOT use this option

    """
    subprocess.run(["mkdir", "-p", "tmp_dir"])
    timings = pd.read_csv("../time_data.csv")
    tmp_dir = os.path.join(os.getcwd(), "tmp_dir")

    avg = data['value'].mean()
    thread_list = list()

    if threading_enabled:  # if threading was enabled, do multithreading
        for i in range(len(timings)):
            t = threading.Thread(target=process_country, kwargs={'data': timings.loc[i],
                                                                 'cur_value': data.loc[i]['value'],
                                                                 'playspeed': data.loc[i]['playspeed'],
                                                                 'tmp_dir': tmp_dir,
                                                                 'avg': avg,
                                                                 'auto_calculate_speed': auto_calculate_speed,
                                                                 'bigger_the_faster': bigger_the_faster,
                                                                 'font_dir': font_dir,
                                                                 'font_color': font_color,
                                                                 'font_size': font_size,
                                                                 'box_enabled': box_enabled,
                                                                 'box_color': box_color,
                                                                 'box_opacity': box_opacity,
                                                                 'box_padding': box_padding,
                                                                 'text_position': text_position})
            thread_list.append(t)
        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()
    else:   # if threading was not enabled, use single thread.
        for i in range(len(timings)):
            process_country(**{'data': timings.loc[i],
                               'cur_value': data.loc[i]['value'],
                               'playspeed': data.loc[i]['playspeed'],
                               'tmp_dir': tmp_dir,
                               'avg': avg,
                               'auto_calculate_speed': auto_calculate_speed,
                               'bigger_the_faster': bigger_the_faster,
                               'font_dir': font_dir,
                               'font_color': font_color,
                               'font_size': font_size,
                               'box_enabled': box_enabled,
                               'box_color': box_color,
                               'box_opacity': box_opacity,
                               'box_padding': box_padding,
                               'text_position': text_position})

    f = open("./files.txt", "w")  # write files.txt for concatenating
    for i in range(len(timings)):
        f.write("file '" +
                os.path.join(tmp_dir,
                             timings.loc[i]['save_name'].replace(".mp4",
                                                                 "f.mp4"))
                + "'\n")
    f.close()

    # Concatenate videos in files.txt as result.mp4
    subprocess.check_output([
                            "ffmpeg",
                            "-f",
                            "concat",
                            "-safe",
                            "0",
                            "-i",
                            "files.txt",
                            "-c",
                            "copy",
                            "result.mp4",
                            "-y"
                            ], stderr=subprocess.STDOUT)

    if clean_up:
        shutil.rmtree(tmp_dir)
        os.remove("./files.txt")


if __name__ == "__main__":
    data = pd.DataFrame()
    data = pd.read_csv("../data.csv")

    start = timeit.default_timer()
    process_all(data, threading_enabled=True)
    stop = timeit.default_timer()

    print("[+] Finished task in " + str(stop - start))
