# Jiten-Tools

Tools and assembly hacks to import western languages to Gyakuten Saiban Jiten (ぎゃくてんさいばんじてん - gamecode AJXJ).

Work in progress.

# Usage

Extract data and assets from the original (and decrypted) rom:
```
py main.py -e [path of the rom]
```

Import the modified assets and build a new rom:
```
py main.py -i [path of the new rom]
```

# Current features

- Text and images full export / import
- New font with flexible width instead of a full monospace one
- Character-based coloring and hitboxes for page jumping instead of OAM-based
- 8 lines instead of 6 for the encyclopedia
- 3 lines openings and credits text box (still not totally functional)

# To Do

## Encyclopedia

- Fix the issue with hitboxes not covering the entirety of the text in the encyclopedia
- Switch the text from red to blue before jumping to match how it originally behaves
- Cut the encyclopedia.xlsx file into several files with reasonable sizes, depending on games, categories, etc.

## Openings/credits

- Correct display of the 3 lines in the textbox
- Increase text box height to match NDS western textbox
- Modify the "next" arrow graphic/animation
- 3-4: make possible the translation of the PC stuff
- 3-2: make possible the translation of the "Guilty" animation

## Tools

- Previewer for encyclopedia
- Automatically generate graphics for character names, animation names, etc. from text instead of doing everything manually


# How it works

The **_project** folder will contain everything you need to modify.

The **_project/original** folder will have original files and original assets. Don't delete or modify files from this folder.
The **_project/new** folder will contain the new files that you modified and the new rom will be build from its contents.

## Font

The font is located in **_project/new/font**. It already have French characters glyphs and metrics.
Too save space, the encoding now uses 1 byte per character. The bytes 00 and 23 are special characters, so you can map a total of 254 different characters.
If you want to add a new character, put it somewhere in the font.png font sheet, and modify the fontmap.csv file. This file follows the layout of the sheet: the cell D7 refers to the character in the 7th row, 4th column of the sheet. Enter <character>|<character_width> in the correct cell.

## Images

Images are originally extracted to **_project/original/images**. After modifying an image, put it at **_project/new/images** with the exact same relative path so it's taken into account in the rebuilding.
Images are extracted as palette-indexed png, and they need to stay in this format to be reimported. You can of course modify the palette.

## Text

The text is extracted to **_project/new/text**. For the encyclopedia, simply modify the Translation column of the xlsx files; for openings/credits, simply modify the txt files.

## Sound

There is nothing in this project for direct SDAT editing, but you can use external tools like Tinke to edit the .sdat file.

## Rom data

This project is using Aetias' ds-rom to extract and rebuild the .nds rom. You can modify stuff like game name, game , banner, etc. in the yaml files located in the **_project/new/rom** folder.

# Credits

Rom extraction/building: Aetias' ds-rom: https://github.com/AetiasHax/ds-rom
Assembly hacks insertion: Kingcom's armips: https://github.com/Kingcom/armips 