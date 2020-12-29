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
    datastore.flags['b'].set(0)
    datastore.flags['z'].set(0)
    datastore.flags['p'].set(0)
    datastore.flags['c'].set(0)
    datastore.flags['m'].set(0)
    datastore.techRando.set("Normal")

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
  row = row + 1
  
  # Checkboxes for the randomizer flags
  # Disable glitches
  var = tk.IntVar()
  datastore.flags['g'] = var
  tk.Checkbutton(frame, text="Disable Glitches(g)", variable = var).grid(row=row, sticky=tk.W, columnspan=3)
  row = row + 1
  
  # Faster overworld movement
  var = tk.IntVar()
  datastore.flags['s'] = var
  tk.Checkbutton(frame, text="Fast overworld movement(s)", variable = var).grid(row=row, sticky=tk.W, columnspan=3)
  row = row + 1
  
  # faster dpad inputs in menus
  var = tk.IntVar()
  datastore.flags['d'] = var
  tk.Checkbutton(frame, text="Fast dpad in menus(d)", variable = var).grid(row=row, sticky=tk.W, columnspan=3)
  row = row + 1
  
  # Lost Worlds

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
  tk.Checkbutton(frame, text="Lost Worlds(l)", variable = var, command=togglePendantState).grid(row=row, sticky=tk.W, columnspan=3)
  row = row + 1
  
  # Boss scaling
  var = tk.IntVar()
  datastore.flags['b'] = var
  tk.Checkbutton(frame, text="Boss scaling(b)", variable = var).grid(row=row, sticky=tk.W, columnspan=3)
  row = row + 1
  
  # Zeal 2 as last boss
  var = tk.IntVar()
  datastore.flags['z'] = var
  tk.Checkbutton(frame, text="Zeal 2 as last boss(z)", variable = var).grid(row=row, sticky=tk.W, columnspan=3)
  row = row + 1
  
  # Early pendant charge
  var = tk.IntVar()
  datastore.flags['p'] = var
  pendantCheckbox= tk.Checkbutton(frame, text="Early Pendant Charge(p)", variable = var)
  pendantCheckbox.grid(row=row, sticky=tk.W, columnspan=3)
  row = row + 1
  
  # Locked characters
  var = tk.IntVar()
  datastore.flags['c'] = var
  tk.Checkbutton(frame, text="Locked characters(c)", variable = var).grid(row=row, sticky=tk.W, columnspan=3)
  row = row + 1

  # Unlocked Magic
  var = tk.IntVar()
  datastore.flags['m'] = var
  tk.Checkbutton(frame, text="Unlocked Magic(m)", variable = var).grid(row=row, sticky=tk.W, columnspan=3)
  row = row + 1

  # Quiet Mode (No Music)
  var = tk.IntVar()
  datastore.flags['q'] = var
  tk.Checkbutton(frame, text="Quiet Mode - No Music (q)", variable = var).grid(row=row, sticky=tk.W, columnspan=3)
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
  mainWindow = tk.Tk()
  mainWindow.wm_title("Jets of Time")

  presetFrame = getPresetsFrame(mainWindow)
  presetFrame.pack(expand=1, fill="both")
  
  optionsFrame = getGameFlagsFrame(mainWindow)
  optionsFrame.pack(expand=1, fill="both")
  
  tk.Button(mainWindow, text="Generate", command=generateHandler).pack()
  
  mainWindow.mainloop()
  
