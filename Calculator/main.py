# Project Plan:
# Make a pop-up window that allows users to convert units of measurement for both time and length
# The program will use TKinter in Python.

# --- IMPORTS ---
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk  # For enhanced styling

# --- TIME CONVERSION VARIABLES ---
# List of time units
timeUnits = ["Seconds", "Minutes", "Hours", "Days", "Weeks", "Months", "Years"]

# Conversion factors for time units
# Each unit is represented as a list of scaling factors to convert to other units
secondUnitTime = {
    "Seconds" :  [1, 60, 3600, 86400, 604800, 2628001, 31536013],
    "Minutes" :  [(1 / 60), 1, 60, 1440, 10080, 43800, 525600],
    "Hours"   :  [(1 / 3600), (1 / 60), 1, 24, 168, 730, 8760],
    "Days"    :  [(1 / 86400), (1 / 1440), (1 / 24), 1, 7, 30.4167, 365.25],
    "Weeks"   :  [(1 / 604800), (1 / 10080), (1 / 168), (1 / 7), 1, 4.34524, 52.149],
    "Months"  :  [(125 / 328500), (625 / 27375012), (3125 / 2281251), (25000 / 760417), (1 / 4.34524), 1, 12],
    "Years"   :  [(1 / 31536013), (1 / 525600), (1 / 8760), (1 / 365.25), (1 / 52.149), (1 / 12), 1],
}

# --- LENGTH CONVERSION VARIABLES ---
# List of length units
lengthUnits = ["Millimeter", "Centimeter", "Inch", "Foot", "Yard", "Meter", "Kilometer", "Mile"]

# Conversion factors for length units
# Each number represents how many of the previous unit fits within it
secondUnitLength = [1, 10, 2.54, 12, 3, 1.09361, 1000, 1.60934]

# --- CONVERSION FUNCTIONS ---
def convertTime(quantity=None, unit1=None, unit2=None):
    """
    Converts a given quantity from one time unit to another.
    If no arguments are provided, it retrieves values from the GUI.
    """
    outputBox = False

    # Retrieve values from GUI if not provided
    if not quantity and not unit1 and not unit2:
        outputBox = True
        quantity = float(timeEntry.get())
        unit1 = timeFirstUnit.get()
        unit2 = timeSecondUnit.get()

        # Error handling for invalid inputs
        if not timeEntry.get().isdigit():
            timeOutputString.set("Enter a number!")
        if timeFirstUnit.get() not in secondUnitTime.keys():
            timeOutputString.set("Enter a valid first unit")
        if timeSecondUnit.get() not in secondUnitTime.keys():
            timeOutputString.set("Enter a valid second unit")

    # Perform the conversion
    secondUnitIndex = timeUnits.index(unit1)
    scaling = secondUnitTime[unit2][secondUnitIndex]
    newQuantity = round(quantity * scaling, 7)

    # Display the result in the output box if required
    if outputBox:
        timeOutputString.set(" " + str(newQuantity) + " ")

    return newQuantity

def convertLength(quantity, unit1, unit2):
    """
    Converts a given quantity from one length unit to another.
    """
    # Error handling for invalid inputs
    if not quantity.isdigit():
        lengthOutputString.set("Enter a number!")
        return
    else:
        quantity = float(quantity)

    firstIndex = lengthUnits.index(unit1)
    secondIndex = lengthUnits.index(unit2)

    # Handle cases where units are the same
    if firstIndex == secondIndex:
        result = quantity
        lengthOutputString.set(" " + str(result) + " ")

    # Handle cases where the first unit is larger
    elif firstIndex > secondIndex:
        subList = secondUnitLength[secondIndex + 1:firstIndex + 1]
        result = quantity
        for scaling in subList:
            result *= scaling
        result = round(result, 3)
        lengthOutputString.set(" " + str(result) + " ")

    # Handle cases where the second unit is larger
    else:
        subList = secondUnitLength[firstIndex + 1:secondIndex + 1]
        result = quantity
        for scaling in subList:
            result /= scaling
        result = round(result, 3)
        lengthOutputString.set(" " + str(result) + " ")

# --- TKINTER WINDOW NAVIGATION FUNCTIONS ---
def raiseTime():
    """Raise the time conversion window."""
    timeWindow.tkraise()

def raiseLength():
    """Raise the length conversion window."""
    lengthWindow.tkraise()

def raiseStart():
    """Raise the start window."""
    startWindow.tkraise()

# --- ROOT TKINTER WINDOW ---
# Create the main application window
root = ttk.Window(themename='darkly')
root.title("Measurements Converter")
root.geometry("620x620")

# Create frames for each window
startWindow = tk.Frame(root)
startWindow.grid(row=0, column=0, sticky="news")

timeWindow = tk.Frame(root)
timeWindow.grid(row=0, column=0, sticky="news")

lengthWindow = tk.Frame(root)
lengthWindow.grid(row=0, column=0, sticky="news")

# --- START WINDOW COMPONENTS ---
# Title label
titleLabel = ttk.Label(master=startWindow, text="Choose measurement type", font="Courier 20 bold", anchor="center")
titleLabel.pack(pady=20)

# Buttons to navigate to time and length conversion windows
inputFrame = ttk.Frame(master=startWindow)
buttonTime = ttk.Button(master=inputFrame, text="Time", command=raiseTime)
buttonLength = ttk.Button(master=inputFrame, text="Length", command=raiseLength)
buttonTime.pack(side="left", padx=15)
buttonLength.pack(side="left")
inputFrame.pack()

# --- TIME CONVERSION COMPONENTS ---
# Title label
timeLabel = ttk.Label(master=timeWindow, text="Time Units Conversion", font="Courier 20 bold")
timeLabel.pack(pady=20, padx=15)

# Input units
timeInputFrame = ttk.Frame(master=timeWindow)
timeFirstUnit = ttk.Combobox(timeInputFrame, textvariable=tk.StringVar(), values=timeUnits)
timeFirstUnit.current(0)
timeFirstUnit.pack(side="left")

canvas = tk.Canvas(timeInputFrame, width=100, height=50)
canvas.pack(side="left")
canvas.create_line(25, 25, 75, 25, arrow=tk.LAST, fill="blue", width=3)

timeSecondUnit = ttk.Combobox(timeInputFrame, textvariable=tk.StringVar(), values=timeUnits)
timeSecondUnit.current(0)
timeSecondUnit.pack(side="left")
timeInputFrame.pack(padx=20)

# Input field for quantity
timeInput = ttk.Frame(master=timeWindow)
timeInputLabel = ttk.Label(master=timeInput, text="Enter Value ")
timeInputLabel.pack(side='left', pady=20)
timeEntry = ttk.Entry(master=timeInput)
timeEntry.pack(side="left")
timeInput.pack()

# Convert button
timeConvert = ttk.Button(master=timeWindow, text="Convert", command=convertTime)
timeConvert.pack(pady=15)

# Output field
timeOutput = ttk.Frame(master=timeWindow)
timeOutputString = tk.StringVar()
timeOutputLabel = ttk.Label(master=timeOutput, text="Output", font="Courier", textvariable=timeOutputString, borderwidth=1, relief="solid")
timeOutputString.set("Output")
timeOutputLabel.pack()
timeOutput.pack()

# Common conversions
commonTimes = [
    (1, "Hours", "Seconds"),
    (1, "Days", "Seconds"),
    (1, "Weeks", "Hours"),
    (1, "Years", "Seconds"),
    (1, "Seconds", "Years"),
]
timeCommonConversions = ttk.Frame(master=timeWindow)
timeCommonLabel = ttk.Label(master=timeCommonConversions, text=" Common Conversions ", font=("Courier", 16), borderwidth=2, relief="solid")
timeCommonLabel.pack(pady=15)
for item in commonTimes:
    value = convertTime(quantity=item[0], unit1=item[1], unit2=item[2])
    itemText = str(item[0]) + " " + item[1] + "  ==  " + str(value) + " " + item[2]
    label = tk.Label(master=timeCommonConversions, text=itemText)
    label.pack()
timeCommonConversions.pack()

# Back button
timeBackButton = ttk.Button(master=timeWindow, text="Back", command=raiseStart)
timeBackButton.pack(pady=10)

# --- LENGTH CONVERSION COMPONENTS ---
# Title label
lengthLabel = ttk.Label(master=lengthWindow, text="Length Units Conversion", font="Courier 20 bold")
lengthLabel.pack(pady=20, padx=15)

# Input units
lengthInputFrame = ttk.Frame(master=lengthWindow)
lengthFirstUnit = ttk.Combobox(lengthInputFrame, textvariable=tk.StringVar(), values=lengthUnits)
lengthFirstUnit.current(0)
lengthFirstUnit.pack(side="left")

canvas = tk.Canvas(lengthInputFrame, width=100, height=50)
canvas.pack(side="left")
canvas.create_line(25, 25, 75, 25, arrow=tk.LAST, fill="blue", width=3)

lengthSecondUnit = ttk.Combobox(lengthInputFrame, textvariable=tk.StringVar(), values=lengthUnits)
lengthSecondUnit.current(0)
lengthSecondUnit.pack(side="left")
lengthInputFrame.pack(padx=20)

# Input field for quantity
lengthInput = ttk.Frame(master=lengthWindow)
lengthInputLabel = ttk.Label(master=lengthInput, text="Enter Value ")
lengthInputLabel.pack(side='left', pady=20)
lengthEntry = ttk.Entry(master=lengthInput)
lengthEntry.pack(side="left")
lengthInput.pack()

# Convert button
lengthOutputString = tk.StringVar()  # Positioned early because it is referenced in the next line
lengthConvert = ttk.Button(master=lengthWindow, text="Convert", command=lambda: convertLength(quantity=lengthEntry.get(), unit1=lengthFirstUnit.get(), unit2=lengthSecondUnit.get()))
lengthConvert.pack(pady=15)

# Output field
lengthOutput = ttk.Frame(master=lengthWindow)
lengthOutputLabel = ttk.Label(master=lengthOutput, text="Output", font="Courier", textvariable=lengthOutputString, borderwidth=1, relief="solid")
lengthOutputString.set("Output")
lengthOutputLabel.pack()
lengthOutput.pack()

# Back button
lengthBackButton = ttk.Button(master=lengthWindow, text="Back", command=raiseStart)
lengthBackButton.pack(pady=15)

# --- MAINLOOP ---
# Start the application
startWindow.tkraise()
root.mainloop()