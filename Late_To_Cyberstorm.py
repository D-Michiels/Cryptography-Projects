from tkinter import *
from PIL import Image, ImageTk
import os
import sys

# resource_path function for converting files .exe: https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Room:
    def __init__(self, name, image, exits=None):
        self._name = name
        self._image = image
        self.exits = exits if exits else {}
        self.hints = []
        self.items = {}
        self.photo_image = None
        self.interactive_areas = {}  
        self.passwords = {}
        self.required_items = {}  

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value

    def addExit(self, exit_name, room, position, password=None, required_item=None):
        self.exits[exit_name] = (room, position)
        if password:
            self.passwords[exit_name] = password
        if required_item:
            self.required_items[exit_name] = required_item

    def __str__(self):
        s = f"You are in {self.name}.\n"
        return s

    def set_image_for_display(self, widget):
        original_image = Image.open(self.image)
        width, height = widget.winfo_width(), widget.winfo_height()
        original_image = original_image.resize((width, height), Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(original_image)

    def addInteractiveArea(self, coord, action):
        self.interactive_areas[coord] = action

    def checkInteractiveArea(self, x, y):
        for (x1, y1, x2, y2), action in self.interactive_areas.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                return action()
        return None

class Game(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.inventory = []
        # self.used_passwords = set()  # Set to store used passwords
        self.createRooms()
        self.setupGUI()
    #     self.image_label.bind("<Motion>", self.on_mouse_hover)

    # def on_mouse_hover(self, event):
    #     x, y = event.x, event.y
    #     self.setStatus(f"Mouse coordinates: ({x}, {y})")

    def createRooms(self):
        r0 = Room("", resource_path("Images/title_card.gif"))

        # First Floor
        r1 = Room("First Floor Lobby", resource_path("Images/iesb_1_lobby.ppm"))
        r3 = Room("Cyber Storm", resource_path("Images/cyber_room.gif"))
        r7 = Room("Popcorn/Hall Area", resource_path("Images/popcorn_area.ppm"))
        r12 = Room("Hall1", resource_path("Images/hallL.ppm"))
        r11 = Room("Popcorn Area", resource_path("Images/locked_bag.ppm"))
        r8 = Room("Vending-Machine", resource_path("Images/vend-machine.ppm"))
        r13 = Room("Keypad", resource_path("Images/keypad.ppm"))
        r10 = Room("Success", resource_path("Images/final.ppm"))
        r15 = Room("Opened Bag", resource_path("Images/bag_id.ppm"))
        r16 = Room("Clue?", resource_path("Images/clue__1.ppm"))
        r25 = Room("Got it!", resource_path("Images/keypad_id.ppm"))
        

        # Second Floor
        r2 = Room("Second Floor Lobby", resource_path("Images/2nd_floor.ppm"))
        r4 = Room("Dr. Timo's Office", resource_path("Images/timo.ppm"))
        r5 = Room("2nd Floor Hallway (right)", resource_path("Images/hallr.ppm"))
        r17 = Room("2nd Floor Hallway (left)", resource_path("Images/left-hall.ppm"))
        r14 = Room("Study Room", resource_path("Images/study-room.ppm"))
        r26 = Room("Board", resource_path("Images/study-board.ppm"))
        r9 = Room("Dr. Anky's Office", resource_path("Images/anky.ppm"))
        r18 = Room("Inside Dr. Timo's Office", resource_path("Images/timo_office.ppm"))
        r19 = Room("qr_code", resource_path("Images/qr_code.ppm"))
        r20 = Room("Drawer", resource_path("Images/drawer_id.ppm"))
        r21 = Room("Dr. Anky's Office", resource_path("Images/in_anky_office.ppm"))
        r27 = Room("Some weird text?", resource_path("Images/anky_closeup.ppm"))
        r22 = Room("Room 216", resource_path("Images/room216.ppm"))
        r23 = Room("Room 216 (inside)", resource_path("Images/216_1.ppm"))
        r24 = Room("Room 216 board", resource_path("Images/216_2.ppm"))

        r0.addExit("START", r1, (250, 30))

        # First Floor
        r1.addExit("upstairs", r2, (480, 300))  # Position (x, y) for button on the image
        # r1.addInteractiveArea((100, 0, 200, 500), lambda: (self.addItemToInventory("key", "A small rusty key"), self.changeRoomImage("iesb_1_lobby.ppm")))
        r1.addExit("Cyber Storm", r3, (75, 320))
        r1.addExit("Walk forward", r7, (250,490))
        r3.addExit("Open", r10, (200, 285), required_item="Dr. Heath's ID")
        r3.addExit("Back", r1, (250, 500))
        r7.addExit("Back", r1, (250, 500))
        r7.addExit("Popcorn", r11, (350, 330))
        r7.addExit("Hall", r12, (146, 300))
        r8.addExit("Back", r12, (250, 500))
        r8.addExit("keypad", r13, (490, 343))
        # Add text to keypad that says to enter in secret selection to get ID
        r13.addExit("Enter", r25, (250, 300), password="4e6f7468696e672068657265")
        r25.hints.append("Right-click item to pick it up")
        r25.addInteractiveArea((202, 237, 413, 341), lambda: (self.addItemToInventory("Dr. Heath's ID", "This is an ID card"), self.changeRoomImage(resource_path("Images/keypad.ppm"))))
        r25.addExit("Back", r8, (250, 540))
        r13.addExit("Back", r8, (250, 540))
        r11.addExit("Back", r7, (250, 550))
        r11.addExit("Look", r16, (292, 376))
        r16.addExit("Back", r11, (250, 500))
        r11.addExit("Open", r15, (128, 397), password="racecar")
        r15.hints.append("Right-click item to pick it up")
        r15.addInteractiveArea((215, 280, 395, 365), lambda: (self.addItemToInventory("Dr. Timo's ID", "This is an ID card"), self.changeRoomImage(resource_path("Images/opened_bag1.ppm"))))
        r15.addExit("Back", r11, (250, 500))
        r12.addExit("Back", r7, (250, 500))
        r12.addExit("Outside", r1, (150, 300))
        r12.addExit("Vending", r8, (450, 350))


        # Second Floor
        r2.addExit("downstairs", r1, (250, 510))
        r2.addExit("Left", r17, (10, 280))
        r17.addExit("Back", r2, (250, 500))
        r17.addExit("Room 216", r22, (270, 265))
        r22.addExit("Open", r23, (250, 330), password="breadbutter")
        r22.addExit("Back", r17, (250, 500))
        r23.addExit("Back", r22, (250, 500))
        r23.addExit("Look", r24, (425, 210))
        r24.addExit("Back", r23, (250, 500))
        r17.addExit("Dr. Timo's Office", r4, (40, 315))
        r4.addExit("Open", r18, (315, 275), required_item="Dr. Timo's ID")
        r18.addExit("Back", r4, (250, 500))
        r18.addExit("Open", r20, (360, 380), password="timo2024")
        r20.hints.append("Right-click item to pick it up")
        r20.addInteractiveArea((248, 348, 345, 385), lambda: (self.addItemToInventory("Dr. Anky's ID", "This is an ID card"), self.changeRoomImage(resource_path("Images/opened_drawer.ppm"))))
        r18.addExit("Look", r19, (300, 220))
        r19.addExit("Back", r18, (250, 500))
        r20.addExit("Back", r18, (250, 500))
        r2.addExit("Right", r5, (475, 280))
        r4.addExit("Back", r17, (250, 500))
        r5.addExit("Back", r2, (250, 500))
        r5.addExit("Study Room", r14, (480, 390))
        r5.addExit("Dr. Anky's Office", r9, (190, 260))
        r5.addExit("Back", r2, (250, 500))
        r9.addExit("Open", r21, (195, 305), required_item="Dr. Anky's ID")
        r9.addExit("Back", r5, (250, 500))
        r21.hints.append("Hints:\n 1. Apes Together Strong + QmxhaXNlIGRl \n 2. Use Deafaults")
        r21.addExit("Back", r9, (250, 500))
        r21.addExit("Look", r27, (395, 320))
        r27.addExit("Back", r21, (250, 500))
        r14.addExit("Back", r5, (250, 500))
        r14.addExit("Look", r26, (375, 115))
        r26.addExit("Back", r14, (250, 500))
        r26.hints.append("Hints:\n 1. It takes two")

        

        self.currentRoom = r0
        self.inventory = []

    def setupGUI(self):
        self.pack(fill=BOTH, expand=1)
        self.player_input = Entry(self, bg="white")
        self.player_input.bind("<Return>", self.process)
        self.player_input.pack(side=BOTTOM, fill=X)
        self.player_input.focus_set()

        self.text_frame = Frame(self, width=400)
        self.text_frame.pack(side=RIGHT, fill=Y, expand=False)
        self.text_frame.pack_propagate(False)
        self.text = Text(self.text_frame, bg="lightgrey", state=DISABLED)
        self.text.pack(fill=BOTH, expand=True)

        # Status label initialization
        self.status_label = Label(self.text_frame, text="", bg="lightgrey", fg="black")
        self.status_label.pack(side=BOTTOM, fill=X)

        self.image_frame = Frame(self, width=600)
        self.image_frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.image_frame.pack_propagate(False)
        self.image_label = Label(self.image_frame)
        self.image_label.pack(fill=BOTH, expand=True)
        self.after(100, self.postSetup)
        

    def postSetup(self):
        self.update_idletasks()  # Ensure GUI is fully initialized
        if self.currentRoom:
            self.currentRoom.set_image_for_display(self.image_label)
            self.image_label.config(image=self.currentRoom.photo_image)
            self.setStatus(str(self.currentRoom))
            self.setupRoomExits()
            self.image_label.bind("<Button-3>", self.on_left_click)

    def setupRoomExits(self):
        for exit_name, (room, pos) in self.currentRoom.exits.items():
            if exit_name in self.currentRoom.passwords:
                # If the exit has a password, use attempt_access to handle the button press
                btn = Button(self.image_frame, text=exit_name,
                            command=lambda r=room, e=exit_name: self.attempt_access(r, e),
                            bg='#f54257')  # Red color for locked doors
            elif exit_name in self.currentRoom.required_items:
                required_item = self.currentRoom.required_items[exit_name]
                if required_item in self.inventory:
                    btn = Button(self.image_frame, text=exit_name,
                                command=lambda r=room: self.change_room(r),
                                bg='light green')  # Green color for unlocked doors
                else:
                    btn = Button(self.image_frame, text=exit_name,bg='#f5a742')  # Orange color for item-locked doors
            else: 
                # No password or item needed, proceed as normal
                btn = Button(self.image_frame, text=exit_name,
                            command=lambda r=room: self.change_room(r),
                            bg='light green')  # Green color for unlocked doors
            btn.place(x=pos[0], y=pos[1], width=100, height=25)

    def attempt_access(self, room, exit_name):
        if exit_name in self.currentRoom.passwords:
            password = self.currentRoom.passwords[exit_name]
            entered_password = self.player_input.get().strip().lower()
            if entered_password == password:
                del self.currentRoom.passwords[exit_name]  # Remove the password requirement
                self.change_room(room)
                self.status_label.config(text="Access granted.", fg="green")
                self.refreshRoomExits()  # Refresh the room exits to reflect the unlocked state
            else:
                self.status_label.config(text="Incorrect password.", fg="red")
        else:
            self.change_room(room)
            self.refreshRoomExits()  # Refresh the exits even if no password was required


    def refreshRoomExits(self):
        for widget in self.image_frame.winfo_children():
            if isinstance(widget, Button):
                widget.destroy()
        self.setupRoomExits()

    def on_left_click(self, event):
        action = self.currentRoom.checkInteractiveArea(event.x, event.y)
        if action:
            action  # Execute the action associated with the interactive area

    def addItemToInventory(self, item, description):
        if item not in self.inventory:
            self.inventory.append(item)
            self.setStatus(f"You picked up {description}\n{str(self.inventory)}")
        # else:
            # self.setStatus("You already have this item.")

    def changeRoomImage(self, new_image_path):
            self.currentRoom.image = new_image_path
            self.currentRoom.set_image_for_display(self.image_label)
            self.image_label.config(image=self.currentRoom.photo_image)
            # self.setStatus("Room changed")


    def setStatus(self, status):
        room_hints = self.currentRoom.hints
        hints_text = "\n".join(room_hints) if room_hints else ""
        inventory_status = "Inventory: " + ", ".join(self.inventory) if self.inventory else "Inventory: []"
        full_status = status + "\n" + inventory_status + "\n\n" + hints_text
        self.text.config(state=NORMAL)
        self.text.delete("1.0", END)
        self.text.insert(END, full_status)
        self.text.config(state=DISABLED)


    def change_room(self, room, required_item=None):
        if required_item and required_item not in self.inventory:
            self.setStatus(f"The door to {room.name} is locked.")
            return
        self.currentRoom = room
        self.currentRoom.set_image_for_display(self.image_label)
        self.image_label.config(image=self.currentRoom.photo_image)
        self.setStatus(str(self.currentRoom))
        for widget in self.image_frame.winfo_children():
            if isinstance(widget, Button):
                widget.destroy()
        self.setupRoomExits()

    def process(self, event):
        entered_password = self.player_input.get().strip().lower()
        self.player_input.delete(0, END)  # Clear the input field after getting the text
        
        # Check if the current room exit requires a password
        for exit_name, (room, pos) in self.currentRoom.exits.items():
            if exit_name in self.currentRoom.passwords and self.currentRoom.passwords[exit_name] == entered_password:
                del self.currentRoom.passwords[exit_name]  # Remove the password requirement
                self.change_room(room)
                self.status_label.config(text="Access granted.", fg="green")
                self.refreshRoomExits()
                self.currentRoom.set_image_for_display(self.image_label)
                self.image_label.config(image=self.currentRoom.photo_image)
                return  # Exit after processing the correct password
        
        # If no password matched, update the status to indicate failure
        self.status_label.config(text="Incorrect.", fg="red")


# Main window setup
root = Tk()
root.resizable(False, False)
root.title("Cryptic Hypnosis")
app = Game(root)
root.geometry("1000x600")
root.mainloop()