import os
from PIL import Image, ImageDraw, ImageOps

# Zielgröße nach Erweiterung
TARGET_WIDTH = 815
TARGET_HEIGHT = 1110

# Berechne Erweiterung pro Seite
def calculate_padding(original_size, target_size):
    total_padding = target_size - original_size
    left = total_padding // 2
    right = total_padding - left
    return left, right

#4 Spiegelung der Ränder mit optionaler Betonung des unteren mittleren Bereichs
def mirror_edges_with_bottom_focus(img, pad_left, pad_right, pad_top, pad_bottom):
    width, height = img.size
    new_img = Image.new("RGBA", (width + pad_left + pad_right, height + pad_top + pad_bottom))

    # Originalbild einfügen
    new_img.paste(img, (pad_left, pad_top))

    # Linker Rand
    if pad_left > 0:
        left_strip = img.crop((0, 0, pad_left, height))
        new_img.paste(left_strip.transpose(Image.FLIP_LEFT_RIGHT), (0, pad_top))

    # Rechter Rand
    if pad_right > 0:
        right_strip = img.crop((width - pad_right, 0, width, height))
        new_img.paste(right_strip.transpose(Image.FLIP_LEFT_RIGHT), (width + pad_left, pad_top))

    # Oberer Rand
    if pad_top > 0:
        top_strip = new_img.crop((0, pad_top, width + pad_left + pad_right, pad_top + pad_top))
        new_img.paste(top_strip.transpose(Image.FLIP_TOP_BOTTOM), (0, 0))

    # Unterer Rand mit Fokus auf Mitte
    if pad_bottom > 0:
        center_width = width // 3
        center_crop = img.crop((width//2 - center_width//2, height - pad_bottom, width//2 + center_width//2, height))
        center_strip = center_crop.resize((width + pad_left + pad_right, pad_bottom))
        new_img.paste(center_strip, (0, pad_top + height))

    return new_img
    
#3 Spiegele Randbereiche
def mirror_edges(img, pad_left, pad_right, pad_top, pad_bottom):
    width, height = img.size
    new_img = Image.new("RGBA", (width + pad_left + pad_right, height + pad_top + pad_bottom))

    # Originalbild einfügen
    new_img.paste(img, (pad_left, pad_top))

    # Ränder spiegeln
    if pad_left > 0:
        left_strip = img.crop((0, 0, pad_left, height))
        new_img.paste(left_strip.transpose(Image.FLIP_LEFT_RIGHT), (0, pad_top))
    if pad_right > 0:
        right_strip = img.crop((width - pad_right, 0, width, height))
        new_img.paste(right_strip.transpose(Image.FLIP_LEFT_RIGHT), (width + pad_left, pad_top))
    if pad_top > 0:
        top_strip = new_img.crop((0, pad_top, width + pad_left + pad_right, pad_top + pad_top))
        new_img.paste(top_strip.transpose(Image.FLIP_TOP_BOTTOM), (0, 0))
    if pad_bottom > 0:
        bottom_strip = new_img.crop((0, pad_top + height - pad_bottom, width + pad_left + pad_right, pad_top + height))
        new_img.paste(bottom_strip.transpose(Image.FLIP_TOP_BOTTOM), (0, pad_top + height))

    return new_img
    
#3 Fülle transparente Ecken durch Spiegelung
def fill_transparent_corners(img):
    width, height = img.size
    pixels = img.load()

    # Ecken definieren
    corners = {
        "tl": (0, 0),
        "tr": (width - 1, 0),
        "bl": (0, height - 1),
        "br": (width - 1, height - 1)
    }

    for name, (x, y) in corners.items():
        if pixels[x, y][3] == 0:  # Transparente Ecke
            # Bereich zum Spiegeln definieren
            box = None
            if name == "tl":
                box = (0, 0, 35, 35)
            elif name == "tr":
                box = (width - 35, 0, width, 35)
            elif name == "bl":
                box = (0, height - 35, 35, height)
            elif name == "br":
                box = (width - 35, height - 35, width, height)

            if box:
                alpha = img.crop(box).split()[-1]
                mask = alpha.point(lambda p: 255 if p < 240 else 0).convert("L")
                region = img.crop(box).transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
                img.paste(region, box, mask=mask)

    return img
    
def extend_black_v_shape_old(img, pad_bottom):
    width, height = img.size
    new_height = height + pad_bottom
    new_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    new_img.paste(img, (0, 0))

    draw = ImageDraw.Draw(new_img)

    # Farbe aus der unteren Mitte entnehmen
    sample_y = height - 5
    sample_x = width // 2
    color = img.getpixel((sample_x, sample_y))

    # Linkes Dreieck
    draw.polygon([
        (0, 0.75 * height),
        (18, 0.75 * height + 2 * pad_bottom),
        (0, 0.75 * height + 2* pad_bottom)
    ], fill=color)

    # Rechtes Dreieck
    draw.polygon([
        (width * 0.75, height),
        (width, height),
        (width, new_height)
    ], fill=color)

    return new_img    
    
def extend_black_v_shape(img, pad_bottom, pad_left, pad_right):
    width, height = img.size
    new_height = height + pad_bottom
    new_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    new_img.paste(img, (0, 0))

    draw = ImageDraw.Draw(new_img)

    # Farbe aus der unteren Mitte entnehmen
    sample_y = height - 5
    sample_x = width // 2
    color = img.getpixel((sample_x, sample_y))

    # Linkes Dreieck
    draw.polygon([
        (0, 0.75 * height),
        (pad_left,  0.75 * height),
        (pad_left, 0.85 * height),
        (0, 0.85*height)
    ], fill=color)

    # Rechtes Dreieck
    draw.polygon([
        (width, 0.75 * height),
        (width - pad_right,  0.75 * height),
        (width - pad_right, 0.85 * height),
        (width, 0.85*height)
    ], fill=color)

    return new_img
    
# Hauptverarbeitung
def process_images():
    for filename in os.listdir():
        if filename.lower().endswith(".png"):
            img = Image.open(filename).convert("RGBA")
            img = fill_transparent_corners(img)

            pad_left, pad_right = calculate_padding(img.width, TARGET_WIDTH)
            pad_top, pad_bottom = calculate_padding(img.height, TARGET_HEIGHT)

            extended_img = mirror_edges(img, pad_left, pad_right, pad_top, pad_bottom)
            
            # das macht einen schwrzen balken der nicht immer gut ist.
            # extended_img = extend_black_v_shape(extended_img, pad_bottom, pad_left, pad_right)

            output_name = f"finally_{filename}"
            extended_img.save(output_name)

process_images()
