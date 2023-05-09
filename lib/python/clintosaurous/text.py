#!/opt/clintosaurous/venv/bin/python3 -Bu

""" Various Text String Operations

This is intended as an internal module for the Clintosaurous tools.

    import clintosaurous.text
"""


import re


VERSION = '1.0.0'
LAST_UPDATE = '2023-01-01'


def center(text: str, width: int = 78) -> str:

    """ Center a String

    Takes the string passed and centers it with the width.

    Width is optional and defaults to 78 to fit in an 80 character terminal.
    For strings longer than width, if wrap is true, the lines are wrapped with
    each line in the wrap centered to width. wrap default is true. Trailing
    spaces are not returned.

        centered = text.center(text)

    Parameters:

    text (str): String to be centered.
    width (int): Width length to center text in. Default: 78

    Return:

    str: Centered text.

    Raises:

    TypeError: `text` is not a `str`.
    TypeError: `width` is not an `int`.
    """

    # Type hints.
    if not isinstance(text, str):
        raise TypeError(f'`text` expected `str`, received {type(text)}')
    if isinstance(width, bool) or not isinstance(width, int):
        raise TypeError(f'`width` expected `int`, received {type(width)}')

    # Normalize spacing.
    text = re.sub(r'[\s\n]+', ' ', text).strip()

    # Return if empty string.
    text_len = len(text)
    if not text_len:
        return ''

    print(text)

    # If `text` is shorter than or equal to width, center it and return it.
    if text_len <= width:
        line_len = len(text)
        start_point = int(width / 2 - line_len / 2)
        return f'{" "*start_point}{text}'

    # Start line wrapping logic.
    lines = []

    current_line = ''
    for word in text.split(' '):
        current_line_len = len(current_line)
        word_len = len(word)

        # What do if we have a really long word? We split it.
        if word_len > width:
            if current_line_len:
                lines.append(current_line)

            # Split the long word into chunks for separate lines. Append the
            # hyphen to try to show we wrapped it.
            for start in range(0, word_len, width - 2):
                lines.append(word[start:start + width - 2] + '-')

            # Make the last line of the split word the current line to start
            # the process over. And strip the hyphen off.
            if len(lines[-1]) < width:
                current_line = re.sub(r'-$', '', lines.pop())

            continue

        # If appending the current word to the current line will make it too
        # long, create a new line.
        if current_line_len + word_len + 1 > width:
            lines.append(current_line)
            current_line = word
        else:
            current_line += ' ' + word
    if len(current_line):
        lines.append(current_line)

    return '\n'.join([center(line, width) for line in lines])


def expand_range(ranges_str: str) -> list:

    """ Expand Ranges of Integers

    Takes integer ranges and expands them to all numbers in the range.

    Format is a dash between ranges and a comma to separate ranges.

        numbers = text.expand_range(range_str)

    Parameters:

    range_str (str): List of numbers to build the range list. Formatted:
        `1-3,5-6,8,10-12`

    Return:

    list: The list of all numbers in the ranges supplied.

    Raises:

    TypeError: `ranges_str` is not a str.
    """

    # Type hints.
    if not isinstance(ranges_str, str):
        raise TypeError(
            f'`ranges_str` expected `str`, received {type(ranges_str)}')

    ranges = []
    # Split individual ranges.
    for range_str in ranges_str.split(","):
        if not len(range_str):
            continue

        # Add single values to return values.
        if '-' not in range_str:
            ranges.append(int(range_str))
            continue

        # Parse the two numbers in the range.
        start_number, end_number = range_str.split("-")
        # Convert the numbers in the range to integers.
        start_number = int(start_number)
        end_number = int(end_number)

        # If the start number is greater than the end number, swap them.
        if start_number > end_number:
            tmp_start = end_number
            start_number = tmp_start

        # Add the range numbers to the ranges list.
        ranges += [i for i in range(start_number, end_number + 1)]

    return sorted(ranges)


def pluralize(word: str, number: int) -> str:

    """ Make a Word the Plural Version

    Takes the word supplied and the number of items and converts the word to a
    plural format.

    It accounts for not making one number plural, words ending in 'y' and all
    uppercase words. If all letters in the word are in uppercase, if plural,
    the added characters will be in uppercase as well.

        pluralized = text.pluralize(word, number)

    Parameters:

    word (str): The word to be pluralized.
    number (int|float): The number to determine if the word should be
        pluralized.

    Return:

    str: The word pluralized if needed. Else, original word is returned.

    Raises:

    TypeError: `word` is not a str.
    TypeError: `number` is not an int or float.
    """

    if not isinstance(word, str):
        raise TypeError(f'`word` expected `str`, received {type(word)}')
    # Booleans evaluate as an `int` as well as `bool`. Force `bool` values
    # to error.
    if (
        isinstance(number, bool)
        or (not isinstance(number, int) and not isinstance(number, float))
    ):
        raise TypeError(
            f'`number` expected `int` or `float`, received {type(word)}')

    if number == 1:
        return word

    if word.isupper():
        uppercase = 1
    else:
        uppercase = 0

    if len(word) <= 1:
        return_txt = word + "s"

    else:
        split_str = [char for char in word]
        base = "".join(split_str[0:-1])
        last_char = split_str[-1]

        if last_char.lower() == "y":
            if re.match(r'[aeiou]', split_str[-2]):
                return_txt = word + "s"
            else:
                return_txt = base + "ies"

        elif last_char.lower() == "s":
            if split_str[-2].lower() == 'e':
                return_txt = word
            else:
                return_txt = word + "es"

        else:
            return_txt = word + "s"

    if uppercase:
        return return_txt.upper()
    else:
        return return_txt


def table(rows: list, title: str = None, headings: bool = True) -> str:

    """ Creates a Text Table

    Creates a text based table with the given title and rows.

    Title and headings are optional.

        table_text = text.table(rows, title)

    Parameters:

    rows (list): List of lists of rows of data.
    title (str): Title to add to the top of the table.
    headings (bool): If the first row are table headings. Default: True

    Return:

    str: Text of the table generated.

    Raises:

    TypeError: `rows` is not a list.
    TypeError: `title` is not a str.
    TypeError: `headings` is not a bool.
    """

    # Type hints.
    if not isinstance(rows, list):
        raise TypeError(f'`rows` expected `list`, received {type(rows)}')
    if title is not None and not isinstance(title, str):
        raise TypeError(f'`title` expected `str`, received {type(title)}')
    if not isinstance(headings, bool):
        raise TypeError(
            f'`headings` expected `bool`, received {type(headings)}')

    # Set headings row.
    if headings:
        headings = rows[0]
        del rows[0]

    # Number of columns in table.
    col_count = 1
    # Max width of all columns.
    col_widths = []

    # If headings, get heading column count and set column widths.
    if headings:
        col_count = len(headings)

        # Loop through headings and set width.
        for i in range(len(headings)):
            if not isinstance(headings[i], str):
                headings[i] = str(headings[i])

            col_width = len(headings[i])

            # If no width, set to 1.
            if col_width:
                col_widths.append(col_width)
            else:
                col_widths.append(1)

    # Loop through rows to get column count, widths.
    for row in rows:
        if not row:
            continue

        row_len = len(row)

        # Increase column count if more row columns than previously seen.
        if row_len > col_count:
            col_count = row_len

        # Loop through row checking width and data type.
        for i in range(row_len):
            if not isinstance(row[i], str):
                row[i] = str(row[i])

            col_width = len(row[i])

            if len(col_widths) <= i:
                if col_width:
                    col_widths.append(col_width)
                else:
                    col_widths.append(1)
            else:
                if col_width > col_widths[i]:
                    col_widths[i] = col_width

    # Return box text.
    table_txt = ""

    # If table title, print title header.
    if title:
        if not isinstance(title, str):
            title = str(title)

        # Determine top bar width.
        dash_width = len(col_widths) * 3 - 1
        for width in col_widths:
            dash_width += width

        text_width = dash_width - 2

        table_txt += '+' + '-'*dash_width + '+\n'
        centeredtitle = center(title, text_width)
        for line in centeredtitle.split('\n'):
            table_txt = \
                f'{table_txt}| {line}{" "*(text_width - len(line))} |\n'

    break_line = ''
    for i in range(len(col_widths)):
        break_line = f'{break_line}+-{"-"*col_widths[i]}-'
    break_line = f'{break_line}+\n'

    # Add headings.
    if headings:
        table_txt += break_line

        # Loop through headings and add to row.
        for i in range(col_count):
            try:
                value = headings[i]
            except IndexError:
                value = ''

            table_txt = \
                f'{table_txt}| {value}{" "*(col_widths[i] - len(value))} '

        table_txt += '|\n'

    table_txt += break_line

    # Loop through data rows.
    for row in rows:
        if not row:
            table_txt += break_line
            continue

        # Loop through headings and add to row.
        for i in range(col_count):
            try:
                value = row[i]
            except IndexError:
                value = ''

            table_txt += f'| {value}{" "*(col_widths[i] - len(value))} '

        table_txt += '|\n'

    table_txt += break_line

    return table_txt
