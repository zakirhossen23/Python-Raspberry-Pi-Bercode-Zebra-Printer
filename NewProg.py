import airtable
import asyncio
from datetime import datetime
import evdev
import logging
import os
import requests
import sys
import threading
import time
from time import sleep
import zpl
from pygame import *
from pydub import AudioSegment
from pydub.playback import play

MY_NAME = 'Rotary3'
ORDER_ITEM_STATUS = 'pressed'

AIRTABLE_API_KEY = 'keydk7e5EQMNQiDSY' # Insert your API Key
AIRTABLE_BASE_ID = 'app6ZdMjuZezqltZo' # Insert the Base ID of your working base
AIRTABLE_TABLE_NAME = 'Pi import' # Insert the name of the table in your working base

last_scan = ''
prevBarcode = ''

# Key to character table only lists commonly used characters
keymap = {
  'KEY_0': u'*',
  'KEY_1': u'1',
  'KEY_2': u'2',
  'KEY_3': u'3',
  'KEY_4': u'4',
  'KEY_5': u'5',
  'KEY_6': u'6',
  'KEY_7': u'7',
  'KEY_8': u'8',
  'KEY_9': u'9',
  'KEY_A': u'A',
  'KEY_B': u'B',
  'KEY_C': u'C',
  'KEY_D': u'D',
  'KEY_E': u'E',
  'KEY_F': u'F',
  'KEY_G': u'G',
  'KEY_H': u'H',
  'KEY_I': u'I',
  'KEY_J': u'J',
  'KEY_K': u'K',
  'KEY_L': u'L',
  'KEY_M': u'M',
  'KEY_N': u'N',
  'KEY_O': u'O',
  'KEY_P': u'P',
  'KEY_Q': u'Q',
  'KEY_R': u'R',
  'KEY_S': u'S',
  'KEY_T': u'T',
  'KEY_U': u'U',
  'KEY_V': u'V',
  'KEY_W': u'W',
  'KEY_X': u'X',
  'KEY_Y': u'Y',
  'KEY_Z': u'Z',
  'KEY_TAB': u'\t',
  'KEY_SPACE': u' ',
  'KEY_COMMA': u',',
  'KEY_SEMICOLON': u';',
  'KEY_EQUAL': u'=',
  'KEY_LEFTBRACE': u'[',
  'KEY_RIGHTBRACE': u']',    
  'KEY_MINUS': u'-',
  'KEY_APOSTROPHE': u'\'',
  'KEY_GRAVE': u'`',
  'KEY_DOT': u'.',
  'KEY_SLASH': u'/',
  'KEY_BACKSLASH': u'\\',
  'KEY_ENTER': u'\n',

  }

def timeDiff(prevTime, timVal):
    difference = int(timVal - prevTime)
    return difference

def createZpl(infoStr):
    
    if len(infoStr) < 3:
        return
    
    print("creating Label for Printing", infoStr)
    #height = 80
    #image_width = 150
    
    height = 25 # 1 inch in mm
    image_width = 50 # 2 inch in mm
    
    l = zpl.Label(450,500)
    #l = zpl.Label(image_width,height)
    
    
    if (infoStr=="Error"):
        bercodezpl="^XA^CF0,100^FO50,50^FDERROR^FS^XZ"
    else:
        bercodezpl = "^XA^BY2,2,100^FO60,50^BC^FD"+infoStr+"^FS^XZ61764354"

    print("Got Label as :",bercodezpl)
  
    os.system("rm -f /home/pi/Documents/demo.txt")
    sleep(0.25)
    zfile = "/home/pi/Documents/demo.txt"
    f = open(zfile,"w") 
    f.write(bercodezpl)
    f.close()
    Status = False
    if os.path.isfile(zfile) is False:
        print("No such File present")
    else:
        print("File is present")
    sleep(0.25)
    try:
        os.system("sudo /usr/bin/lp -n 1 -o raw " + zfile)
        print("Print  success ....")
        Status = True
    except Exception as err:
        print("Cannot print ....")
    return Status
barcodeCount=0

# Trigger when input is detected
async def print_events(device):
  buf = ''
  global keymap, last_scan,barcodeCount
  async for event in device.async_read_loop():
    # key_up= 0 key_down= 1 key_hold= 2
    if event.type == evdev.ecodes.EV_KEY and event.value == 1:
      kv = evdev.events.KeyEvent(event)
      # In this modification, map the event to the character table
      if (kv.scancode == evdev.ecodes.KEY_ENTER):
        last_scan = buf
        print("Read Barcode is :", last_scan)
        barcodeCount+=1
        buf = ''
      else:
        try:
          buf += keymap.get(kv.keycode)
        except Exception as err:
          print("Got Exception")
          pass


def readInput():
    global last_scan, MY_NAME, pTable , prevBarcode,barcodeCount
    numpreV=""
    tbName = "Pi import"
    barcodeCount = 0
    #timVal = time.time()
    #prevTime = time.time()
    try:
        
        while True:
            
            if barcodeCount ==1:
                prevBarcode=last_scan
                import os
               
                # audiofile = "/home/pi/Documents/alarm.mp3"
            
                # song = AudioSegment.from_wav(audiofile)
                # play(song)
                print("prevBarcode is now:", prevBarcode)
                while True:
                    if barcodeCount == 2:
                        if prevBarcode ==last_scan:
                            createZpl((last_scan.lstrip()).rstrip()) #Newline to fill info in to ZPL var
                            print("Creating Duplicate Barcode", last_scan)
                            break
                        if prevBarcode !=last_scan:
                            createZpl("Error") 
                            audiofile = "/home/pi/Documents/alarm.mp3"
                            song = AudioSegment.from_wav(audiofile)
                            play(song)
                           
                            break
                        
                barcodeCount=0    
               
                continue        

    except KeyboardInterrupt:
        logging.debug('Keyboard interrupt')
    except Exception as err:
        logging.error(err)


if __name__ == '__main__':
    print("Stating Capturing barcode")
    import time
    import os
    audiofile = "/home/pi/Documents/alarm.mp3"
   
                   
    # for i in range(3):
    #     time.sleep(3)
    #     print("\a")
    thrId = threading.Thread(target=readInput)
    thrId.start()
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    print('The following devices were found:')
    for device in devices:
        print(device.path, device.name, device.phys)

    for device in devices:
        asyncio.ensure_future(print_events(device))

    loop = asyncio.get_event_loop()
    loop.run_forever()
    thrId.join()

