import logging
import os
import sys

from PIL import Image

from improcessing import replaceall, filetostring, imgkitstring


def imcaption(image, caption, tosavename=None):
    logging.info(f"[improcessing] Rendering {image}...")
    with Image.open(image) as im:
        imagewidth = im.size[0]  # seems ineffecient but apparently fast?
    replacedict = {
        "calc((100vw / 13) * (16 / 12))": f"{(imagewidth / 13)}pt",
        "calc((100vw / 2) / 13)": f"{(imagewidth / 2) / 13}px",
        "<base href='./'>": f"<base href='file://{'/' if sys.platform == 'win32' else ''}{os.path.abspath('rendering')}'> ",
        "CaptionText": caption,
        "rendering/demoimage.png": image
    }
    torender = replaceall(filetostring("caption.html"), replacedict)
    rendered = imgkitstring(torender, tosavename)
    return rendered


def motivate(image, caption, tosavename=None):
    logging.info(f"[improcessing] Rendering {image}...")
    with Image.open(image) as im:
        imagewidth = im.size[0] * 1.1 + 16  # weird adding is to estimate final size based on styling
    replacedict = {
        "margin: 30px;": f"margin: {imagewidth*0.05}px;",
        "font-size: 80px;": f"font-size: {imagewidth*0.133}px;",
        "font-size: 40px;": f"font-size: {imagewidth * 0.067}px;",
        "<base href='./'>": f"<base href='file://{'/' if sys.platform == 'win32' else ''}{os.path.abspath('rendering')}'> ",
        "CaptionText1": caption[0],
        "CaptionText2": caption[1],
        "rendering/demoimage.png": image
    }
    torender = replaceall(filetostring("motivate.html"), replacedict)
    rendered = imgkitstring(torender, tosavename)
    return rendered
