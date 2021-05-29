from tkinter import *
from tkinter.ttk import *
from tkinter.font import Font
from tkinter.messagebox import showerror

from PIL import Image, ImageTk

from tkintercanvaswidgets import (CanvasSection, CanvasButton,
                                  SimpleCanvasCheckbox)


def main():
    root = Tk()
    root.geometry('500x500')

    mainframe = Frame(root)
    maincanvas = Canvas(mainframe, background='red')
    # Create a canvas starting on x=25, y=25 and size of 250x250
    mainsection = CanvasSection(maincanvas, 25, 25, 450, 450)
    mainsection.show_borders()

    center_width = mainsection.width * 0.8
    center_height = mainsection.height * 0.8
    # Create another section, this time inside 'mainsection'.
    centersection = CanvasSection(mainsection, mainsection.width*0.1,
                                  mainsection.height*0.1, center_width,
                                  center_height)
    centersection.show_borders()

    rect1 = centersection.create_rectangle(
        centersection.width*0.1, centersection.height*0.1,
        centersection.width*0.5, centersection.height*0.5, outline='yellow')
    centersection.itemconfig(rect1, fill='blue')

    # Adding an image button.
    image_dict = {'image': ImageTk.PhotoImage(Image.open('btn_icon.png')),
                  'anchor': N}
    btn1 = CanvasButton(centersection, x=centersection.width*0.60,
                        y=centersection.height*0.1,
                        image=image_dict)

    image_dict.pop('anchor')
    # Adding an image button with text.
    btn_text = {'text': 'Btn txt', 'fill': 'white'}
    btn2 = CanvasButton(centersection, x=centersection.width*0.75,
                        y=centersection.height*0.17,
                        image=image_dict, text=btn_text)

    # Create a button with text underneath.
    btn_text['textoffset'] = (0, image_dict['image'].height()*0.65)
    btn3 = CanvasButton(centersection, x=centersection.width*0.9,
                        y=centersection.height*0.17,
                        image=image_dict, text=btn_text)

    btn_text.pop('textoffset')
    btn_text['font'] = Font(family='Calibri')
    # Text button:
    btn4 = CanvasButton(centersection, x=centersection.width*0.75,
                        y=centersection.height*0.4,
                        text=btn_text)

    btn_text.update({'text': 'error msg', 'fill': 'lime'})
    # Button with a callback.
    btn5 = CanvasButton(centersection, x=centersection.width*0.75,
                        y=centersection.height*0.5,
                        text=btn_text,
                        command=lambda e: showerror('title', 'message'))

    # Create a simple, no image, checkbox.
    colors = {'font': 'blue', 'background': 'white', 'check': 'green'}
    SimpleCanvasCheckbox(centersection, centersection.width*0.1,
                         centersection.height*0.7, 20, 20, colors=colors,
                         font=Font(family='Times New Roman'),
                         extra_txt='Checkbox')

    mainframe.pack(expand=True, fill=BOTH)
    maincanvas.pack(expand=True, fill=BOTH)

    mainloop()


if __name__ == "__main__":
    main()
