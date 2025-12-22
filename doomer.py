# DOOMer v0.1.4
# 2025-11-04

import os
import json
import subprocess

from textual import on
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Grid, Container, Horizontal, VerticalScroll, HorizontalScroll
from textual.widgets import Button, Static, TabbedContent, TabPane


###File handling
#directory of WADs. Each WAD should be in own directory. Directory names server as button labels
DIR = "/Users/alex/doom/WADS/"
USER_DIR = ""
#valid filetypes for running WADs
FILETYPE = [".wad", ".WAD", ".Wad", ".deh", ".DEH"]
#misc 
TITLE = "DOOMer"

#Lists to break up WADs by IWAD. Excluding DOOM2 WADs, each WAD must be added here.
DOOM = ["DOOM", "SIGIL", "SIGIL_II"]
TNT_WADS = ["TNT", "TNT_Revilution"]
PLUTONIA = ["Plutonia", "Plutonia_2"]
HERETIC = ["Heretic", "Hexen"]
#IWADs/Retail Games
IWADS = ["DOOM", "DOOM 2", "TNT", "Plutonia", "Heretic", "Hexen"]
##scans base dir for folders starting with '_' and looks for IWAD files
IWADS_GEN = [f.name for f in os.scandir(DIR) if f.is_dir() and f.name.startswith("_")]


def get_source_port_ver(self) -> None:
    #runs subprocess to get current version of 'source port' installed
    text = subprocess.run(['dsda-doom', '-v'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    output = text[:18] #formats output down to just sourceport name and version
    return output

#scans "DIR" for WAD folders and sorts alphabetically 
wad_names = [f.name for f in os.scandir(DIR) if f.is_dir() and not f.name.startswith("_")]
wad_names.sort()

def is_wad(file):   #checks files in WAD directory to match against "FILETYPE" above
    filename, extension = os.path.splitext(file)
    return extension in FILETYPE


#Builds vertical column of buttons for DOOM WADs       
class Doom(VerticalScroll):
        
    def compose(self) -> ComposeResult:
        wad_count = 0
        with VerticalScroll(id="WADs-container"):
            with Grid(id="WADs-grid"):
                for x in DOOM:
                    yield Button(x, id=x, classes="doom", tooltip=x)
                    wad_count += 1
        self.border_title = f"DOOM - {wad_count} WADs"
        self.border_subtitle = f"DOOM  - {wad_count} WADs"


#Builds vertical column of buttons for DOOM2 WADs
class Doom2(ScrollableContainer):
        
    def compose(self) -> ComposeResult:
        exclude_list = DOOM + TNT_WADS + PLUTONIA + HERETIC
        exclude_set = set(exclude_list)
        doom2_wads = [name for name in wad_names if name not in exclude_set]
        wad_count = 0

        with VerticalScroll(id="WADs-container"):
            with Grid(id="WADs-grid"):
                for x in doom2_wads:
                #   y = x[:14] + (x[14:] and '..') #reduces WAD name to less than 14 characters
                    y = x.replace("_", " ")
                    yield Button(y, id=x, classes=f"doom2", tooltip=x)
                    wad_count += 1
        self.border_title = f"DOOM2 - {wad_count} WADs"
        self.border_subtitle = f"DOOM2  - {wad_count} WADs"


#Builds vertical column of buttons for TNT WADs
class TNT(VerticalScroll):
        
    def compose(self) -> ComposeResult:
        wad_count = 0
        with VerticalScroll(id="WADs-container"):
            with Grid(id="WADs-grid"):
                for x in TNT_WADS:
                    yield Button(x, id=x, classes="tnt", tooltip=x)
                    wad_count += 1
        self.border_title = f"TNT - {wad_count} WADs"
        self.border_subtitle = f"TNT - {wad_count} WADs"



#Builds vertical column of buttons for Plutonia WADs
class Plutonia(VerticalScroll):

    def compose(self) -> ComposeResult:
        wad_count = 0
        with VerticalScroll(id="WADs-container"):
            with Grid(id="WADs-grid"):
                for x in PLUTONIA:
                    yield Button(x, id=x, classes="plutonia", tooltip=x)
                    wad_count += 1
        self.border_title = f"Plutonia - {wad_count} WADs"
        self.border_subtitle = f"Plutonia  - {wad_count} WADs"


#Builds vertical column of buttons for Heretic WADs
class Heretic(VerticalScroll):
    def on_mount(self) -> None:
        self.border_title = "Heretic/Hexen"
        self.border_subtitle = "Heretic/Hexen"
        
    def compose(self) -> ComposeResult:
        with VerticalScroll(id="WADs-container"):
            with Grid(id="WADs-grid"):
                for x in HERETIC:
                    yield Button(x, id=x, classes="heretic", tooltip=x)


class Doomer(App):
    CSS_PATH = "static/css_doomer.tcss"

    
    def compose(self) -> ComposeResult:
        with TabbedContent(initial="doom2"):
            with TabPane("DOOM", id="doom"):
                yield Doom()
            with TabPane("DOOM2", id="doom2"):
                yield Doom2()
            with TabPane("TNT", id="tnt"):
                yield TNT()
            with TabPane("Plutonia", id="plutonia"):
                yield Plutonia()
            with TabPane("Heretic/Hexen", id="heretic"):
                yield Heretic()
        with Container(id="command_out"):
            yield Static("Select WAD to play", id="command")
            yield Static(get_source_port_ver(self))
            # yield Input(placeholder=DIR, id="user_dir")
            with Horizontal():
                yield Button("Play", id="play_button", variant="success", disabled=True)
                yield Button("Quit", id="quit", variant="error")


    @on(Button.Pressed, "#quit")
    def quit(self, event: Button.Pressed) -> None:
        self.exit()


    @on(Button.Pressed, "#play_button")
    def launch(self):
        os.system(self.output_run)


    @on(Button.Pressed, ".doom")
    def run_doom(self, event: Button.Pressed) -> None:
        self.wad = event.button.id
        self.wad_dir = f"{DIR}{self.wad}"
        self.wad_command = ""

        wad_file = [file for file in os.listdir(self.wad_dir) if is_wad(file)]
        for wad in wad_file:
            self.wad_command += f" {self.wad_dir}/{wad}"
        
        iwad_command = "dsda-doom -iwad /Users/alex/doom/WADS/DOOM/doom.wad -file"
        self.output_run = f"{iwad_command}{self.wad_command}"
        # os.system(f"{self.output_run}")
        button = self.query_one("#play_button")
        button.disabled = False
        label = self.query_one("#command")
        label.update(f"WAD: {self.wad}")


    @on(Button.Pressed, ".doom2")
    def run_doom2(self, event: Button.Pressed) -> None:
        self.wad = event.button.id
        self.wad_dir = f"{DIR}{self.wad}"
        self.wad_command = ""

        wad_file = [file for file in os.listdir(self.wad_dir) if is_wad(file)]
        for wad in wad_file:
            self.wad_command += f" {self.wad_dir}/{wad}"
        
        iwad_command = "dsda-doom -iwad /Users/alex/doom/WADS/DOOM2/doom2.wad -file"
        self.output_run = f"{iwad_command}{self.wad_command}"
        button = self.query_one("#play_button")
        button.disabled = False
        label = self.query_one("#command")
        label.update(f"WAD: {self.wad}")


    @on(Button.Pressed, ".tnt")
    def run_tnt(self, event: Button.Pressed) -> None:
        self.wad = event.button.id
        self.wad_dir = f"{DIR}{self.wad}"
        self.wad_command = ""

        wad_file = [file for file in os.listdir(self.wad_dir) if is_wad(file)]
        for wad in wad_file:
            self.wad_command += f" {self.wad_dir}/{wad}"
        
        iwad_command = "dsda-doom -iwad /Users/alex/doom/WADS/TNT/tnt.wad -file"
        self.output_run = f"{iwad_command}{self.wad_command}"
        button = self.query_one("#play_button")
        button.disabled = False
        label = self.query_one("#command")
        label.update(f"WAD: {self.wad}")


    @on(Button.Pressed, ".plutonia")
    def run_plutonia(self, event: Button.Pressed) -> None:
        self.wad = event.button.id
        self.wad_dir = f"{DIR}{self.wad}"
        self.wad_command = ""

        wad_file = [file for file in os.listdir(self.wad_dir) if is_wad(file)]
        for wad in wad_file:
            self.wad_command += f" {self.wad_dir}/{wad}"
        
        iwad_command = "dsda-doom -iwad /Users/alex/doom/WADS/Plutonia/plutonia.wad -file"
        self.output_run = f"{iwad_command}{self.wad_command}"
        button = self.query_one("#play_button")
        button.disabled = False
        label = self.query_one("#command")
        label.update(f"WAD: {self.wad}")

    
    @on(Button.Pressed, ".heretic")
    def run_heretic(self, event: Button.Pressed) -> None:
        self.wad = event.button.id
        self.wad_dir = f"{DIR}{self.wad}"
        self.wad_command = ""

        wad_file = [file for file in os.listdir(self.wad_dir) if is_wad(file)]
        for wad in wad_file:
            self.wad_command += f" {self.wad_dir}/{wad}"
        
        if self.wad == "Heretic":
            iwad_command = f"dsda-doom -iwad /Users/alex/doom/WADS/Heretic/heretic.wad -file"
        else:
            iwad_command = f"dsda-doom -iwad /Users/alex/doom/WADS/Hexen/hexen.wad -file"
        self.output_run = f"{iwad_command}{self.wad_command}"
        button = self.query_one("#play_button")
        button.disabled = False
        label = self.query_one("#command")
        label.update(f"WAD: {self.wad}")


if __name__ == "__main__":
    app = Doomer()
    app.run()
