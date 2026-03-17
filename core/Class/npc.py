class Npc:
    def __init__(self, attached_gui, dialogues: list, pos: tuple):
        self.gui = attached_gui
        self.dialogues = dialogues
        self.pos = pos
        self.recruited = False