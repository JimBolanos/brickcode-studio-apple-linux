"""Turn the screen calls a program made into a picture, so the pictures the
blocks draw can be looked at and checked by pixel, not only by call count.
Black and white, 178 x 128, like the EV3 screen."""
from PIL import Image, ImageDraw

W, H = 178, 128


def raster(draw, scale=1):
    im = Image.new("1", (W * scale, H * scale), 1)
    d = ImageDraw.Draw(im)
    s = scale

    def col(c):
        return 1 if c == "Color.WHITE" else 0

    for op in draw:
        k = op[0]
        if k == "clear":
            d.rectangle([0, 0, W * s, H * s], fill=1)
        elif k == "circle":
            _, x, y, r, fill, c = op
            box = [(x - r) * s, (y - r) * s, (x + r + 1) * s - 1, (y + r + 1) * s - 1]
            if fill:
                d.ellipse(box, fill=col(c))
            else:
                d.ellipse(box, outline=col(c), width=s)
        elif k == "box":
            _, x1, y1, x2, y2, fill, c = op
            box = [x1 * s, y1 * s, (x2 + 1) * s - 1, (y2 + 1) * s - 1]
            d.rectangle(box, fill=col(c) if fill else None, outline=col(c))
        elif k == "line":
            _, x1, y1, x2, y2, w, c = op
            half = w / 2.0
            d.line([(x1 + .5) * s, (y1 + .5) * s, (x2 + .5) * s, (y2 + .5) * s],
                   fill=col(c), width=max(1, int(w * s)))
    return im
