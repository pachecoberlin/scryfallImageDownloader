# scryfallImageDownloader
Download images from scryfall, extend and mirror edges

New method which is almost the same, go to devprint.taxiera.net,(if you like go to advanced settings and checkl Upscale Decklist Images, but i did not noticed any difference even with lens) click on Import from Decklist paste the list e.g. from moxfield with set and number and it will get you the scryfall images and extend them, it does also something to the edges which idk if i like it. 

First create a deck on scryfall. You can export from Moxfield, but may have some errors and/or missing cards. Vielleicht besser die Bilder bei Scryfall auswählen.
Second export as Spreadsheet (csv file).
First Parameter is path to csv sheet.
Images are downloaded.
see result.log for missing images, normally double sided fail

Then you may copy and call justmirrored.py in folder where images are to extend the images and mirror the edges (or use extend.py to extend the black bottom border).

Go to https://proxyprint.taxiera.net/ and use Card size standard, size in mm 210 x 297, Cols 3, Enable bleed edge, bleed edge 2mm, some color, guides width 1 px, unchecked guides at bleed edge. See proxyprint.taxiera.net.jpg
Use mtg.jpeg for the card backs. Click on card to double it.
For US Letter size, which my 310 gsm blackcard stock is use 216 x 283 for 3mm bleed, but may have problems since paper is only 216x279 or even more accurate its 217x280. So you can set 216x279(probably better 217x280) with 2mm bleed