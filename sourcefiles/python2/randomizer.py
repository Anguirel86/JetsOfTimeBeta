from shutil import copyfile
import struct as st
from os import stat
from time import time
import treasurewriter as treasures
import specialwriter as hardcoded_items
import shopwriter as shops
import characterwriter as char_slots
import logicwriter as keyitems
import random as rand
import patcher as patches
def tenthousands_digit(digit):
    digit = st.unpack(">B",digit)
    digit = int(digit[0]) * 0x10000
    return digit       
def make_number(digit,digit2):
       digit2 = st.unpack(">H",digit2)
       digit2 = int(digit2[0])
       number = digit + digit2
#       print "{:X}".format(number)
       return number
def get_length(length):
       length = st.unpack(">H",length)
       length = int(length[0])
       return length
def write_data(length,pointer,position):
        bRepeatable = False
        if length == 0:
            length = p.read(2)
            length = get_length(length)
            data = get_data()            
            position += 3
            bRepeatable = True
        while length > 0:
          if not bRepeatable:
            data = get_data()
            position += 1
          f.seek(pointer)
          f.write(st.pack("B",data))
          pointer += 1
          length -= 1
        return position
def get_data():
        data = p.read(1)
        data = st.unpack("B",data)
        data = int(data[0])
        return data
if __name__ == "__main__":
     flags = ""
     sourcefile = raw_input("Enter ROM please.")
     seed = raw_input("Enter seed(or leave blank if you want to randomly generate one).")
     if seed is None or seed == "":
        seed = time()
     seed = int(seed)
     seed = seed % (10**10)
     rand.seed(seed)
     glitch_fixes = raw_input("Would you like to disable (most known) glitches? Y/N ")
     if glitch_fixes == "Y":
        flags = flags + "g" 
     fast_move = raw_input("Would you like to move faster on the overworld/Epoch? Y/N ")
     if fast_move == "Y":
        flags = flags + "s"
     sense_dpad = raw_input("Would you like faster dpad inputs in menus? Y/N ")
     if sense_dpad == "Y":
        flags = flags + "d"
     outfile = sourcefile.split(".")
     outfile = str(outfile[0])
     outfile = "%s.%s.%d.sfc"%(outfile,flags,seed)
     try:
        size = stat(sourcefile).st_size
     except WindowsError:
        raw_input("""Try placing the ROM in the same folder as this program.
Also, try writing the extension(.sfc/smc).""")
     if size % 0x400 == 0:
        copyfile(sourcefile, outfile)
     elif size % 0x200 == 0:
        print "SNES header detected. Removing header from output file."
        f = open(sourcefile, 'r+b')
        data = f.read()
        f.close()
        data = data[0x200:]
        open(outfile, 'w+').close()
        f = open(outfile, 'r+b')
        f.write(data)
        f.close()
     print "Applying patch. This might take a while."
     p = open("patch.ips","r+b")
     position = 5
     f = open(outfile,'r+b')
     while position < 351306:
       p.seek(position)
       pointer1 = p.read(1)
       pointer1 = tenthousands_digit(pointer1)
       position += 1
       pointer2 = p.read(2)
       pointer = make_number(pointer1,pointer2)
       position += 2
       length = p.read(2)
       length = get_length(length)
       position += 2
       position = write_data(length,pointer,position)
     p.close
     f.close
     patches.patch_file("patches/patch_codebase.txt",outfile)
     if glitch_fixes == "Y":
        patches.patch_file("patches/save_anywhere_patch.txt",outfile)
        patches.patch_file("patches/unequip_patch.txt",outfile)
        patches.patch_file("patches/fadeout_patch.txt",outfile)
        patches.patch_file("patches/hp_overflow_patch.txt",outfile)
     if fast_move == "Y":
        patches.patch_file("patches/fast_overworld_walk_patch.txt",outfile)
        patches.patch_file("patches/faster_epoch_patch.txt",outfile)
     if sense_dpad == "Y":
        patches.patch_file("patches/faster_menu_dpad.txt",outfile)
     print "Randomizing treasures..."
     treasures.randomize_treasures(outfile)
     hardcoded_items.randomize_hardcoded_items(outfile)
     print "Randomizing shops..."
     shops.randomize_shops(outfile)
     print "Randomizing character locations..."
     char_locs = char_slots.randomize_char_positions(outfile)
     print "Now placing key items..."
     keyitems.randomize_keys(char_locs,outfile)
     print "Randomization completed successfully."
     raw_input("Press Enter to exit.")