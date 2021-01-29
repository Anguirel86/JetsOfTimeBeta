# Python libraries
import enum
import random as rand
import struct as st

# jets of time libraries
import characterwriter as chars
import treasurewriter as treasure

#
# This script file implements the Chronosanity logic.
# It uses a weighted random distribution to place key items
# based on logical access rules per location.  Any baseline key
# item location that does not get a key item assigned to it will
# be assigned a random treasure.
#

# Script variables
locationGroups = []

#
# Enum type for the game's key items.
#
class KeyItems(enum.Enum):
  tomapop = 0xE3
  hilt = 0x51
  blade = 0x50
  dreamstone = 0xDC
  rubyknife = 0xE0
  gatekey = 0xD7
  jerky = 0xDB
  pendant = 0xD6
  moonstone = 0xDE
  prismshard = 0xD8
  grandleon = 0x42
  clone = 0xE2
  ctrigger = 0xD9
  heromedal = 0xB3
  roboribbon = 0xB8
# end KeyItems enum class

#
# Enum type used for the game's characters.
# Enum values correspond to the in game character IDs.
#
class Characters(enum.Enum):
  Crono = 0
  Marle = 1
  Lucca = 2
  Robo = 3
  Frog = 4
  Ayla = 5
  Magus = 6
# end Character enum class

#
# Enum representing various loot tiers that are used
# for assigning treasure to unused key item checks.
#
class LootTiers(enum.Enum):
  Mid = 0
  MidHigh = 1
  High = 2
# end LootTiers enum class

#
# The Game class is used to keep track of game state
# as the randomizer places key items.  It:
#   - Tracks key items obtained
#   - Tracks characters obtained
#   - Provides logic convenience functions
#  
class Game:
  def __init__(self, charLocations):
    self.characters = set()
    self.keyItems = set()
    self.earlyPendant = False
    self.lockedChars = False
    self.charLocations = charLocations
  
  #
  # Get the number of key items that have been acquired by the player.
  #
  # return: Number of obtained key items
  #
  def getKeyItemCount(self):
    return len(self.keyItems)
  
  #
  # Set whether or not this seed is using the early pendant flag.
  # This is used to determine when sealed chests and sealed doors become available.
  #
  # param: pflag - boolean, whether or not the early pendant flag is on
  #
  def setEarlyPendant(self, pflag):
    self.earlyPendant = pflag
  
  #
  # Set whether or not this seed is using the Locked Characters flag.
  # This is used to determine when characters become available to unlock further checks.
  #
  # param cflag - boolean, whether or not the locked characters flag is on.
  #
  def setLockedCharacters(self, cflag):
    self.lockedChars = cflag
  
  #
  # Check if the player has the specified character
  #
  # param: character - Name of a character
  # return: true if the character has been acquired, false if not
  #
  def hasCharacter(self, character):
    return character in self.characters
    
  #
  # Add a character to the set of characters acquired
  #
  # param: character - The character to add
  #
  def addCharacter(self, character):
    self.characters.add(character)
    
  #
  # Remove a character from the set of characters acquired
  #
  # param: character: The character to remove
  #
  def removeCharacter(self, character):
    self.characters.discard(character)
    
  #
  # Check if the player has a given key item.
  #
  # param: item - The key item to check for
  # returns: True if the player has the key item, false if not
  #
  def hasKeyItem(self, item):
    return item in self.keyItems
  #
  # Add a key item to the set of key items acquired
  #
  # param: item - The Key Item to add
  #
  def addKeyItem(self, item):
    self.keyItems.add(item)
    
  #
  # Remove a key item from the set of key items acquired
  #
  # param: item: The Key Item to remove
  #
  def removeKeyItem(self, item):
    self.keyItems.discard(item)

  #
  # Determine which characters are available based on what key items/time periods
  # are available to the player.
  #
  # The character locations are provided at object construction.  The dictionary
  # is provided as output from running the characterwriter.py script.
  #
  def updateAvailableCharacters(self):
    # charLocations is a dictionary that uses the location name as
    # a key and the character data structure as a value.
    #
    # NOTE: The first entry in the character data is the character ID.
    #       Use the ID to get the correct character from the enum.
    #
    # The first four characters are always available.
    self.addCharacter(Characters(self.charLocations['start'][0]))
    self.addCharacter(Characters(self.charLocations['start2'][0]))
    self.addCharacter(Characters(self.charLocations['cathedral'][0]))
    self.addCharacter(Characters(self.charLocations['castle'][0]))
    
    # The remaining three characters are progression gated.
    if self.canAccessFuture():
      self.addCharacter(Characters(self.charLocations['proto'][0]))
    if self.canAccessDactylCharacter():
      self.addCharacter(Characters(self.charLocations['dactyl'][0]))
    if self.hasMasamune():
      self.addCharacter(Characters(self.charLocations['burrow'][0]))
  # end updateAvailableCharacters function
    
  #
  # Logic convenience functions.  These can be used to
  # quickly check if particular eras or chests are
  # logically accessible.
  #
  def canAccessDactylCharacter(self):
    # If character locking is on, dreamstone is required to get the
    # Dactyl Nest character in addition to prehistory access.
    return (self.canAccessPrehistory() and 
           ((not self.lockedChars) or self.hasKeyItem(KeyItems.dreamstone)))
  
  def canAccessFuture(self):
    return self.hasKeyItem(KeyItems.pendant)
    
  def canAccessPrehistory(self):
    return self.hasKeyItem(KeyItems.gatekey)
    
  def canAccessTyranoLair(self):
    return self.canAccessPrehistory() and self.hasKeyItem(KeyItems.dreamstone)
    
  def hasMasamune(self):
    return (self.hasKeyItem(KeyItems.hilt) and 
            self.hasKeyItem(KeyItems.blade))
            
  def canAccessMagusCastle(self):
    return (self.hasMasamune() and 
            self.hasCharacter(Characters.Frog))
    
  def canAccessDarkAges(self):
    return ((self.canAccessTyranoLair()) or
           (self.canAccessMagusCastle()))
        
  def canAccessOceanPalace(self):
    return (self.canAccessDarkAges() and 
            self.hasKeyItem(KeyItems.rubyknife))
    
  def canAccessBlackOmen(self):
    return (self.canAccessFuture() and 
            self.hasKeyItem(KeyItems.clone) and 
            self.hasKeyItem(KeyItems.ctrigger))
  
  def canGetSunstone(self):
    return (self.canAccessFuture() and
            self.canAccessPrehistory() and
            self.hasKeyItem(KeyItems.moonstone))
  
  def canAccessKingsTrial(self):
    return (self.hasCharacter(Characters.Marle) and
            self.hasKeyItem(KeyItems.prismshard))
  
  def canAccessMelchiorsRefinements(self):
    return (self.canAccessKingsTrial() and
            self.canGetSunstone())
  
  def canAccessGiantsClaw(self):
    return self.hasKeyItem(KeyItems.tomapop)
    
  def canAccessRuins(self):
    return self.hasKeyItem(KeyItems.grandleon)
    
  def canAccessSealedChests(self):
    return (self.hasKeyItem(KeyItems.pendant) and 
           (self.earlyPendant or self.canAccessDarkAges()))
           
  def canAccessBurrowItem(self):
    return self.hasKeyItem(KeyItems.heromedal)
    
  def canAccessFionasShrine(self):
    return self.hasCharacter(Characters.Robo)
# End Game class


#
# This class represents a location within the game.
# It is the parent class for the different location types
#
class Location:
  def __init__(self, name, pointer):
    self.name = name
    self.pointer = pointer
    self.keyItem = None
    
  #
  # Get the name of this location.
  #
  # return: The name of this location
  #
  def getName(self):
    return self.name
    
  #
  # Get the pointer for this treasure location.
  #
  # return: The pointer for this treasure location
  #
  def getPointer(self):
    return self.pointer 
    
  #
  # Set the key item at this location.
  #
  # param: keyItem The key item to be placed at this location
  #
  def setKeyItem(self, keyItem):
    self.keyItem = keyItem
    
  #
  # Get the key item placed at this location.
  #
  # return: The key item being held in this location
  #
  def getKeyItem(self):
    return self.keyItem
# End Location class

#
# This Location type represents a location tied to an event.
# These are used for the sealed chests, which are not treated like normal chests.
# They have two pointers associated with them.
#
class EventLocation(Location):
  def __init__(self, name, pointer, pointer2):
    Location.__init__(self, name, pointer)
    self.pointer2 = pointer2

  #
  # Get the second pointer for this location.
  #
  def getPointer2(self):
    return self.pointer2
    
# End EventLocation class


#
# This class represents a normal check in the randomizer.
# EventLocation provides all of the pointers needed. 
# This class allows for a loot tier to be specified, that 
# will be used to assign a piece of loot to locations that
# were nor assigned a key item.
#
class BaselineLocation(EventLocation):
  def __init__(self, name, pointer, pointer2, lootTier):
    EventLocation.__init__(self, name, pointer, pointer2)
    self.lootTier = lootTier
    
  #
  # Get the loot tier associated with this check.
  #
  # return: The loot tier associated with this check
  #
  def getLootTier(self):
    return self.lootTier

# End BaselineLocation class


#
# This class represents a group of locations controlled by 
# the same access rule.
#
class LocationGroup:
  #
  # Constructor for a LocationGroup.
  #
  # param: name - The name of this LocationGroup
  # param: weight - The initial weighting factor of this LocationGroup
  # param: accessRule - A function used to determine if this LocationGroup is accessible
  # param: weightDecay - Optional function to define weight decay of this LocationGroup
  #
  def __init__(self, name, weight, accessRule, weightDecay = None):
    self.name = name
    self.locations = []
    self.weight = weight
    self.accessRule = accessRule
    self.weightDecay = weightDecay
    self.weightStack = []
    
    
  #
  # Return whether or not this location group is accessible.
  #
  # param: game - The game object with current game state
  # return: True if this location is accessible, false if not
  #
  def canAccess(self, game):
    return self.accessRule(game)
    
  #
  # Get the name of this location.
  #
  # return: The name of this location
  #
  def getName(self):
    return self.name
    
  #
  # Get the weight value being used to select locations from this group.
  #
  # return: Weight value used by this location group
  #
  def getWeight(self):
    return self.weight
    
  #
  # Set the weight used when selecting locations from this group.
  # The weight cannot be set less than 1.
  #
  # param: weight - Weight value to set
  #
  def setWeight(self, weight):
    if weight < 1:
      weight = 1
    self.weight = weight
  
  #
  # This function is used to decay the weight value of this 
  # LocationGroup when a location is chosen from it.
  #
  def decayWeight(self):
    self.weightStack.append(self.weight)
    if self.weightDecay == None:
      # If no weight decay function was given, reduce the weight of this
      # LocationGroup to 1 to make it unlikelyto get any other items.
      self.setWeight(1)
    else:
      self.setWeight(self.weightDecay(self.weight))
  
  #
  # Undo a previous weight decay of this LocationGroup.
  # The previous weight values are stored in the weightStack.
  #
  def undoWeightDecay(self):
    if len(self.weightStack) > 0:
      self.setWeight(self.weightStack.pop())
  
  #
  # Get the number of available locations in this group.
  #
  # return: The number of locations in this group
  #
  def getAvailableLocationCount(self):
    return len(self.locations)
  
  #
  # Add a location to this location group. If the location is 
  # already part of this location group then nothing happens.
  #
  # param: location - A location object to add to this location group
  #
  def addLocation(self, location):
    if not location in self.locations:
      self.locations.append(location)
    return self
  
  #
  # Remove a location from this group.
  #
  # param: location - Location to remove from this group
  #
  def removeLocation(self, location):
    self.locations.remove(location)
  
  #
  # Get a list of all locations that are part of this location group.
  #
  # return: List of locations associated with this location group
  #
  def getLocations(self):
    return self.locations.copy()
# End LocationGroup class


#
# Initialize all of the location groups.
#
def initLocationGroups():
  
  # Clear out the locationGroups list and repopulate it.
  global locationGroups
  locationGroups = []

  # Dark Ages 
  # Mount Woe does not go away in the randomizer, so it
  # is being considered for key item drops.
  darkagesLocations = \
      LocationGroup("Darkages", 30, lambda game:game.canAccessDarkAges())
  (darkagesLocations
      .addLocation(Location("Mt Woe 1st Screen",0x35F770))
      .addLocation(Location("Mt Woe 2nd Screen 1",0x35F748))
      .addLocation(Location("Mt Woe 2nd Screen 2",0x35F74C))
      .addLocation(Location("Mt Woe 2nd Screen 3",0x35F750))
      .addLocation(Location("Mt Woe 2nd Screen 4",0x35F754))
      .addLocation(Location("Mt Woe 2nd Screen 5",0x35F758))
      .addLocation(Location("Mt Woe 3rd Screen 1",0x35F75C))
      .addLocation(Location("Mt Woe 3rd Screen 2",0x35F760))
      .addLocation(Location("Mt Woe 3rd Screen 3",0x35F764))
      .addLocation(Location("Mt Woe 3rd Screen 4",0x35F768))
      .addLocation(Location("Mt Woe 3rd Screen 5",0x35F76C))
      .addLocation(Location("Mt Woe Final 1",0x35F774))
      .addLocation(Location("Mt Woe Final 2",0x35F778))
      .addLocation(BaselineLocation("Mount Woe", 0x381010, 0x381013, LootTiers.High))
  )

  # Fiona Shrine (Key Item only)
  fionaShrineLocations = \
      LocationGroup("Fionashrine", 2, lambda game:game.canAccessFionasShrine())
  (fionaShrineLocations
      .addLocation(BaselineLocation("Fiona's Shrine", 0x6EF5E, 0x6EF61, LootTiers.MidHigh))
  )

  # Future
  futureOpenLocations = \
      LocationGroup("FutureOpen", 20, lambda game:game.canAccessFuture())
  (futureOpenLocations
      # Chests
      .addLocation(Location("Arris Dome",0x35F5C8))
      .addLocation(Location("Arris Dome Food Store",0x35F744))
      # KeyItems    
      .addLocation(BaselineLocation("Arris Dome Doan", 0x392F4C, 0x392F4E, LootTiers.MidHigh))
      .addLocation(BaselineLocation("Sun Palace", 0x1B8D95, 0x1B8D97, LootTiers.MidHigh))
  )
  
  futureSewersLocations = \
      LocationGroup("FutureSewers", 9, lambda game:game.canAccessFuture())
  (futureSewersLocations
      .addLocation(Location("Sewers 1",0x35F614))     
      .addLocation(Location("Sewers 2",0x35F618))
      .addLocation(Location("Sewers 3",0x35F61C))
  )
  
  futureLabLocations = \
      LocationGroup("FutureLabs", 15, lambda game:game.canAccessFuture())
  (futureLabLocations
      .addLocation(Location("Lab 16 1",0x35F5B8))
      .addLocation(Location("Lab 16 2",0x35F5BC))
      .addLocation(Location("Lab 16 3",0x35F5C0))
      .addLocation(Location("Lab 16 4",0x35F5C4))
      .addLocation(Location("Lab 32 1",0x35F5E0))
      # 1000AD, opened after trial - putting it here to dilute the lab pool a bit
      .addLocation(Location("Prison Tower",0x35F7DC)) 
      # Race log chest is not included.      
      #.addLocation(Location("Lab 32 2",0x35F5E4))
  )
  
  genoDomeLocations = \
      LocationGroup("GenoDome", 33, lambda game:game.canAccessFuture())
  (genoDomeLocations
      .addLocation(Location("Geno Dome 1st Floor 1",0x35F630))
      .addLocation(Location("Geno Dome 1st Floor 2",0x35F634))
      .addLocation(Location("Geno Dome 1st Floor 3",0x35F638))
      .addLocation(Location("Geno Dome 1st Floor 4",0x35F63C))
      .addLocation(Location("Geno Dome Room 1",0x35F640))
      .addLocation(Location("Geno Dome Room 2",0x35F644))
      .addLocation(Location("Proto 4 Chamber 1",0x35F648))
      .addLocation(Location("Proto 4 Chamber 2",0x35F64C))
      .addLocation(Location("Geno Dome 2nd Floor 1",0x35F668))
      .addLocation(Location("Geno Dome 2nd Floor 2",0x35F66C))
      .addLocation(Location("Geno Dome 2nd Floor 3",0x35F670))
      .addLocation(Location("Geno Dome 2nd Floor 4",0x35F674))
      .addLocation(BaselineLocation("Geno Dome Mother Brain", 0x1B1844, 0x1B1846, LootTiers.MidHigh))
  )
  
  factoryLocations = \
      LocationGroup("Factory", 30, lambda game:game.canAccessFuture())
  (factoryLocations
      .addLocation(Location("Factory Ruins Left - Auxillary Console",0x35F5E8))
      .addLocation(Location("Factory Ruins Left - Security Center (Right)",0x35F5EC))
      .addLocation(Location("Factory Ruins Left - Security Center (Left)",0x35F5F0))
      .addLocation(Location("Factory Ruins Left - Power Core",0x35F610))
      .addLocation(Location("Factory Ruins Right - Data Core 1",0x35F650))
      .addLocation(Location("Factory Ruins Left - Data Core 2",0x35F654))
      .addLocation(Location("Factory Ruins Right - Factory Floor (Top)",0x35F5F4))
      .addLocation(Location("Factory Ruins Right - Factory Floor (Left)",0x35F5F8))
      .addLocation(Location("Factory Ruins Right - Factory Floor (Bottom)",0x35F5FC))
      .addLocation(Location("Factory Ruins Right - Factory Floor (Secret)",0x35F600))
      .addLocation(Location("Factory Ruins Right - Crane Control Room (lower)",0x35F604))
      .addLocation(Location("Factory Ruins Right - Crane Control Room (upper)",0x35F608))
      .addLocation(Location("Factory Ruins Right - Information Archive",0x35F60C))
      #.addLocation(Location("Factory Ruins Right - Robot Storage",0x35F7A0)) # Inaccessible chest
  )

  # GiantsClawLocations
  giantsClawLocations = \
      LocationGroup("Giantsclaw", 30, lambda game:game.canAccessGiantsClaw())
  (giantsClawLocations
      .addLocation(Location("Giant's Claw Kino's Cell",0x35F468))
      .addLocation(Location("Giant's Claw Traps",0x35F46C))
      .addLocation(Location("Giant's Claw Caves 1",0x35F56C))
      .addLocation(Location("Giant's Claw Caves 2",0x35F570))
      .addLocation(Location("Giant's Claw Caves 3",0x35F574))
      .addLocation(Location("Giant's Claw Caves 4",0x35F578))
      .addLocation(Location("Giant's Claw Caves 5",0x35F57C))
      .addLocation(Location("Giant's Claw Caves 6",0x35F580))
      .addLocation(BaselineLocation("Giant's Claw", 0x1B8AEC, 0x1B8AEF, LootTiers.Mid)) #key item
  )

  # Northern Ruins
  northernRuinsLocations = \
      LocationGroup("NorthernRuins", 25, \
          lambda game:(game.canAccessRuins() and game.canAccessSealedChests()))
  (northernRuinsLocations
      # Sealed chests in Northern Ruins
      .addLocation(EventLocation("Hero's Grave 1",0x1B03CD,0x1B03D0))
      .addLocation(EventLocation("Hero's Grave 2",0x1B0401,0x1B0404))
      .addLocation(EventLocation("Hero's Grave 3",0x393F8,0x393FF))
  )

  # Guardia Treasury
  guardiaTreasuryLocations = \
      LocationGroup("GuardiaTreasury", 36, lambda game:game.canAccessKingsTrial())
  (guardiaTreasuryLocations
      .addLocation(Location("Guardia Basement 1", 0x35F41C))
      .addLocation(Location("Guardia Basement 2", 0x35F420))
      .addLocation(Location("Guardia Basement 3", 0x35F424))
      .addLocation(Location("Guardia Treasury 1", 0x35F7A4))
      .addLocation(Location("Guardia Treasury 2", 0x35F7A8))
      .addLocation(Location("Guardia Treasury 3", 0x35F7AC))
      .addLocation(BaselineLocation("King's Trial", 0x38045D, 0x38045F, LootTiers.High))
  )
  
  # Ozzie's Fort locations
  # Ozzie's fort is a high level location.  For the first four chests, don't
  # consider these locations until the player has either the pendant or gate key.
  # The final two chests are locked behind the trio battle.  Only consider these if
  # the player has access to the Dark Ages.
  earlyOzziesFortLocations = \
      LocationGroup("Ozzie's Fort Front", 6, \
          lambda game: (game.canAccessFuture() or game.canAccessPrehistory()))
  (earlyOzziesFortLocations
      .addLocation(Location("Ozzie's Fort Guillotines 1",0x35F554))
      .addLocation(Location("Ozzie's Fort Guillotines 2",0x35F558))
      .addLocation(Location("Ozzie's Fort Guillotines 3",0x35F55C))
      .addLocation(Location("Ozzie's Fort Guillotines 4",0x35F560))
  )
  
  lateOzziesFortLocations = \
      LocationGroup("Ozzie's Fort Back", 6, lambda game: game.canAccessDarkAges())
  (lateOzziesFortLocations
      .addLocation(Location("Ozzie's Fort Final 1",0x35F564))
      .addLocation(Location("Ozzie's Fort Final 2",0x35F568))
  )

  # Open locations always available with no access requirements
  # Open locations are split into multiple groups so that weighting
  # can be applied separately to individual areas.
  openLocations = LocationGroup("Open", 10, \
       lambda game: True, \
       lambda weight:int(weight * 0.2))
  (openLocations
      .addLocation(Location("Truce Mayor's House F1",0x35F40C))
      .addLocation(Location("Truce Mayor's House F2",0x35F410))
      .addLocation(Location("Forest Ruins",0x35F42C))
      .addLocation(Location("Porre Mayor's House F2",0x35F440))
      .addLocation(Location("Truce Canyon 1",0x35F470))
      .addLocation(Location("Truce Canyon 2",0x35F474))
      .addLocation(Location("Fiona's House 1",0x35F4FC))
      .addLocation(Location("Fiona's House 2",0x35F500))
      .addLocation(Location("Cursed Woods 1",0x35F4A4))
      .addLocation(Location("Cursed Woods 2",0x35F4A8))
      .addLocation(Location("Frog's Burrow Right Chest",0x35F4AC))
  )
  
  openKeys = LocationGroup("OpenKeys", 5, lambda game: True)
  (openKeys
      .addLocation(BaselineLocation("Zenan Bridge", 0x393C82, 0x393C84, LootTiers.Mid))
      .addLocation(BaselineLocation("Snail Stop", 0x380C42, 0x380C5B, LootTiers.Mid))
      .addLocation(BaselineLocation("Lazy Carpenter", 0x3966B, 0x3966D, LootTiers.Mid))
  )
  
  heckranLocations = \
      LocationGroup("Heckran", 4, lambda game: True)
  (heckranLocations
      .addLocation(Location("Heckran Cave Sidetrack",0x35F430))
      .addLocation(Location("Heckran Cave Entrance",0x35F434))
      .addLocation(Location("Heckran Cave 1",0x35F438))
      .addLocation(Location("Heckran Cave 2",0x35F43C))
      .addLocation(BaselineLocation("Taban", 0x35F888, 0x35F88A, LootTiers.Mid))
  )
  
  guardiaCastleLocations = \
      LocationGroup("GuardiaCastle", 3, lambda game: True)
  (guardiaCastleLocations
      .addLocation(Location("King's Room (Present)",0x35F414))
      .addLocation(Location("Queen's Room (Present)",0x35F418))
      .addLocation(Location("King's Room(Middle Ages)",0x35F478))
      .addLocation(Location("Queen's Room(Middle Ages)",0x35F47C))
      .addLocation(Location("Royal Kitchen",0x35F480))
      .addLocation(Location("Queen's Tower(Middle Ages)",0x35F7B0))
      .addLocation(Location("King's Tower(Middle Ages)",0x35F7CC))
      .addLocation(Location("King's Tower(Present)",0x35F7D0))
      .addLocation(Location("Queen's Tower(Present)",0x35F7D4))
      .addLocation(Location("Guardia Court Tower",0x35F7D8))
  )
  
  cathedralLocations = \
      LocationGroup("CathedralLocations", 6, lambda game: True)
  (cathedralLocations
      .addLocation(Location("Manoria Cathedral 1",0x35F488))
      .addLocation(Location("Manoria Cathedral 2",0x35F48C))
      .addLocation(Location("Manoria Cathedral 3",0x35F490))
      .addLocation(Location("Cathedral Interior 1",0x35F494))
      .addLocation(Location("Cathedral Interior 2",0x35F498))
      .addLocation(Location("Cathedral Interior 3",0x35F49C))
      .addLocation(Location("Cathedral Interior 4",0x35F4A0))
      .addLocation(Location("Manoria Shrine Sideroom 1",0x35F588))
      .addLocation(Location("Manoria Shrine Sideroom 2",0x35F58C))
      .addLocation(Location("Manoria Bromide Room 1",0x35F590))
      .addLocation(Location("Manoria Bromide Room 2",0x35F594))
      .addLocation(Location("Manoria Bromide Room 3",0x35F598))
      .addLocation(Location("Manoria Magus Shrine 1",0x35F59C))
      .addLocation(Location("Manoria Magus Shrine 2",0x35F5A0))
      .addLocation(Location("Yakra's Room",0x35F584))
  )
  
  denadoroLocations = \
      LocationGroup("DenadoroLocations", 6, lambda game:True)
  (denadoroLocations
      .addLocation(Location("Denadoro Mts Screen 2 1",0x35F4B0))
      .addLocation(Location("Denadoro Mts Screen 2 2",0x35F4B4))
      .addLocation(Location("Denadoro Mts Screen 2 3",0x35F4B8))
      .addLocation(Location("Denadoro Mts Final 1",0x35F4BC))
      .addLocation(Location("Denadoro Mts Final 2",0x35F4C0))     
      .addLocation(Location("Denadoro Mts Final 3",0x35F4C4))     
      .addLocation(Location("Denadoro Mts Waterfall Top 1",0x35F4C8))     
      .addLocation(Location("Denadoro Mts Waterfall Top 2",0x35F4CC))     
      .addLocation(Location("Denadoro Mts Waterfall Top 3",0x35F4D0))     
      .addLocation(Location("Denadoro Mts Waterfall Top 4",0x35F4D4))     
      .addLocation(Location("Denadoro Mts Waterfall Top 5",0x35F4D8))     
      .addLocation(Location("Denadoro Mts Entrance 1",0x35F4DC))      
      .addLocation(Location("Denadoro Mts Entrance 2",0x35F4E0))      
      .addLocation(Location("Denadoro Mts Screen 3 1",0x35F4E4))      
      .addLocation(Location("Denadoro Mts Screen 3 2",0x35F4E8))      
      .addLocation(Location("Denadoro Mts Screen 3 3",0x35F4EC))      
      .addLocation(Location("Denadoro Mts Screen 3 4",0x35F4F0))      
      .addLocation(Location("Denadoro Mts Ambush",0x35F4F4))      
      .addLocation(Location("Denadoro Mts Save Point",0x35F4F8))
      .addLocation(BaselineLocation("Denadoro Mountain", 0x3773F1, 0x3773F3, LootTiers.Mid))
  )
      
  # Sealed locations
  sealedLocations = \
      LocationGroup("SealedLocations", 30, 
          lambda game:game.canAccessSealedChests(),
          lambda weight:int(weight * 0.3))
  (sealedLocations
      # Sealed Doors
      .addLocation(Location("Bangor Dome Seal 1", 0x35F5A4))
      .addLocation(Location("Bangor Dome Seal 2", 0x35F5A8))
      .addLocation(Location("Bangor Dome Seal 3", 0x35F5AC))
      .addLocation(Location("Trann Dome Seal 1", 0x35F5B0))
      .addLocation(Location("Trann Dome Seal 2", 0x35F5B4))
      .addLocation(Location("Arris Dome Seal 1", 0x35F5CC))
      .addLocation(Location("Arris Dome Seal 2", 0x35F5D0))
      .addLocation(Location("Arris Dome Seal 3", 0x35F5D4))
      .addLocation(Location("Arris Dome Seal 4", 0x35F5D8))
      # Sealed chests
      .addLocation(EventLocation("Truce Inn 600AD Sealed",0x19FE7C,0x19FE83))     
      .addLocation(EventLocation("Porre Elder's House 1 Sealed",0x1B90EA,0x1B90F2))     
      .addLocation(EventLocation("Porre Elder's House 2Sealed",0x1B9123,0x1B9126))     
      .addLocation(EventLocation("Guardia Castle 600AD Sealed",0x3AED24,0x3AED26))  
      .addLocation(EventLocation("Guardia Forest 600AD Sealed",0x39633B,0x39633D))      
      .addLocation(EventLocation("Truce Inn 1000AD Sealed",0xC3328,0xC332C))           
      .addLocation(EventLocation("Porre Mayor's House Sealed 1",0x1BACD6,0x1BACD8))     
      .addLocation(EventLocation("Porre Mayor's House Sealed 2",0x1BACF7,0x1BACF9))     
      .addLocation(EventLocation("Guardia Forest 1000AD Sealed",0x3908B5,0x3908C9))     
      .addLocation(EventLocation("Guardia Castle 1000AD Sealed",0x3AEF65,0x3AEF67))     
      .addLocation(EventLocation("Heckran's Cave Sealed 1",0x24EC29,0x24EC2B))      
      .addLocation(EventLocation("Heckran's Cave Sealed 2",0x24EC3B,0x24EC3D))
      # These are the sealed chests in the blue pyramid.  
      # Not included since you can only get one of the two.
      #.addLocation(EventLocation("Forest Ruins 1",0x1BAB33,0x1BAB35))      
      #.addLocation(EventLocation("Forest Ruins 2",0x1BAB62,0x1BAB64)) 
  )
  
  # Sealed chest in the magic cave.
  # Requires both powered up pendant and Magus' Castle access
  magicCaveLocations = \
      LocationGroup("Magic Cave", 4, \
          lambda game: game.canAccessSealedChests() and game.canAccessMagusCastle())
  (magicCaveLocations
      .addLocation(EventLocation("Magic Cave",0x1B31C7,0x1B31CA))
  )
  
  # Prehistory
  prehistoryForestMazeLocations = \
      LocationGroup("PrehistoryForestMaze", 18, lambda game:game.canAccessPrehistory())
  (prehistoryForestMazeLocations
      .addLocation(Location("Mystic Mtn Stream",0x35F678))
      .addLocation(Location("Forest Maze 1",0x35F67C))
      .addLocation(Location("Forest Maze 2",0x35F680))
      .addLocation(Location("Forest Maze 3",0x35F684))
      .addLocation(Location("Forest Maze 4",0x35F688))
      .addLocation(Location("Forest Maze 5",0x35F68C))
      .addLocation(Location("Forest Maze 6",0x35F690))
      .addLocation(Location("Forest Maze 7",0x35F694))
      .addLocation(Location("Forest Maze 8",0x35F698))
      .addLocation(Location("Forest Maze 9",0x35F69C))
  )
  
  prehistoryReptiteLocations = \
      LocationGroup("PrehistoryReptite", 27, lambda game:game.canAccessPrehistory())
  (prehistoryReptiteLocations
      .addLocation(Location("Reptite Lair Reptites 1",0x35F6B8))
      .addLocation(Location("Reptite Lair Reptites 2",0x35F6BC))
      .addLocation(BaselineLocation("Reptite Lair", 0x18FC04, 0x18FC07, LootTiers.MidHigh)) #Reptite Lair Key Item
  )
  
  # Dactyl Nest already has a character, so give it a relatively low weight compared
  # to the other prehistory locations.
  prehistoryDactylNest = \
      LocationGroup("PrehistoryDactylNest", 6, lambda game:game.canAccessPrehistory())
  (prehistoryDactylNest
      .addLocation(Location("Dactyl Nest 1",0x35F6C0))
      .addLocation(Location("Dactyl Nest 2",0x35F6C4))
      .addLocation(Location("Dactyl Nest 3",0x35F6C8)) 
  )

  # MelchiorRefinements
  melchiorsRefinementslocations = \
      LocationGroup("MelchiorRefinements", 15, lambda game:game.canAccessMelchiorsRefinements())
  (melchiorsRefinementslocations
      .addLocation(BaselineLocation("Melchior's Refinements", 0x3805DE, 0x3805E0, LootTiers.High))
  )

  # Frog's Burrow
  frogsBurrowLocation = \
      LocationGroup("FrogsBurrowLocation", 9, lambda game:game.canAccessBurrowItem())
  (frogsBurrowLocation
      .addLocation(BaselineLocation("Frog's Burrow Left Chest", 0x3891DE, 0x3891E0, LootTiers.MidHigh))
  )
  
  # Prehistory
  locationGroups.append(prehistoryForestMazeLocations)
  locationGroups.append(prehistoryReptiteLocations)
  locationGroups.append(prehistoryDactylNest)
  
  # Dark Ages
  locationGroups.append(darkagesLocations)
  
  # 600/1000AD
  locationGroups.append(fionaShrineLocations)
  locationGroups.append(giantsClawLocations)
  locationGroups.append(northernRuinsLocations)
  locationGroups.append(guardiaTreasuryLocations)
  locationGroups.append(openLocations)
  locationGroups.append(openKeys)
  locationGroups.append(heckranLocations)
  locationGroups.append(cathedralLocations)
  locationGroups.append(guardiaCastleLocations)
  locationGroups.append(denadoroLocations)
  locationGroups.append(magicCaveLocations)
  locationGroups.append(melchiorsRefinementslocations)
  locationGroups.append(frogsBurrowLocation)
  locationGroups.append(earlyOzziesFortLocations)
  locationGroups.append(lateOzziesFortLocations)
  
  # Future
  locationGroups.append(futureOpenLocations)
  locationGroups.append(futureLabLocations)
  locationGroups.append(futureSewersLocations)
  locationGroups.append(genoDomeLocations)
  locationGroups.append(factoryLocations)
  
  # Sealed Locations (chests and doors)
  locationGroups.append(sealedLocations)
  
# end initLocationGroups function

#
# Get a list of location groups that are available for key item placement.
#
# param: game - Game object used to determine location access
#
# return: List of all available locations
#
def getAvailableLocations(game):
  # Have the game object update what characters are available based on the
  # currently available items and time periods.
  game.updateAvailableCharacters()
  
  # Get a list of all accessible location groups
  accessibleLocationGroups = []
  for locationGroup in locationGroups:
    if locationGroup.canAccess(game):
      if locationGroup.getAvailableLocationCount() > 0:
        accessibleLocationGroups.append(locationGroup)
  
  return accessibleLocationGroups
  
# end getAvailableLocations

#
# Get the initial set of available key items.
#
# return: Full list of the game's key items
#
def getInitialKeyItems():
  # NOTE:
  # The initial list of key items contains multiples of most of the key items, and
  # not in equal number.  The pendant and gate key are more heavily weighted
  # so that they appear earlier in the run, opening up more potential checks.
  # The ruby knife, dreamstone, clone, and trigger only appear once to reduce
  # the frequency of extremely early go mode from open checks.
  # The hilt and blade show up 3 times each, also to reduce early go mode through
  # Magus' Castle to a reasonable number.
  
  # Seed the list with 5 copies of each item
  keyItemList = [key for key in (KeyItems)]
  keyItemList.extend([key for key in (KeyItems)])
  keyItemList.extend([key for key in (KeyItems)])
  keyItemList.extend([key for key in (KeyItems)])
  keyItemList.extend([key for key in (KeyItems)])
  
  # remove all but 1 copy of the dreamstone/ruby knife/clone/trigger
  keyItemList[:] = [x for x in keyItemList if x != KeyItems.rubyknife]
  keyItemList[:] = [x for x in keyItemList if x != KeyItems.dreamstone]
  keyItemList[:] = [x for x in keyItemList if x != KeyItems.clone]
  keyItemList[:] = [x for x in keyItemList if x != KeyItems.ctrigger]
  keyItemList.extend([KeyItems.rubyknife, KeyItems.dreamstone, 
                      KeyItems.clone, KeyItems.ctrigger])
  
  # remove all but 3 copies of the hilt/blade
  keyItemList.remove(KeyItems.hilt)
  keyItemList.remove(KeyItems.hilt)
  keyItemList.remove(KeyItems.blade)
  keyItemList.remove(KeyItems.blade)
  
  # Add additional copies of the pendant and gate key
  keyItemList.extend([KeyItems.gatekey, KeyItems.gatekey, KeyItems.gatekey, 
                      KeyItems.pendant, KeyItems.pendant, KeyItems.pendant])
                      
  return keyItemList
# end getInitialKeyItems


#
# Randomly place key items.
#
# param: charlocs - Dictionary of characer locations
# param: lockedChars - Whether or not the locked chars flag is being used
# param: earlyPendant - Whether or not the eary pendant charge flag is being used
#
def determineKeyItemPlacement(charlocs, lockedChars, earlyPendant):
  initLocationGroups()
  game = Game(charlocs)
  game.setEarlyPendant(earlyPendant)
  game.setLockedCharacters(lockedChars)
  chosenLocations = []
  remainingKeyItems = getInitialKeyItems()
  return determineKeyItemPlacement_impl(chosenLocations, remainingKeyItems, game)
# end place_key_items


#
# NOTE: Do not call this function directly. This will be called 
#       by placeKeyItems after setting up the parameters
#       needed by this function.
#
# This function will recursively determine key item locations
# such that a seed can be 100% completed.  This uses a weighted random
# approach to placement and will only consider logically accessible locations.
#
# The algorithm for determining locations is:
#   Each location group has an assigned weight.
#   When selecting a location, get a list of all accessible locations and add up their weights.
#   pick a random number from 1 to the combined weight
#   Select the location group corresponding to that number
#   Pick a location randomly from within that group
#   Lower the weight of the selected group to reduce the chance of it being picked again
#
#
# param: chosenLocations - List of locations already chosen for key items
# param: remainingKeyItems - List of key items remaining to be placed
# param: game - Game object used to determine logic
#
# return: A tuple containing:
#             A Boolean indicating whether or not key item placement was successful
#             A list of locations with key items assigned
#
def determineKeyItemPlacement_impl(chosenLocations, remainingKeyItems, game):
  if len(remainingKeyItems) == 0:
    # We've placed all key items.  This is our breakout condition
    return True, chosenLocations
  else:
    # We still have key items to place.
    availableLocations = getAvailableLocations(game)
    if len(availableLocations) == 0:
      # This item configuration is not completable. 
      return False, chosenLocations
    else:
      # Continue placing key items.
      keyItemConfirmed = False
      returnedChosenLocations = None
      location = None
      keyItem = None
      locationGroup = None
      keyItemTemp = None
      while True:
        if keyItemConfirmed:
          # We're unwinding the recursion here, all key items are placed.
          return keyItemConfirmed, returnedChosenLocations
        else:
          # Keep trying key item placement
          # select a location randomly from the list
          if locationGroup != None:
            locationGroup.addLocation(location)
            locationGroup.undoWeightDecay()
            
          # get the max rand value from the combined weightings of the location groups
          # This will be used to help select a location group
          weightTotal = 0
          for group in availableLocations:
            weightTotal = weightTotal + group.getWeight()
          
          # Select a location group
          locationChoice = rand.randint(1, weightTotal)
          counter = 0
          for group in availableLocations:
            counter = counter + group.getWeight()
            if counter >= locationChoice:
              locationGroup = group
              break
            
          # Select a random location from the chosen location group.
          # Reduce the weighting on that location group to lower the chance
          # that it will be selected again.
          location = rand.choice(group.getLocations())
          group.removeLocation(location)
          group.decayWeight()
          chosenLocations.append(location)
          
          # If 2/3 of the key items have been placed
          # then remove the key item bias from the remaining list.
          # This is to slightly reduce the occurrence of the lowest weighted
          # items from showing up dispraportionately on extremely late checks
          # like Mount Woe or the Guardia Treasury.
          if game.getKeyItemCount() == 10:
            newList = []
            for key in remainingKeyItems:
              if not key in newList:
                newList.append(key)
            remainingKeyItems = newList
          
          # select a key item for this location
          keyItem = rand.choice(remainingKeyItems)
          # Remove all copies of the key item from the list
          remainingKeyItems[:] = [x for x in remainingKeyItems if x != keyItem]
          location.setKeyItem(keyItem)
          game.addKeyItem(keyItem)
          
          # If this isn't the first time through the loop, choose a new item and 
          # undo the previous item selection
          if keyItemTemp != None:
            remainingKeyItems.append(keyItemTemp)
            game.removeKeyItem(keyItemTemp)
          keyItemTemp = keyItem
          # recurse and try to place the next key item.
          keyItemConfirmed, returnedChosenLocations = \
              determineKeyItemPlacement_impl(chosenLocations, remainingKeyItems, game)

              
# end determineKeyItemPlacement_impl recursive function

#
# Write out the spoiler log.
#
# param: chosenLocations - List of locations containing key items
# param: charLocations - Dictionary of locations to characters
#
def writeSpoilerLog(chosenLocations, charLocations):
  spoilerLog = open("spoiler_log.txt","w+")
  # Write the key item location to the spoiler log
  
  spoilerLog.write("Key ItemLocations:\n")
  for location in chosenLocations:
    spoilerLog.write("  " + location.getName() + ": " + location.getKeyItem().name + "\n")
  
  # Write the character locations to the spoiler log
  spoilerLog.write("\n\nCharacter Locations:\n")
  for loc, char in charLocations.items():
    character = Characters(char[0])
    spoilerLog.write("  " + loc + ": " + character.name + "\n")
  spoilerLog.close()


#
# Get a random treasure for a baseline location.
# This function uses the loog selection algorithm from treasures.py.
# Loot tiers are set as part of the location construction.
#
# param: location - BaselineLocation that needs loot 
#
# return: The item code for a random treasure
#
def getRandomTreasure(location):
  treasureCode = 0;
  
  lootTier = location.getLootTier()
  # loot selection algorithm stolen from treasurewriter.py
  rand_num = rand.randrange(0,11,1)
  # Mid tier loot - early checks
  if lootTier == LootTiers.Mid:
    if rand_num > 5:
      treasureCode = rand.choice(treasure.plvlconsumables + \
                                 treasure.mlvlconsumables)
    else:
      rand_num = rand.randrange(0,100,1)
      if rand_num > 74:
        if rand_num > 94:
          treasureCode = rand.choice(treasure.hlvlitems)
        else:
          treasureCode = rand.choice(treasure.glvlitems)
      else:
        treasureCode = rand.choice(treasure.mlvlitems)
        
  # Mid-high tier loot - moderately gated or more difficult checks
  elif lootTier == LootTiers.MidHigh:
    if rand_num > 5:
      treasureCode = rand.choice(treasure.mlvlconsumables + \
                                 treasure.glvlconsumables)
    else:
      rand_num = rand.randrange(0,100,1)
      if rand_num > 74:
        if rand_num > 94:
          treasureCode = rand.choice(treasure.alvlitems)
        else:
          treasureCode = rand.choice(treasure.hlvlitems)
      else:
        treasureCode = rand.choice(treasure.glvlitems)
  
  # High tier loot - Late or difficult checks
  elif lootTier == LootTiers.High:
    if rand_num > 6:
      treasureCode = rand.choice(treasure.glvlconsumables + \
                                 treasure.hlvlconsumables + \
                                 treasure.alvlconsumables)
    else:
      rand_num = rand.randrange(0,100,1)
      if rand_num > 74:
        treasureCode = rand.choice(treasure.alvlitems)
      else:
        treasureCode = rand.choice(treasure.glvlitems + \
                                   treasure.hlvlitems)
                                
  return treasureCode
# end getRandomTreasure function
    
  
  
#
# Determine key item placements and write them to the provided ROM file.
# Additionally, a spoiler log is written that lists where the key items and
# characters were placed.
#
# param: outFile - File name of the output ROM
# param: charLocations - Dictionary of character locations from characterwriter.py
# param: lockedChars - Whether or not the locked characters flag is selected
# param: earlyPendant - Whether or not the early pendant charge flag is selected
#
def writeKeyItems(outFile, charLocations, lockedChars, earlyPendant):
  # Determine placements for the key items
  success, chosenLocations = determineKeyItemPlacement(charLocations, lockedChars, earlyPendant)
  
  if not success:
    print("Unable to place key items.")
    return
  
  # Write key items to their locations in the ROM.
  romFile = open(outFile, "r+b")
  for location in chosenLocations:
    romFile.seek(location.getPointer())
    romFile.write(st.pack("B", location.getKeyItem().value))
    
    # Baseline locations have a second pointer
    if type(location) == EventLocation or type(location) == BaselineLocation:
      romFile.seek(location.getPointer2())
      romFile.write(st.pack("B", location.getKeyItem().value))
  
  # Go through any baseline locations not assigned an item and place a 
  # piece of treasure. Treasure quality is based on the location's loot tier.
  for locationGroup in locationGroups:
    for location in locationGroup.getLocations():
      if type(location) == BaselineLocation and (not location in chosenLocations):
        # This is a baseline location without a key item.  
        # Assign a piece of treasure.
        treasureCode = getRandomTreasure(location)
        romFile.seek(location.getPointer())
        romFile.write(st.pack("B", treasureCode))
        romFile.seek(location.getPointer2())
        romFile.write(st.pack("B", treasureCode))
  
  romFile.close()
  
  writeSpoilerLog(chosenLocations, charLocations)
  
# End writeKeyItems function

