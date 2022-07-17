# Using Program
There are two ways of using this program, by `jupyter notebook` and normal `python`.

## Providing Data
This program generates videos using the data provided by `data.csv` which can be found [here](https://github.com/gooday2die/Yakkos-world-video-generator/blob/main/data.csv).

In `data.csv`, you can manually set `playspeed` of each country or set `value` and make this program automatically calculate each country's playspeed.

Let's assume that we would like to set values to United States. The table below is from `data.csv`. 

|  |name|value|playspeed|
|--|--|--|--|
|  |...|...|...|
|  |United States|0|0|
|  |...|...|...|

Assume that we would like following scenarios.
#### Skip United States
|  |name|value|playspeed|
|--|--|--|--|
|  |...|...|...|
|  |United States|0|-1|
|  |...|...|...|

You can make the video skip United States by setting `-1` as value of `playspeed`.

#### Set United States as value of 10
|  |name|value|playspeed|
|--|--|--|--|
|  |...|...|...|
|  |United States|10|0|
|  |...|...|...|

Now the program can automatically know that United States has value of `10`. If you want to make program automatically calculate the playspeed, check here.
#### Set United States as playspeed of 1.5
|  |name|value|playspeed|
|--|--|--|--|
|  |...|...|...|
|  |United States|0|1.5|
|  |...|...|...|

Now the program can automatically know that United States has value of `1.5`. The `playspeed` **must** be a positive number.

**Be advised that there are countries starting with `Break` and those are for timings where it is a break (where it does not sing any country name)**

## Using Parameters
This program offers multiple parameters for customization of the video. The list below describes each parameters and how they work.

### clean_up
**Jupyter Notebook**: Use `clean_up=True` for function `process_all()`
**Python Commandline**: Use `-cu` or `--clean_up` when executing `run_me.py`
**Default**:  `True`

This program generates a directory named `tmp_dir` for saving temporary video clips while processing the video. When this option was enabled or was set `True`, it will automatically remove directory `tmp_dir`. Unless you need video of each country, enable this option to save disk space.

### auto_calculate_speed
**Jupyter Notebook**: Use `auto_calculate_speed=True` for function `process_all()`
**Python Commandline**: Use `-ac True` or `--auto_calculate_speed True` when executing `run_me.py`
**Default**:  `True`

When the program starts, each country's values will be all collected and will generate an average value of all countries. When this option was enabled, it will automatically set all country video clip's playspeed from `0.1` to `2.0`.

The formula of calculating play speed is as it follows:
```
 (1 + (-1) ** (not bigger_the_faster) * ((cur_value - avg) / avg))
```
Example:
- Average was 100
- Current Value was 200
- Bigger the faster was set
- Result will be `2.0` playspeed.

If you want to set relatively bigger number as faster speed, or bigger number as slower speed, check [bigger_the_faster](#bigger_the_faster).

### bigger_the_faster
**Jupyter Notebook**: Use `bigger_the_faster=True` for function `process_all()`
**Python Commandline**: Use `-bf True` or `--bigger_the_faster True` when executing `run_me.py`
**Default**:  `True`

This parameter **only** works when [auto_calculate_speed](#auto_calculate_speed) was set `True`. When this parameter is set `True`, it will calculate country with bigger values as faster playspeed. If this was set `False`, it will calculate country with bigger values as slower playspeed.

### font_dir
**Jupyter Notebook**: Use `font_dir="path_to_font"` for function `process_all()`
**Python Commandline**: Use `-fd "path_to_font"` or `--font_directory "path_to_font"` when executing `run_me.py`
**Default**:  `"../fonts/comic.ttf"`

This sets caption's font style of the video. Check here for more [information](https://ffmpeg.org/ffmpeg-filters.html#drawtext)

### font_color
**Jupyter Notebook**: Use `font_color="white"` for function `process_all()`
**Python Commandline**: Use -fc "white"` or `--font_color "white"` when executing `run_me.py`
**Default**:  `"white"`

This sets caption's font color of the video. Check here for more [information](https://ffmpeg.org/ffmpeg-filters.html#drawtext) on colors.

### font_size
**Jupyter Notebook**: Use `font_size="20"` for function `process_all()`
**Python Commandline**: Use `-fc 20` or `--font_color 20` when executing `run_me.py`
**Default**:  `20` (in `int`)

This sets caption's font size of the video. Check here for more [information](https://ffmpeg.org/ffmpeg-filters.html#drawtext) on font sizes.

### box_enabled
**Jupyter Notebook**: Use `box_enabled=True` for function `process_all()`
**Python Commandline**: Use `-be True` or `--box_enabled True` when executing `run_me.py`
**Default**:  `True`

This generates a caption box behind the caption when enabled.

### box_opacity
**Jupyter Notebook**: Use `box_opacity=0.5` for function `process_all()`
**Python Commandline**: Use `-bo 0.5` or `--box_opacity 0.5` when executing `run_me.py`
**Default**:  `0.5` (in `float`)

This determines the caption box's opacity. `0` for no transparency, `1` for max transparency.

### box_color
**Jupyter Notebook**: Use `box_color="black"` for function `process_all()`
**Python Commandline**: Use `-bc "black"` or `--box_color "black"` when executing `run_me.py`
**Default**:  `"black"`

This determines the caption box's color. Check here for more [information](https://ffmpeg.org/ffmpeg-filters.html#drawtext) on colors.

### box_padding
**Jupyter Notebook**: Use `box_padding=10` for function `process_all()`
**Python Commandline**: Use `-bp 10` or `--box_padding 10` when executing `run_me.py`
**Default**:  `10`

This determines the caption box's location from the corners. For example, if set `10`, this will have 10 pixels away from corners. If the caption's location was `("center", "center")` this will have no effect. 

### text_position
**Jupyter Notebook**: Use `text_position=("left", "down")` for function `process_all()`
**Python Commandline**: Use `-tp "("left", "down")"` or `--text_position "("left", "down")"` when executing `run_me.py`
**Default**:  `("left", "down")`

This determines where the caption box will be generated at. There are following positions:

- Horizontal : `"left"`, `"center"`,`"right"`
- Vertical : `"up"`, `"center"`, `"down"`

For example, if the text needs to be generated at "right down corner", use `("right", "down")` as text_position.

Also if a padding from each corner was needed, use [box_padding](#box_padding) for paddings from each corners.

### threading_enabled
**Jupyter Notebook**: Use `threading_enabled=False` for function `process_all()`
**Python Commandline**: Use `-t False` or `--threading False` when executing `run_me.py`
**Default**:  `False`

This is experimental feature. This options sets whether or not to use multithreading. If threading was not enabled, video clip of each country will be generated one by one. However enabling multithreading will make all video clips be generated at once. Enabling this option **does** generate video quite faster than not enabling it.

The multithreading of this program was **not ideally** optimized. Unless you have a decent CPU with enough RAM left, **DO NOT** use this option. It might crash the program.

*PC with `i9-7940x` CPU and `32GB` RAM had all its CPU cores loaded with ffmpeg tasks and used 29GB of RAM and took about 34.72 seconds*`
