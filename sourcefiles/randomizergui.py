# python standard libraries
import os
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox


# custom/local libraries
import randomizer

#
# Data storage class to hold GUI selection data
#
class DataStore:
  def __init__(self):
    self.flags = {}
    self.difficulty = None
    self.inputFile = None
    self.outputFile = None
    self.techRando = None

datastore = DataStore()
progressBar = None
optionsFrame = None

#
# tkinter does not have a native tooltip implementation.
# This tooltip implementation is stolen from Stack Overflow:
# https://stackoverflow.com/a/36221216
#
class CreateToolTip(object):
  """
  create a tooltip for a given widget
  """
  def __init__(self, widget, text='widget info'):
    self.waittime = 800     #miliseconds
    self.wraplength = 300   #pixels
    self.widget = widget
    self.text = text
    self.widget.bind("<Enter>", self.enter)
    self.widget.bind("<Leave>", self.leave)
    self.widget.bind("<ButtonPress>", self.leave)
    self.id = None
    self.tw = None

  def enter(self, event=None):
    self.schedule()

  def leave(self, event=None):
    self.unschedule()
    self.hidetip()

  def schedule(self):
    self.unschedule()
    self.id = self.widget.after(self.waittime, self.showtip)

  def unschedule(self):
    id = self.id
    self.id = None
    if id:
      self.widget.after_cancel(id)

  def showtip(self, event=None):
    x = y = 0
    x, y, cx, cy = self.widget.bbox("insert")
    x += self.widget.winfo_rootx() + 25
    y += self.widget.winfo_rooty() + 20
    # creates a toplevel window
    self.tw = tk.Toplevel(self.widget)
    # Leaves only the label and removes the app window
    self.tw.wm_overrideredirect(True)
    self.tw.wm_geometry("+%d+%d" % (x, y))
    label = tk.Label(self.tw, text=self.text, justify='left',
                 background="#ffffff", relief='solid', borderwidth=1,
                 wraplength = self.wraplength)
    label.pack(ipadx=1)

  def hidetip(self):
    tw = self.tw
    self.tw= None
    if tw:
      tw.destroy()
# end class CreateToolTip

#
# Generate thread target function, calls out to the randomizer to
# generate a seed with the datastore values and stops the progress
# bar when the seed is ready.
#
def randomize():
  try:
    randomizer.handle_gui(datastore)
    progressBar.stop()
    tk.messagebox.showinfo("Randomization Complete", "Randomization complete. Seed: " + datastore.seed.get())
  except WindowsError:
    tk.messagebox.showinfo("Invalid File Name", f"Try placing the ROM in the same folder as the program. \n Also, try writing the extension(.sfc/smc).")
    progressBar.stop()

genThread = None
    
#
# Button handler function for the generate button. It starts the
# generate thread.
#
def generateHandler():
  global genThread
  if genThread == None or not genThread.is_alive():
    genThread = threading.Thread(target=randomize)
    progressBar.start(50)
    genThread.start()
  
#
# Function to display a file chooser for the input ROM.
# Set the chosen file to the datastore.
# Target of the "Browse" button.
#
def browseForRom():
  datastore.inputFile.set(askopenfilename())

def flagClear():
    datastore.difficulty.set("normal")
    datastore.flags['g'].set(0)
    datastore.flags['s'].set(0)
    datastore.flags['d'].set(0)
    datastore.flags['l'].set(0)
    datastore.flags['ro'].set(0)
    datastore.flags['b'].set(0)
    datastore.flags['z'].set(0)
    datastore.flags['p'].set(0)
    datastore.flags['c'].set(0)
    datastore.flags['m'].set(0)
    datastore.flags['q'].set(0)
    datastore.flags['tb'].set(0)
    datastore.flags['cr'].set(0)
    datastore.techRando.set("Normal")
    # Make sure all checkboxes are enabled
    for widget in optionsFrame.winfo_children():
      if type(widget) == tk.Checkbutton:
        widget.configure(state="normal")

def presetRace():
    flagClear()
    datastore.difficulty.set("normal")
    datastore.flags['g'].set(1)
    datastore.flags['s'].set(1)
    datastore.flags['d'].set(1)
    datastore.flags['z'].set(1)
    datastore.flags['p'].set(1)
    datastore.techRando.set("Fully Random")

def presetNew():
    flagClear()
    datastore.difficulty.set("easy")
    datastore.flags['g'].set(1)
    datastore.flags['s'].set(1)
    datastore.flags['d'].set(1)
    datastore.flags['z'].set(1)
    datastore.flags['p'].set(1)
    datastore.flags['m'].set(1)
    datastore.techRando.set("Fully Random")

def presetLost():
    flagClear()
    datastore.difficulty.set("normal")
    datastore.flags['g'].set(1)
    datastore.flags['s'].set(1)
    datastore.flags['d'].set(1)
    datastore.flags['z'].set(1)
    datastore.flags['l'].set(1)
    datastore.techRando.set("Fully Random")

def presetHard():
    flagClear()
    datastore.difficulty.set("hard")
    datastore.flags['g'].set(1)
    datastore.flags['s'].set(1)
    datastore.flags['d'].set(1)
    datastore.flags['b'].set(1)
    datastore.flags['c'].set(1)
    datastore.techRando.set("Balanced Random")

# Frame for presets, hopefully.

def getPresetsFrame(window):
  frame = tk.Frame(window, borderwidth=1)
  row = 0
  #Presets Header
  tk.Label(frame, text="Preset Selection:").grid(row=row, column=0, sticky=tk.E)
  
  #Preset Buttons
  tk.Button(frame, text="Race", command=presetRace).grid(row=row, column=1)
  tk.Button(frame, text="New Player", command=presetNew).grid(row=row, column=2)
  tk.Button(frame, text="Lost Worlds", command=presetLost).grid(row=row, column=3)
  tk.Button(frame, text="Hard", command=presetHard).grid(row=row, column=4)
  return frame
  
#
# Populate and return the frame where the user can pick game flags.
#  
def getGameFlagsFrame(window):
  frame = tk.Frame(window, borderwidth = 1)
  row = 0
  pendantCheckbox = None
  bossScalingCheckbox = None
  lostWorldsCheckbox = None
  
  # Dropdown for the difficulty flags
  difficultyValues = ["easy", "normal", "hard"]
  label = tk.Label(frame, text="Difficulty:")
  var = tk.StringVar()
  var.set('normal')
  datastore.difficulty = var
  dropdown = tk.OptionMenu(frame, var, *difficultyValues)
  dropdown.config(width = 5)
  label.grid(row = row, column = 0, sticky=tk.W)
  dropdown.grid(row = row, column = 1, sticky=tk.W)
  CreateToolTip(dropdown, \
      "Game difficulty:\n"
      "Easy - Quality of treasure from chests and monster drops greatly improved.\n"
      "Normal - Standard treasure drops, standard enemy difficulty.\n"
      "Hard - Reduced treasure quality, some enemies have been made more difficult, "
      "some exp and tech point rewards have been reduced.")
  row = row + 1
  
  # Checkboxes for the randomizer flags
  # Disable glitches
  var = tk.IntVar()
  datastore.flags['g'] = var
  checkButton = tk.Checkbutton(frame, text="Disable Glitches(g)", variable = var)
  checkButton.grid(row=row, sticky=tk.W, columnspan=3)
  CreateToolTip(checkButton, "Disabled common glitches such as the unequip and save anywhere glitches.")
  row = row + 1
  
  # Faster overworld movement
  var = tk.IntVar()
  datastore.flags['s'] = var
  checkButton = tk.Checkbutton(frame, text="Fast overworld movement(s)", variable = var)
  checkButton.grid(row=row, sticky=tk.W, columnspan=3)
  CreateToolTip(checkButton, "Move faster on the overworld while walking and riding in the Epoch.")
  row = row + 1
  
  # faster dpad inputs in menus
  var = tk.IntVar()
  datastore.flags['d'] = var
  checkButton = tk.Checkbutton(frame, text="Fast dpad in menus(d)", variable = var)
  checkButton.grid(row=row, sticky=tk.W, columnspan=3)
  CreateToolTip(checkButton, "Dpad inputs in menus are faster and more responsive.")
  row = row + 1
  
  # Lost Worlds

  #
  # Callback function to disable the early pendant charge option when 
  # the user selects the Lost Worlds mode. Early Pendant is not avaiable
  # in Lost Worlds mode.
  #
  def togglePendantState():
    if datastore.flags['l'].get() == 1:
      datastore.flags['p'].set(0)
      pendantCheckbox.config(state=tk.DISABLED)
    else:
      pendantCheckbox.config(state=tk.NORMAL)
  
  var = tk.IntVar()
  datastore.flags['l'] = var
  lostWorldsCheckbox = tk.Checkbutton(frame, text="Lost Worlds(l)", variable = var, command=togglePendantState)
  lostWorldsCheckbox.grid(row=row, sticky=tk.W, columnspan=3)
  CreateToolTip(lostWorldsCheckbox, "An alternate game mode where you start with access to Prehistory, the Dark Ages, and the Future. Find the clone and c.trigger to climb Death Peak and beat the Black Omen, or find the Dreamstone and Ruby Knife to make your way to Lavos through the Ocean Palace. 600AD and 1000AD are unavailable until the very end of the game.")
  row = row + 1
  
  # Boss randomization
  var = tk.IntVar()
  datastore.flags['ro'] = var
  bossRandoCheckbox = tk.Checkbutton(frame, text="Randomize bosses(ro)", variable = var)
  bossRandoCheckbox.grid(row=row, sticky=tk.W, columnspan=3)
  CreateToolTip(bossRandoCheckbox, "Various dungeon bosses are shuffled and scaled.  Does not affect end game bosses.")
  row = row + 1

  # Boss scaling
  var = tk.IntVar()
  datastore.flags['b'] = var
  bossScalingCheckbox = tk.Checkbutton(frame, text="Boss scaling(b)", variable = var)
  bossScalingCheckbox.grid(row=row, sticky=tk.W, columnspan=3)
  CreateToolTip(bossScalingCheckbox, "Bosses are scaled in difficulty based on how many key items they block.  Early bosses are unaffected.")
  row = row + 1
  
  # Zeal 2 as last boss
  var = tk.IntVar()
  datastore.flags['z'] = var
  checkButton = tk.Checkbutton(frame, text="Zeal 2 as last boss(z)", variable = var)
  checkButton.grid(row=row, sticky=tk.W, columnspan=3)
  CreateToolTip(checkButton, "The game ends after defeating Zeal 2 when going through the Black Omen.  Lavos is still required for the Ocean Palace route.")
  row = row + 1
  
  # Early pendant charge
  var = tk.IntVar()
  datastore.flags['p'] = var
  pendantCheckbox= tk.Checkbutton(frame, text="Early Pendant Charge(p)", variable = var)
  pendantCheckbox.grid(row=row, sticky=tk.W, columnspan=3)
  CreateToolTip(pendantCheckbox, "The pendant becomes charged immediately upon access to the Future, granting access to sealed doors and chests.")
  row = row + 1
  
  # Locked characters
  var = tk.IntVar()
  datastore.flags['c'] = var
  checkButton = tk.Checkbutton(frame, text="Locked characters(c)", variable = var)
  checkButton.grid(row=row, sticky=tk.W, columnspan=3)
  CreateToolTip(checkButton, "The Dreamstone is required to access the character in the Dactyl Nest and power must be turned on at the Factory before the Proto Dome character can be obtained.")
  row = row + 1

  # Unlocked Magic
  var = tk.IntVar()
  datastore.flags['m'] = var
  checkButton = tk.Checkbutton(frame, text="Unlocked Magic(m)", variable = var)
  checkButton.grid(row=row, sticky=tk.W, columnspan=3)
  CreateToolTip(checkButton, "Magic is unlocked at the start of the game, no trip to Spekkio required.")
  row = row + 1

  # Quiet Mode (No Music)
  var = tk.IntVar()
  datastore.flags['q'] = var
  checkButton = tk.Checkbutton(frame, text="Quiet Mode - No Music (q)", variable = var)
  checkButton.grid(row=row, sticky=tk.W, columnspan=3)
  CreateToolTip(checkButton, "Music is disabled.  Sound effects will still play.")
  row = row + 1

  # Tab Treasures
  var = tk.IntVar()
  datastore.flags['tb'] = var
  checkButton = tk.Checkbutton(frame, text="Make all treasures tabs(tb)", variable = var)
  checkButton.grid(row=row, sticky=tk.W, columnspan=3)
  CreateToolTip(checkButton, "All treasures chest contents are replaced with power, magic, or speed tabs.")
  row = row + 1
  
  # Chronosanity
  def disableChronosanityIncompatibleFlags():
    if datastore.flags['cr'].get() == 1:
      # Boss scaling doesn't work with full rando.
      datastore.flags['b'].set(0)
      bossScalingCheckbox.config(state=tk.DISABLED)
    else:
      bossScalingCheckbox.config(state=tk.NORMAL)
      
  var = tk.IntVar()
  datastore.flags['cr'] = var
  checkButton = tk.Checkbutton(frame, text="Chronosanity(cr)", variable = var, command=disableChronosanityIncompatibleFlags)
  checkButton.grid(row=row, sticky=tk.W, columnspan=3)
  CreateToolTip(checkButton, "Key items can now show up in most treasure chests in addition to their normal locations.")
  row = row + 1

  # Dropdown for the tech rando
  techRandoValues = ["Normal", "Balanced Random", "Fully Random"]
  label = tk.Label(frame, text="Tech Randomization:")
  var = tk.StringVar()
  var.set('Normal')
  datastore.techRando = var
  dropdown = tk.OptionMenu(frame, var, *techRandoValues)
  dropdown.config(width = 20)
  label.grid(row = row, column = 0, sticky=tk.W)
  dropdown.grid(row = row, column = 1, sticky=tk.W)
  CreateToolTip(dropdown, "Determines the order in which techs are learned:\n"
      "Normal - Vanilla tech order.\n"
      "Balanced Random - Random tech order, but stronger techs are more likely to show up later.\n"
      "Fully Random - Tech order is fully randomized.")
  row = row + 1
  
  # Let the user choose a seed (optional parameter)
  tk.Label(frame, text="Seed(optional):").grid(row=row, column=0, sticky=tk.E)
  datastore.seed = tk.StringVar()
  tk.Entry(frame, textvariable=datastore.seed).grid(row=row, column=1)
  row = row + 1
  
  # Let the user select the base ROM to copy and patch
  tk.Label(frame, text="Input ROM:").grid(row=row, column=0, sticky=tk.E)
  datastore.inputFile = tk.StringVar()
  tk.Entry(frame, textvariable=datastore.inputFile).grid(row=row, column=1)
  tk.Button(frame, text="Browse", command=browseForRom).grid(row=row, column=2)
  row = row + 1

  # Add a progress bar to the GUI for ROM generation
  global progressBar
  progressBar = ttk.Progressbar(frame, orient='horizontal', mode='indeterminate')
  progressBar.grid(row = row, column = 0, columnspan = 3, sticky=tk.N+tk.S+tk.E+tk.W)
  row = row + 1
  
  return frame
  

#
# Main entry function for the GUI. Set up and launch the display.
#  
def guiMain():
  global optionsFrame
  mainWindow = tk.Tk()
  mainWindow.wm_title("Jets of Time")

  presetFrame = getPresetsFrame(mainWindow)
  presetFrame.pack(expand=1, fill="both")
  
  optionsFrame = getGameFlagsFrame(mainWindow)
  optionsFrame.pack(expand=1, fill="both")
  
  tk.Button(mainWindow, text="Generate", command=generateHandler).pack()
  
  mainWindow.mainloop()
  
