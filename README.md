# afont57
Adafruit GFX / Arduino GFX fixed 5x7 font utilities

## afont572gfxfont.py : Convert fixed LCD 5x7 font to gfxFont
Converter from fixed 5x8 (actually (5+1)x8) font definition (line in `glcdfont.c`) to drop-in replacement 6x8 gfxfont with same character size and same coordinates policy.

**The derived gfxfont may be installed by your code without altering the library, and then you may use it in a way you use default font.**

Useful to create gfxfont form localized glcdfont (like Cyrillic font). 
Especially good in case you already have English version of code, that uses default font and want to use Cyrillic (cp1251) or another local font.
In case of generated font as drop in replacement, you need just to switch the font, then you may use existing English texts, existing coordinates and existing text positions as you did with previous fixed font, while use localized code for messages where you need (for sue you may need context the text from utf-8 source to correct codepage in a runtime, if you edit text in Arduino IDE).

### Usage
```
afont572gfxfont.py source_font_file target_font_file
```
*Note: you may specify alternate font variable name by `--fontname` option, default font name is name of you target file*

Example
```
afont572gfxfont.py glcdfont.c gfxlcdfont.h
```

#### Font integration in Arduino code

In your code, use `setFont` function of `Adafruit_GFX.h` or `Arduino_GFX.h`:
```
...
#include "gfxlcdfont.h"
...

setup()
{
  ...
  tft.setFont(&gfxlcdfont);
  ...
}
...
```
*Note on `Adafruit_GFX` there was (and is) well-document bug in 8-bit ascii support.  
The old code has missing char 176. The bug is fixed long time ago, but for compatibility reasons, 
the code still uses broken path for default font. the gfxFont does not have this bug.
To enable correct codepage 437 support in default font, call `tft.cp437();` in begin of your setup.
This way both your default and gfxFont operates the same.*


### Special abilities
gfxFont specified in binary form, so you may see actual pattern of an character

Source alike
```
0x49, 0x32, 0x3A, 0x44, 0x44, 0x44, 0x3A, // O-umlaut
```

Becomes
```
    // 0x99 153
 FC(0b00111101,
    0b01000010,
    0b01000010,
    0b01000010,
    0b00111101), // O-umlaut
```

### Limitations

*Utility supports decimal, hex and bin values with no expressions, may not convert too exotic font bytes definitions*

## afont572bincpp.py : Convert fixed LCD 5x7 font source from hex to bin

This takes input fixed font definitions and changes bytes from hex to binary, so , so you may see actual pattern of an character.
The font content is not changes, just font itself becomes more visible

### Usage
```
afont572bincpp.py source_font_file target_font_file
```

### Conversion result

Source alike
```
0x49, 0x32, 0x3A, 0x44, 0x44, 0x44, 0x3A, // O-umlaut
```

Becomes
```
    // 0x99 153
    0b00111101,
    0b01000010,
    0b01000010,
    0b01000010,
    0b00111101, // O-umlaut
```

### Limitations

*Utility supports decimal, hex and bin values with no expressions, may not convert too exotic font bytes definitions*
