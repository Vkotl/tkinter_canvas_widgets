from tkinter.font import Font

from PIL import Image, ImageTk


def _fit_text_width(font: Font, text: str, width: float, divider=None) -> str:
    """
        Takes a string and splits it to lines based on the required width.
    :param font: Font used for the text.
    :param text: The text to be fitted.
    :param width: The width to fit in.
    :param divider: Character to divide the string based on.
    :return: The string with \n as needed.
    """
    new_text = text
    i = len(text)
    while font.measure(new_text) > width and i > 0:
        try:
            if divider is not None:
                i = text.rindex(divider, 0, i)
            else:
                i -= 1
        except ValueError:
            divider = None
        new_text = text[:i] if i >= len(text) and text[i+1] != ' ' else text[:i-1]
    if i == len(text):
        return text
    elif i == 0 and divider is not None:
        return _fit_text_width(font, text, width)
    return f'{text[:i+1]}\n{_fit_text_width(font, text[i + 1:], width, divider)}'


def _fit_font_height(font, height):
    """
        Resize the font based on the height the text should be in.
    :param font: Font object.
    :param height: Height for the text to fit in.
    """
    while font.metrics('linespace') > height and font.cget('size') > 0:
        font.config(size=font.cget('size')-1)
    while font.metrics('linespace') < height:
        font.config(size=font.cget('size')+1)


def _get_image(w, h, directory, relation=False, resample='antialias', convert=True):
    w, h = int(w), int(h)
    img = Image.open(directory).convert('RGBA')
    if relation:
        width, height = img.size
        relation = height/width
        h = int(w*relation)
    return _resize_image(w, h, img, convert, resample=resample)


def _resize_image(w, h, img, convert=True, resample='antialias'):
    resampledict = dict.fromkeys(['nearest', 'none'], Image.NEAREST)
    resampledict.update(dict.fromkeys(['linear', 'bilinear'], Image.BILINEAR))
    resampledict.update(dict.fromkeys(['cubic', 'bicubic'], Image.BICUBIC))
    resampledict.update(dict.fromkeys(['antialias', 'lanczos'], Image.LANCZOS))
    resampledict['box'] = Image.BOX
    resampledict['hamming'] = Image.HAMMING

    if resample.lower() in resampledict:
        resized_img = img.resize((int(w), int(h)), resampledict[resample.lower()])
    else:
        resized_img = img.resize((int(w), int(h)), Image.LANCZOS)
    if convert:
        return ImageTk.PhotoImage(resized_img)
    else:
        return resized_img
