import os
from PIL import Image, ImageDraw, ImageOps      
import cv2
import numpy as np
import math

# Zielgröße nach Erweiterung
TARGET_WIDTH = 780
TARGET_HEIGHT = 1075

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
    
    
def paint_shape(contour, image, padding, right, color):
        
    height, width = image.shape[:2]
     # Obersten Punkt der Kontur finden
    #topmost = tuple(contour[contour[:, :, 1].argmin()][0])
    
    if contour is not None and len(contour) > 0 and contour.ndim == 3:
        topmost = tuple(contour[contour[:, :, 1].argmin()][0])
    else:
        #print("Ungültige oder leere Kontur.")
        #cv2.drawContours(image, [contour], -1, (255, 0, 0), 2)
        return image


    # Beispiel: nur Punkte oberhalb eines bestimmten y-Werts
    y_threshold=topmost[1]+10
    filtered_contour = np.array([pt for pt in contour if pt[0][1] < y_threshold])
    #cv2.drawContours(image, [filtered_contour], -1, (0, 255, 0), 2)

    # Gerade an Kontur anpassen
    [vx, vy, x, y] = cv2.fitLine(filtered_contour, cv2.DIST_L2, 0, 0.01, 0.01)

    # Länge der Linie
    line_length = 1000

    # Endpunkt berechnen
    if(right):
        end_point = (int(topmost[0] + vx * line_length), int(topmost[1] + vy * line_length))
    else:
        end_point = (int(topmost[0] - vx * line_length), int(topmost[1] - vy * line_length))

    if 5<end_point[0]<width-5 or padding+5<topmost[0]<width-padding-5 or end_point[1]>topmost[1]:
        return image

    # Linie zeichnen
    #cv2.line(image, topmost, end_point, (0, 0, 0), thickness=1)

    if (right):
        pts = np.array([topmost, end_point, [width, end_point[1]],[width, height], [width-padding, height]], np.int32)
    else:
        pts = np.array([topmost, end_point, [0, end_point[1]],[0, height], [topmost[0], height]], np.int32)
        
    #print(color)
    cv2.fillPoly(image, [pts], color)
    
    
    #cv2.drawContours(image, [filtered_contour], -1, (0, 0, 255), 2)
    
    return image
    
def extend_black_v_shape(orgimg, extimg, pad_bottom, pad_left, pad_right):
    
    # TODO nur machen wenn wir die schwarzen ecken haben
    
    
    
    width, height = extimg.size
    
    

    
    
    
    # In NumPy-Array umwandeln
    image_np = np.array(extimg)

    # Farbkanäle von RGB nach BGR konvertieren
    image = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)


    #imgName="parabel_high.jpg"
    #imgName="parabel.jpg"
    #imgName="bild.png"
    # Bild laden
    #img = cv2.imread(imgName)
    #extension_width=18
    # Dimensionen des Originalbilds
    #height, width = img.shape[:2]
    # Neues weißes Bild mit erweiterter Breite erstellen
    #new_width = width + extension_width
    #image = np.ones((height, new_width, 3), dtype=np.uint8) * 255
        
    # Originalbild in das neue Bild einfügen
    #image[:, :width] = img
        
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Schwellenwert anwenden, um dunkle Bereiche zu isolieren
    _, binary = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY_INV)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    binary_cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    # Konturen finden
    #contours, _ = cv2.findContours(binary_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours, _ = cv2.findContours(binary_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter: große Fläche + im unteren Bildbereich
    min_area = 20
    height = binary.shape[0]
    #bottom_threshold = int(height * 0.7)
    bottom_threshold = 700

    filtered_contours = [
        cnt for cnt in contours
        if cv2.contourArea(cnt) > min_area and cv2.boundingRect(cnt)[1] + cv2.boundingRect(cnt)[3] > bottom_threshold
    ]
    filtered_contours2 = []
    for cont in filtered_contours:
        #cv2.drawContours(image, [cont], -1, (0, 255, 0), 2)
        if cont is not None and len(cont) > 0 and cont.ndim == 3:
            topmost = tuple(cont[cont[:, :, 1].argmin()][0])
        else:
            #print("Ungültige oder leere Kontur.")
            cv2.drawContours(image, [cont], -1, (255, 0, 0), 2)
            return image
        if 700<topmost[1]<900 and (topmost[0]<pad_left+5 or topmost[0]>width-pad_right-5 ):
            #cv2.drawContours(image, [cont], -1, (0, 0, 255), 2)
            filtered_contours2.append(cont)
            
    if filtered_contours2 is None or len(filtered_contours2)==0:
        return image
    largest_contour = max(filtered_contours2, key=cv2.contourArea)
    
    
    #largest_contour = max(contours, key=cv2.contourArea)
    #x_threshold=width/2
    textboxDistance=40
    x_threshold_left=pad_left+textboxDistance
    x_threshold_right=width-pad_right-textboxDistance
    filtered_contour_left = np.array([pt for pt in largest_contour if pt[0][0] < x_threshold_left and pt[0][0] > pad_left])
    filtered_contour_right = np.array([pt for pt in largest_contour if pt[0][0] > x_threshold_right and pt[0][0] < width-pad_right])
    
    #getFillingColor
    # Farbe aus der unteren Mitte entnehmen
    sample_y = height - 10
    sample_x = width // 2
    r,g,b,a = extimg.getpixel((sample_x, sample_y))
    color = (b,g,r,a)
    
    #cv2.drawContours(image, [largest_contour], -1, (255, 0, 0), 2)
    image=paint_shape(filtered_contour_right, image, pad_right, True, color)
    image=paint_shape(filtered_contour_left, image, pad_right, False, color)
   

    # Kontur SEHEN
    #cv2.drawContours(image, [filtered_contour_left], -1, (255, 0, 0), 2)
    #cv2.drawContours(image, [filtered_contour_right], -1, (0, 255, 0), 2)
    #cv2.drawContours(image, [filtered_contour], -1, (0, 0, 255), 2)
    
    return image
    
# Hauptverarbeitung
def process_images():
    for filename in os.listdir():
        if filename.lower().endswith(".png"):
            img = Image.open(filename).convert("RGBA")
            img = fill_transparent_corners(img)

            pad_left, pad_right = calculate_padding(img.width, TARGET_WIDTH)
            pad_top, pad_bottom = calculate_padding(img.height, TARGET_HEIGHT)

            extended_img = mirror_edges(img, pad_left, pad_right, pad_top, pad_bottom)
            
            extended_img = extend_black_v_shape(img, extended_img, pad_bottom, pad_left, pad_right)
            # Ergebnis speichern
            cv2.imwrite("Done"+filename, extended_img)

            #output_name = f"finally_{filename}"
            #extended_img.save(output_name)

process_images()
