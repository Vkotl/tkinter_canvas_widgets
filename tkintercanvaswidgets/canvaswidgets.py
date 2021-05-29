import time
import threading
from typing import Callable
from operator import itemgetter
from tkinter import HIDDEN, NORMAL, NW, N, W, CENTER
from tkinter.font import Font

from PIL import ImageTk, Image

from ._helpers import _fit_font_height, _resize_image, _fit_text_width, _get_image


class CanvasSection:
    def __init__(self, parent, x, y, width, height, tag=None):
        """
            Constructor for a CanvasSection
        :param parent: Parent canvas that will be used.
        :param x: The initial x on the parent from which the section starts.
        :param y: The initial x on the parent from which the section starts.
        :param width: The width of the section.
        :param height: The height of the section.
        :param tag: Tag for the elements in this section.
        """
        self.parent = parent
        self._initx = x
        self._inity = y
        self._width = width
        self._height = height
        self._events = []
        if not isinstance(tag, tuple) and tag is not None:
            tag = (tag, )
        elif tag is None:
            tag_prefix = '~canvsect~'
            i = 1
            tag = f'{tag_prefix}{i}'
            while len(parent.find_withtag(tag)) != 0:
                i += 1
                tag = f'{tag_prefix}{i}'
            tag = (tag, )
        self.tag = tag
        self._area = self.parent.create_rectangle(self._initx, self._inity,
                                                  self._initx + width,
                                                  self._inity + height, fill='',
                                                  outline='', tags=tag)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def update_item_params(self, kwargs):
        """
            Add more tags to the item.
        :param kwargs:
        :return:
        """
        tags = 'tags'
        if self.tag is not None:
            if tags in kwargs:
                if type(kwargs[tags]) == tuple:
                    kwargs[tags] += (self.tag, )
                elif type(kwargs[tags]) == str:
                    kwargs[tags] = (kwargs[tags], *self.tag)
            else:
                kwargs[tags] = self.tag

    def create_text(self, x, y, **kwargs):
        self.update_item_params(kwargs)
        return self.parent.create_text(self._initx + x, self._inity + y,
                                       **kwargs)

    def create_image(self, x, y, **kwargs):
        self.update_item_params(kwargs)
        return self.parent.create_image(self._initx + x, self._inity + y,
                                        **kwargs)

    def create_line(self, *args, **kwargs):
        args = (arg + self._initx if i % 2 == 0 else arg + self._inity
                for i, arg in enumerate(args))
        self.update_item_params(kwargs)
        self.parent.create_line(*args, **kwargs)

    def create_rectangle(self, left, top, right, bottom, **kwargs):
        self.update_item_params(kwargs)
        return self.parent.create_rectangle(self._initx + left, self._inity + top,
                                            self._initx + right, self._inity + bottom,
                                            **kwargs)

    def create_arc(self, x, y, xsize, ysize, **kwargs):
        self.update_item_params(kwargs)
        return self.parent.create_arc(x + self._initx, y + self._inity,
                                      xsize + self._initx, ysize + self._inity,
                                      **kwargs)

    def create_oval(self, x, y, xsize, ysize, **kwargs):
        self.update_item_params(kwargs)
        return self.parent.create_oval(x + self._initx, y + self._inity,
                                       xsize + self._initx, ysize + self._inity,
                                       **kwargs)

    def create_button(self, x, y, **kwargs):
        self.update_item_params(kwargs)
        return CanvasButton(self, x, y, **kwargs)

    def bbox(self, item):
        """
            Convert canvas bbox coordinates to relative
            coordinates for this section.
        :param item: Item that exists in the canvas.
        :return:
        """
        if self.parent.itemcget(item, 'state') != HIDDEN:
            borders = self.parent.bbox(item)
            return tuple(val-(self._inity if i % 2 else self._initx)
                         for i, val in enumerate(borders))

    def coords(self, item, x1=None, y1=None, x2=None, y2=None):
        if all(var is None for var in (x1, y1, x2, y2)):
            coords = self.parent.coords(item)
            if len(coords) == 2:
                coords = coords[0] - self._initx, coords[1] - self._inity
            else:
                coords = (
                    coords[0] - self._initx, coords[1] - self._inity,
                    coords[2] - self._initx, coords[3] - self._inity)
            return coords
        else:
            if x2 is None or y2 is None:
                return self.parent.coords(item, self._initx + x1, self._inity + y1)
            return self.parent.coords(item, self._initx + x1, self._inity + y1,
                                      self._initx + x2, self._inity + y2)

    def show_borders(self):
        border_color = {'outline': 'black'}
        self.create_rectangle(0, 0, self.width, self.height, **border_color)

    def tag_raise(self, item):
        self.parent.tag_raise(item)

    def tag_lower(self, item):
        self.parent.tag_lower(item)

    def lower_section(self):
        self.tag_lower(self.tag)

    def raise_section(self):
        self.tag_raise(self.tag)

    def bind_section(self, event, func):
        self.tag_bind(self.tag, event, func, add=True)

    def itemconfig(self, item, **kwargs):
        self.parent.itemconfig(item, **kwargs)

    def tag_bind(self, item, event, func, add=None):
        if event != '<MouseWheel>':
            self._events.append(event)
            self.parent.tag_bind(item, event, func, add)
        else:
            self.bind_all(event, self.mousescroll)
            self.tag_bind(item, f'<{event}>', func, add)

    def bind(self, event, func, add=None):
        self.parent.bind(event, func, add)

    def move(self, item, x, y):
        self.parent.move(item, x, y)

    def itemcget(self, tagOrId, option):
        return self.parent.itemcget(tagOrId, option)

    def delete(self, tag):
        if tag == 'all' and self.tag is not None:
            self.parent.delete(self.tag)
        else:
            self.parent.delete(tag)

    def find_withtag(self, tag):
        if self.tag is not None:
            tag = (tag, *self.tag)
        return self.parent.find_withtag(tag)

    def tag_unbind(self, tagOrId, sequence, funcId=None):
        self.parent.tag_unbind(tagOrId, sequence, funcId)

    def bind_all(self, event: str, func: Callable):
        self.parent.bind_all(event, func)

    def absolute_coords(self, x, y):
        if isinstance(self.parent, CanvasSection):
            return self.parent.absolute_coords(x + self._initx,
                                               y + self._inity)
        return self._initx + x, self._inity + y

    def itemconfigure(self, item, **kwargs):
        self.parent.itemconfigure(item, **kwargs)

    def update(self):
        self.parent.update()

    def update_idletasks(self):
        self.parent.update_idletasks()

    def after(self, ms, func=None, *args):
        """
            Run callback function after milliseconds time.
        :param ms: Time to wait before calling callback function.
        :param func: Callback function to run after the time passed.
        :param args: Extra arguments for the callback function.
        """
        self.parent.after(ms, func, *args)

    def master_canvas(self):
        if isinstance(self.parent, CanvasSection):
            return self.parent.master_canvas()
        return self.parent

    def mousescroll(self, event):
        event.widget.event_generate('<<MouseWheel>>', x=event.x, y=event.y,
                                    time=event.delta)

    def destroy(self):
        while len(self._events) > 0:
            self.tag_unbind(self.tag, self._events.pop(0))
        self.delete('all')
        attrs = list(self.__dict__.keys())
        for attr in attrs:
            delattr(self, attr)


class CanvasButton:
    image = None
    text = None
    cursored_img = None

    def __init__(self, parent, x, y, image=None, text=None, command=None,
                 tags=None, cursored_img=None, value=None):
        """
            Creation of a canvas item similar in activity as a button.
        :param parent: Parent is the element the button is drawn on,
                       can be either Canvas or an object that implements
                       'create_image', 'create_text', 'itemconfig',
                       'move' and 'tag_bind'.
        :param x: x coordinates of the button (based on anchor time
                  given in image kwargs)
        :param y: y coordinates of the button (based on anchor time
                  given in image kwargs)
        :param image: Dictionary of data for the image.
                      Must have 'image' key that holds the image instance.
        :param text: Dictionary of data for the text.
        :param command: Callback function to run after the button is pressed.
        :param tags: Tag for the element.
        :param cursored_img: Image to switch to on mouse-over.
        """
        self._parent = parent

        if text is None and image is None:
            raise AttributeError('Either text or image have to be given.')
        if image is not None:
            image = image.copy()
            self.imgobj = image.pop('image')
            self.image = parent.create_image(x, y, image=self.imgobj, **image,
                                             tags=tags)
        if text is not None:
            if 'textoffset' in text:
                text = text.copy()
                offsetx, offsety = text.pop('textoffset')
            else:
                offsetx, offsety = 0, 0
            self.text = parent.create_text(x + offsetx, y + offsety, tags=tags,
                                           **text)
            # parent.find_withtag(self.text)
            self._click_listeners(self.text)

        self.bound = command
        if cursored_img is not None:
            self.cursored_img = parent.create_image(x, y, image=cursored_img,
                                                    state=HIDDEN)
            if self.image is not None:
                self._parent.tag_bind(self.image, '<Enter>', self._on_enter)
            self._parent.tag_bind(self.cursored_img, '<Leave>', self._on_leave)

            self._click_listeners(self.cursored_img)
        else:
            if self.image is not None:
                self._click_listeners(self.image)
        if value is not None:
            self.value = value

    def _click_listeners(self, element):
        self._parent.tag_bind(element, '<ButtonPress-1>', self._btnclick)
        self._parent.tag_bind(element, '<ButtonRelease-1>', self._btnrelease)

    def _btnclick(self, event):
        if self.image is not None:
            self._parent.move(self.image, 1, 1)
        if self.text is not None:
            self._parent.move(self.text, 1, 1)

    def _btnrelease(self, event):
        event.widget = self
        if self.text is not None:
            self._parent.move(self.text, -1, -1)
        if self.image is not None:
            self._parent.move(self.image, -1, -1)
        if self.bound is not None:
            self.bound(event)

    def draw_border(self):
        img_box, txt_box = self._get_bboxes()
        if img_box is not None and txt_box is not None:
            initx = min(img_box[0], txt_box[0])
            inity = min(img_box[1], txt_box[1])
        elif img_box is None:
            initx = txt_box[0]
            inity = txt_box[1]
        else:
            initx = img_box[0]
            inity = img_box[1]

        width = self.width
        height = self.height
        self._parent.create_rectangle(initx, inity, initx+width, inity+height,
                                      fill='', outline='white')

    def itemcget(self, elem, param):
        return self._parent.itemcget(elem, param)

    def change_text(self, text):
        if self.text is not None:
            self._parent.itemconfig(self.text, text=text)

    def get_text(self):
        if self.text is not None:
            return self.itemcget(self.text, 'text')
        return ''

    def press_bind(self, func):
        self.bound = func

    def _on_enter(self, event):
        if self.image is not None:
            self._parent.itemconfig(self.image, state=HIDDEN)
        self._parent.itemconfig(self.cursored_img, state=NORMAL)

    def _on_leave(self, event):
        self._parent.itemconfig(self.cursored_img, state=HIDDEN)
        if self.image is not None:
            self._parent.itemconfig(self.image, state=NORMAL)

    def update_cursored_img(self, new_img):
        self._parent.itemconfig(self.cursored_img, image=new_img)

    def update_main_image(self, new_img):
        if self.image is not None:
            self._parent.itemconfig(self.image, image=new_img)

    def delete(self):
        """
            Delete the CanvasButton from the parent.
        """
        if self.image is not None:
            self._parent.delete(self.image)
        if self.text is not None:
            self._parent.delete(self.text)
        if self.cursored_img is not None:
            self._parent.delete(self.cursored_img)

    def _get_bboxes(self):
        img_box, txt_box = None, None
        if (self.image is not None and
                self._parent.itemcget(self.image, 'state') in ('', NORMAL)):
            img_box = self._parent.bbox(self.image)
        elif (self.cursored_img is not None and
              self._parent.itemcget(self.cursored_img, 'state') in ('', NORMAL)):
            img_box = self._parent.bbox(self.cursored_img)
        if (self.text is not None and
                self._parent.itemcget(self.text, 'state') in ('', NORMAL)):
            txt_box = self._parent.bbox(self.text)

        return img_box, txt_box

    @property
    def height(self):
        img_box, txt_box = self._get_bboxes()
        if all(box is not None for box in (img_box, txt_box)):
            height = max(img_box[3], txt_box[3]) - min(img_box[1], txt_box[1])
        elif img_box is not None:
            height = img_box[3] - img_box[1]
        else:
            height = txt_box[3] - txt_box[1]
        return height

    @property
    def width(self):
        img_box, txt_box = self._get_bboxes()
        if all(box is not None for box in (img_box, txt_box)):
            width = round(max(img_box[2], txt_box[2]) - min(img_box[0],
                                                            txt_box[0]), 4)
        elif img_box is not None:
            width = img_box[2] - img_box[0]
        else:
            width = txt_box[2] - txt_box[0]
        return width


class SimpleCanvasCheckbox(CanvasSection):
    def __init__(self, parent, x, y, width, height, default=False, tag=None,
                 colors: dict = None, font=None, extra_txt=''):
        super().__init__(parent, x, y, width, height, tag=tag)
        self.default = default
        if colors is not None:
            self.colors = colors
            if 'font' not in self.colors:
                self.colors['font'] = 'black'
            if 'background' not in self.colors:
                self.colors['background'] = 'black'
            if 'check' not in self.colors:
                self.colors['check'] = 'white'
        else:
            self.colors = {'font': 'black', 'background': 'black',
                           'check': 'white'}
        if font is None:
            font = Font()
        self.font = font
        _fit_font_height(self.font, height)
        self.create_rectangle(0, 0, height, height, outline='',
                              fill=self.colors['background'])
        self.create_text(height*1.2, height/2, text=extra_txt, font=self.font,
                         fill=self.colors['font'], anchor=W)
        self.check = self.create_rectangle(height/3, height/3,
                                           height*(2/3), height*(2/3),
                                           fill=self.colors['check'],
                                           outline='',
                                           state=NORMAL if default else HIDDEN)
        self.enabled = True
        self.bind_section('<ButtonRelease-1>', self._mouseclick)

    def _mouseclick(self, event):
        if self.enabled:
            self.value = self.itemcget(self.check, 'state') != NORMAL
        return 'break'

    def set_enable_disable(self, enabled: bool = True):
        self.enabled = enabled

    @property
    def value(self) -> bool:
        return self.itemcget(self.check, 'state') == NORMAL

    @value.setter
    def value(self, newval: bool):
        if newval:
            self.itemconfig(self.check, state=NORMAL)
        else:
            self.itemconfig(self.check, state=HIDDEN)

    def is_shown(self) -> bool:
        return self.itemcget(self.tag, 'state') == NORMAL

    def hide(self):
        self.itemconfig(self.tag, state=HIDDEN)

    def show(self):
        self.itemconfig(self.tag, state=NORMAL)
        self.itemconfig(self.check, state=NORMAL if self.default else HIDDEN)
