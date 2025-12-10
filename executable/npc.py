class Npc:
    def __init__(self, dialogues: list, attached_gui, position: tuple):
        self.gui = attached_gui
        self.dialogues = dialogues
        self.position = position
        self.recruited = False
