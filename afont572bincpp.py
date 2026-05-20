#!/usr/bin/env python3

#Python 3.7.8+
import re
import sys

# Default fixed font:
# Declared 5x7
# Actual font cell is 5x8, software uses 6x8 print cells (that is, adds 1px margin to right of each char)
# So, vertical pseudograph is linked, horizontal is not (that is, chars are separated by 1px enforced gap)
# Font char stored 5 bytes, matrix 8x5, rotated 90 deg CW
# Dumping chars as binary provides much more visibility of actual char pixel pattern

MSG_WARN = 'WARN:'
MSG_FAIL = 'FAIL:'

EXCODE_FAIL = 1
EXCODE_OK   = 0

def processArgs(args):
  INDENT = "    "

  head = re.compile(r".*\[\s*\].*{\s*", flags=re.IGNORECASE)

  # We do not support all the cases in regexp
  # some errors catched in int values parsing (special case is absense of last comma)
  # so we have adequete balance here
  pattern = re.compile(r"(0x[0-9a-f]+|0b[0-9a-f]+|0|[1-9][0-9]*)[ \t]*(,|\)[ \t]*,|)[ \t]*(//.*$|)", flags=re.IGNORECASE)

  tail = re.compile(r"\s*}\s*;", flags=re.IGNORECASE)

  with open(args.fontin, "rt", encoding="utf-8") as f:
    linesin = [linein.rstrip("\n\r") for linein in f]

  FONT_IN_BYTES_PER_CHAR = 5 # actual char matrix 5 bytes

  byteIndex = 0
  charIndex = 0
  linesout = []

  head_found = False
  tail_found = False

  lineNumber = 0

  for linein in linesin:
    lineNumber += 1
    if not head_found:
      if head.match(linein):
        head_found = True
        #print("Font head found")
        linesout.append(linein)
        #linesout.append("//head")
      else:
        linesout.append(linein)
      continue
    elif not tail_found:
      if tail.match(linein):
        tail_found = True
        #print("Font tail found")
        #linesout.append("//tail")
        linesout.append(linein)
        continue
    elif tail_found:
      linesout.append(linein)
      continue

    # Here is the body of the font, we need to process it

    if (linein.strip() ==""):
      # skip pure empty lines
      #linesout.append(linein)
      continue

    if (linein.strip().startswith("//")):
      # skip pure comment lines
      #linesout.append(linein)
      continue

    matches = list(pattern.finditer(linein))
    if (len(matches) == 0):
      linesout.append(linein)
      continue

    matchIndex = 0
    for m in matches:
      try:
        value = int(m.group(1), 0)
      except Exception as e:
        value = None
      
      if (value is None) or (value < 0) or (value > 255):
        print(MSG_WARN+f"Invalid value in line {lineNumber}: '{m.group(1)}' -- ignored")
        continue # skip invalid lines

      sep     = m.group(2)
      comment = m.group(3)

      if (sep.startswith(")")):
        #remove closing brace in separators in case we parse gfxfont
        #TODO: gfx font complete parsing is not complete yet, as only font body reparsed, all other definitions are kept
        sep = sep[1:]

      lineout = ""

      if (byteIndex % FONT_IN_BYTES_PER_CHAR == 0):
        if (args.nocomcode):
          pass
        else:
          lineout += "\n"
          lineout += INDENT + "// 0x{:02x} {:3d}".format(charIndex, charIndex)
          if (charIndex >= 0x20) and (charIndex < 127):
            lineout += " '{}'".format(chr(charIndex))
        lineout += "\n"

      lineout += INDENT + "0b{:08b}".format(value)+sep

      if (comment != ""):
        lineout += " "+comment

      linesout.append(lineout)
      byteIndex += 1
      matchIndex += 1

      if (byteIndex % FONT_IN_BYTES_PER_CHAR == 0):
        charIndex += 1

  if not head_found:
      print(MSG_FAIL + "Font array head not found")
      return EXCODE_FAIL

  if not tail_found:
      print(MSG_FAIL + "Font array tail not found")
      return EXCODE_FAIL

  charCount = 256
  byteCount = byteIndex
  goodCount = charCount * FONT_IN_BYTES_PER_CHAR

  if (byteCount != goodCount):
    print(MSG_WARN+f"font size {byteCount} bytes does not match expected size of {goodCount} bytes")

  with open(args.fontout, "wt", encoding="utf-8") as f:
    for lineout in linesout:
      f.write(lineout+'\n')

  print(f"Converted {byteCount} bytes")

  return EXCODE_OK

def main(argv):

  import argparse

  parser = argparse.ArgumentParser(description='Adafruit fixed font 5x7 definition converter to 0bxxxxxxxx')
  parser.add_argument('fontin', type=str, help='Input 5x7 font file (.h or .cpp)')
  parser.add_argument('fontout', type=str, help='Output 5x7 font file (.h or .cpp)')
  parser.add_argument('--nocomcode', help='Do not add char code comments', action='store_true')
  parser.add_argument('--debug', help='Print extra info on exceptions', action='store_true')
  args = parser.parse_args(argv)

  try:
    if processArgs(args) != 0:
      return(EXCODE_FAIL)
    print("OK!")
  except Exception as e:
    if hasattr(e,'reason'): print("FAIL "+e.reason); 
    else: print("FAIL:"+str(e))
    if (args.debug): raise e
    print(MSG_FAIL+"Error while in operation")
    return(EXCODE_FAIL)
  
  return(EXCODE_OK)

if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
