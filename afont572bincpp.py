#Python 3.7.8+
import re
import sys

MSG_ERR = 'ERROR:'

EXCODE_FAIL = 1
EXCODE_OK   = 0

def proccessArgs5(args):
  INDENT = "    "

  pattern = re.compile(r"^[ \t]*((?:0x)?[0-9a-f]{1,2})[ \t]*,[ \t]*((?:0x)?[0-9a-f]{1,2})[ \t]*,[ \t]*((?:0x)?[0-9a-f]{1,2})[ \t]*,[ \t]*((?:0x)?[0-9a-f]{1,2})[ \t]*,[ \t]*((?:0x)?[0-9a-f]{1,2})[ \t]*(,|)[ \t]*(.*|)$", flags=re.IGNORECASE)

  with open(args.fontin, "rt", encoding="utf-8") as f:
    linesin = [linein.rstrip("\n\r") for linein in f]

  ci = 0
  linesout = []
  for linein in linesin:
    m = pattern.match(linein)
    if m:
      ###lineout = m.group(1)+", "+m.group(2)+", "+m.group(3)+", "+m.group(4)+", "+m.group(5)+m.group(6)
      values = [int(m.group(i), 0) for i in range(1,6)]

      lineout = ""
      lineout += "\n"
      lineout += INDENT + "// 0x{:02x} {:3d}".format(ci, ci)
      if (ci >= 0x20) and (ci < 127):
        lineout += " '{}'".format(chr(ci))
      else:
        if (m.group(7) != ""):
          lineout += "    "

      if (m.group(7) != ""):
        lineout += " " + m.group(7)

      lineout += "\n"
      lineout += ",\n".join(INDENT + "0b{:08b}".format(v) for v in values)+m.group(6)
      linesout.append(lineout)
      ci += 1
    else:
      linesout.append(linein)

  with open(args.fontout, "wt", encoding="utf-8") as f:
    for lineout in linesout:
      f.write(lineout+'\n')      

  return EXCODE_OK

def proccessArgs(args):
  INDENT = "    "

  head = re.compile(r".*\[\s*\].*{\s*", flags=re.IGNORECASE)
  pattern = re.compile(r"((?:0x|0b)?[0-9a-f]{1,8})[ \t]*(,|\)[ \t]*,|)[ \t]*(//.*$|)", flags=re.IGNORECASE)
  tail = re.compile(r"\s*}\s*;", flags=re.IGNORECASE)

  with open(args.fontin, "rt", encoding="utf-8") as f:
    linesin = [linein.rstrip("\n\r") for linein in f]

  FONT_IN_BYTES_PER_CHAR = 5

  byteIndex = 0
  charIndex = 0
  linesout = []

  head_found = False
  tail_found = False

  for linein in linesin:
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
        #print(MSG_ERR+"Invalid value in line: "+linein+":"+m.group(1))
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

  with open(args.fontout, "wt", encoding="utf-8") as f:
    for lineout in linesout:
      f.write(lineout+'\n')

  byteCount = byteIndex
  charCount = 256
  goodCount = charCount * FONT_IN_BYTES_PER_CHAR

  if (byteCount != goodCount):
    print(f"WARN: font size {byteCount} bytes does not match expected size of {goodCount} bytes")

  print(f"Converted {byteCount} bytes")

  return EXCODE_OK

def main(argv):

  import argparse

  parser = argparse.ArgumentParser(description='Adafruit gfx FONT 5x7 definition converter to 0bxxxxxxxx')
  parser.add_argument('fontin', type=str, help='Input 5x7 font file (.h or .cpp)')
  parser.add_argument('fontout', type=str, help='Output 5x7 font file (.h or .cpp)')
  parser.add_argument('--nocomcode', help='Do not add char code comments', action='store_true')
  args = parser.parse_args(argv)

  try:
    if proccessArgs(args) != 0:
      return(EXCODE_FAIL)
    print("OK!")
  except Exception as e:
    if hasattr(e,'reason'): print("FAIL "+e.reason); 
    else: print("FAIL:"+str(e))
    raise e # uncomment this like to have traceback printed
    print(MSG_ERR+"Error while in operation")
    return(EXCODE_FAIL)
  
  return(EXCODE_OK)

if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
