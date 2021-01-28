import random as rand
import struct as st
import patcher as patch

# Start marker:  0xC4700
# Boss stats:  
# Byte 0+1 - HP
# Byte 2 - Level
# Byte 10 - Magic
# Byte 13 - Magic Defense
# Byte 14 - Offense
# Byte 15 - Defense

# Start reward marker:  0xC5E00
# Byte 0+1 - XP
# Byte 2+3 - GP
# Byte 4 - Item Drop
# Byte 5 - Charm Item
# Byte 6 - TP

# Bosses:  04 - Krawlie, 90 - Yakra, 95 - Golem, 99 - Masa & Mune, 9B - Nizbel, 9C - Nizbel II, 9D - Slash, 9E - Slash w/ Sword, 9F - Flea
#          A1 - Dalton, A2 - Dalton Plus, A5 - Super Slash, A9 - Heckran, BB - Flea Plus, BD - Rust Tyrano, C0 - Atropus XR, C7 - Yakra XIII, F3 - Golem Boss

# Yakra
# Masa&Mune, Heckran
# Slash, Flea, Golem, Twin Golem
# Rust Tyrano, Yakra 13, Nizbel II
spots = [0x1B38F0, 0x377824, 0x24EC85, 0x3ABF86, 0x1ED226, 0x1BEBBB, 0x38821C, 0x1B8A4C, 0x36F40B, 0x5FBBA]
spot_tiers = [0, 1, 1, 2, 2, 2, 2, 3, 3, 3]

# krawlie_spot = [500, 12, 5, 50, 40, 150, 100, 500, 5]
#yakra_spot = [0x1B38C2, 920, 6, 9, 50, 16, 127, 200, 600, 5] # Changes:  50 -> 200 XP
#golem_spot = [0x1BEBBB, 7000, 34, 22, 50, 105, 127, 1000, 2000, 35]
#masamune_spot = [0x377824, 3600, 16, 6, 50, 40, 127, 500, 1500, 10]
#nizbel_spot = [0x18FC30, 4200, 18, 33, 100, 60, 252, 500, 0, 10]
#nizbel2_spot = [0x5FBBA, 6500, 25, 35, 50, 85, 127, 880, 0, 10]
# slash_spot = [3200, 21, 6, 50, 40, 127, 0, 0, 0]
#slashsword_spot = [0x3ABF86, 5200, 22, 7, 60, 70, 127, 880, 1500, 10]
#flea_spot = [0x1ED226, 4120, 21, 10, 60, 45, 150, 880, 1000, 10]
#dalton_spot = [3500, 32, 50, 50, 20, 127, 1000, 2500, 30]
#daltonplus_spot = [2800, 32, 20, 50, 20, 127, 2500, 2000, 40]
#superslash_spot = [2800, 37, 15, 50, 180, 127, 2500, 2000, 30]
#heckran_spot = [0x24EC52, 2100, 13, 16, 50, 40, 253, 250, 1500, 10]
# fleaplus_spot = [2500, 35, 15, 50, 120, 127, 1000, 0, 15]
#rusttyrano_spot = [0x1B8A4C, 25000, 35, 30, 50, 1, 127, 3000, 3000, 40]
#atropus_spot = [6000, 38, 10, 50, 38, 127, 0, 0, 0]
#yakra13_spot = [0x36F40B, 18000, 45, 18, 50, 200, 127, 3500, 2000, 40]
#golemboss_spot = [15000, 34, 18, 50, 40, 127, 2500, 2000, 40]

# Krawlie, Yakra, Golem, Masa & Mune, Nizbel, Nizbel II, Slash w/ Sword, Flea, Dalton, Dalton Plus, Heckran, Super Slash, Flea Plus, RustTyrano, Atropos XR, Yakra XIII, Golem Boss
eligible_bosses = [0x04, 0x90, 0x95, 0x99, 0x9B, 0x9C, 0x9E, 0x9F, 0xA1, 0xA2, 0xA9, 0xBA, 0xBB, 0xBD, 0xC0, 0xC7, 0xF3]
boss_tiers = [0, 0, 2, 1, 2, 3, 2, 2, 2, 3, 1, 2, 2, 3, 2, 3, 2]

def randomize_bosses(outfile):
    eligible_bosses = [0x04, 0x90, 0x95, 0x99, 0x9B, 0x9C, 0x9E, 0x9F, 0xA1, 0xA2, 0xA9, 0xBA, 0xBB, 0xBD, 0xC0, 0xC7, 0xF3]
    boss_tiers = [0, 0, 2, 1, 2, 3, 2, 2, 2, 3, 1, 2, 2, 3, 2, 3, 2]

    f = open(outfile,"r+b")
    lnI = 0
    for spot in spots:
        boss = rand.randrange(0,len(eligible_bosses),1)
        boss_tier = boss_tiers[boss]
        spot_tier = spot_tiers[lnI]
        
        f.seek(0xC4700 + (eligible_bosses[boss] * 23) + 0);
        hp = int.from_bytes(f.read(2), byteorder='little', signed=False);
        f.seek(0xC4700 + (eligible_bosses[boss] * 23) + 2);
        level = int.from_bytes(f.read(1), byteorder='little', signed=False);
        f.seek(0xC4700 + (eligible_bosses[boss] * 23) + 10);
        magic = int.from_bytes(f.read(1), byteorder='little', signed=False);
        #f.seek(0xC4700 + (eligible_bosses[boss] * 23) + 13);
        #magic_defense = int.from_bytes(f.read(1), byteorder='little', signed=False);
        f.seek(0xC4700 + (eligible_bosses[boss] * 23) + 14);
        offense = int.from_bytes(f.read(1), byteorder='little', signed=False);
        #f.seek(0xC4700 + (eligible_bosses[boss] * 23) + 15);
        #defense = int.from_bytes(f.read(1), byteorder='little', signed=False);

        f.seek(0xC5E00 + (eligible_bosses[boss] * 7) + 0);
        xp = int.from_bytes(f.read(2), byteorder='little', signed=False);
        f.seek(0xC5E00 + (eligible_bosses[boss] * 7) + 2);
        gp = int.from_bytes(f.read(2), byteorder='little', signed=False);
        f.seek(0xC5E00 + (eligible_bosses[boss] * 7) + 6);
        tp = int.from_bytes(f.read(1), byteorder='little', signed=False);

        boss_power = 1
        if (spot_tier - boss_tier == -3):
            boss_power = .7
        elif (spot_tier - boss_tier == -2):
            boss_power = .85
        elif (spot_tier - boss_tier == -1):
            boss_power = .95
        elif (spot_tier - boss_tier == 1):
            boss_power = 1.15
        elif (spot_tier - boss_tier == 2):
            boss_power = 1.25
        elif (spot_tier - boss_tier == 3):
            boss_power = 1.45
        
        hp = min(int(pow(hp, boss_power)), 65000)
        level = min(int(pow(level, boss_power)), 90)
        magic = min(int(pow(magic, boss_power)), 250)
        offense = min(int(pow(offense, boss_power)), 250)
        xp = min(int(pow(xp, boss_power)), 65000)
        gp = min(int(pow(gp, boss_power)), 65000)
        tp = min(int(pow(tp, boss_power)), 250)

        f.seek(spot)
        f.write(st.pack("B",eligible_bosses[boss]))
        # To avoid graphical glitches at the Masa & Mune spot
        if lnI == 1:
            f.seek(spot + 1)
            f.write(st.pack("B", 0x03))

        f.seek(0xC4700 + (eligible_bosses[boss] * 23) + 0);
        f.write(st.pack("<H",hp))
        f.seek(0xC4700 + (eligible_bosses[boss] * 23) + 2);
        f.write(st.pack("B",level))
        f.seek(0xC4700 + (eligible_bosses[boss] * 23) + 10);
        f.write(st.pack("B",magic))
        #f.seek(0xC4700 + (eligible_bosses[boss] * 23) + 13);
        #magic_defense = int.from_bytes(reader.read(1), byteorder='little', signed=False);
        f.seek(0xC4700 + (eligible_bosses[boss] * 23) + 14);
        f.write(st.pack("B",offense))
        #f.seek(0xC4700 + (eligible_bosses[boss] * 23) + 15);
        #defense = int.from_bytes(reader.read(1), byteorder='little', signed=False);

        f.seek(0xC5E00 + (eligible_bosses[boss] * 7) + 0);
        f.write(st.pack("<H",xp))
        f.seek(0xC5E00 + (eligible_bosses[boss] * 7) + 2);
        f.write(st.pack("<H",gp))
        f.seek(0xC5E00 + (eligible_bosses[boss] * 7) + 6);
        f.write(st.pack("B",tp))

        del eligible_bosses[boss]
        del boss_tiers[boss]

        lnI = lnI + 1