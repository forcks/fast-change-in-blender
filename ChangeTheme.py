import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.utils import register_class, unregister_class
from bpy.props import StringProperty,EnumProperty,IntProperty,PointerProperty
from bpy_extras.io_utils import ImportHelper
from os import listdir
from os import listdir
from os.path import isfile, join
import shutil
import os
import datetime
import json
from bpy.app.handlers import persistent


bl_info = {
    "name": "ChangeTheme",
    "description": "changing theme depending on time",
    "author": "Forcks",
    "version": (1, 0),
    "blender": (3,4,1),
    "location": "View3D > UI > set theme",
    "warning": "", 
    "doc_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "",
}

Themes = []
maxId = 0
dayTimeChangePre = False
dayTimeChangePost = False
isOnSetThemeByTimesOfDay = False
ThemeDirectory = os.path.join(os.path.join(os.environ['USERPROFILE']), 'blenderThemes')
statusDayNightTheme_ = "off"

dayTheme = ""
nightTheme = ""

start_time_h = 0
start_time_m = 0
end_time_h = 1
end_time_m = 0

startSettings = True

#saving variables to json file
def saveStatusToJson():
    dictJson = {"isOnSetThemeByTimesOfDay":isOnSetThemeByTimesOfDay,"dayTheme":dayTheme,"nightTheme":nightTheme,"start_time_h":start_time_h,"start_time_m":start_time_m,
                "end_time_h":end_time_h,"end_time_m":end_time_m,"dayTimeChangePre":dayTimeChangePre,"dayTimeChangePost":dayTimeChangePost,"statusDayNightTheme_":statusDayNightTheme_}
    json_x = json.dumps(dictJson)


    if not os.path.exists(ThemeDirectory +"\\json\\"):
        os.mkdir(ThemeDirectory +"\\json\\")

    my_file = open(ThemeDirectory +"\\json\\data_themes.json", "w")
    my_file.truncate()
    my_file.write(json_x)
    my_file.close()

#loading variables from json , is theme change enabled depending on time of day, daytime theme, time etc
def loadStatusToJson():
    if os.path.exists(ThemeDirectory +"\\json\\data_themes.json"):
        with open(ThemeDirectory +"\\json\\data_themes.json", "r") as my_file:
            status_json = my_file.read()
        status_theme = json.loads(status_json)
        global isOnSetThemeByTimesOfDay
        global dayTheme
        global nightTheme
        global start_time_h
        global start_time_m
        global end_time_h
        global end_time_m
        global dayTimeChangePre
        global dayTimeChangePost
        global statusDayNightTheme_

        isOnSetThemeByTimesOfDay = status_theme["isOnSetThemeByTimesOfDay"]
        dayTheme = status_theme["dayTheme"]
        nightTheme = status_theme["nightTheme"]
        start_time_h = status_theme["start_time_h"]
        start_time_m = status_theme["start_time_m"]
        end_time_h = status_theme["end_time_h"]
        end_time_m = status_theme["end_time_m"]
        dayTimeChangePre = status_theme["dayTimeChangePre"]
        dayTimeChangePost = status_theme["dayTimeChangePost"]
        statusDayNightTheme_ = status_theme["statusDayNightTheme_"]

#load variable value in ui
def loadUiVariables():
    bpy.context.scene.f_themes.startHour = start_time_h
    bpy.context.scene.f_themes.startMinutes = start_time_m
    bpy.context.scene.f_themes.EndHour = end_time_h
    bpy.context.scene.f_themes.EndMinutes = end_time_m
    bpy.context.scene.f_themes.statusDayNightTheme = statusDayNightTheme_
    
#check time of day, if day then true , if night then false
def dayTime():
    props = bpy.context.scene.f_themes
    now = datetime.datetime.now()
    start_time = datetime.time(props.startHour,props.startMinutes)
    end_time = datetime.time(props.EndHour,props.EndMinutes)


    global start_time_h
    global start_time_m
    global end_time_h
    global end_time_m

    start_time_h = props.startHour
    start_time_m = props.startMinutes
    end_time_h = props.EndHour
    end_time_m = props.EndMinutes
    
    global dayTimeChangePre 
    global dayTimeChangePost 
    
    print("now.time()",now.time())
    print("start",start_time)
    print("end",end_time)

    if start_time <= now.time() <= end_time:
        print("day")
        return False
    else:
        print("night")
        return True

def getTh(self, context):
    return Themes

class ThemesProps(PropertyGroup):
    path  : StringProperty(
        name="theme path",
        default='*.xml',
        subtype='FILE_PATH',
    )
    themes_list : EnumProperty(
        name="themes",
        items=getTh,
        description="some",
        update=getTh
    )
    startMinutes : IntProperty(
        name="min",
        default=1,
        min=0,
        max=59
    )
    startHour : IntProperty(
        name="hour",
        default=1,
        min=0,
        max=23
    )
    EndHour : IntProperty(
        name="hour",
        default=2,
        min=0,
        max=23
    )
    EndMinutes : IntProperty(
        name="min",
        default=2,
        min=0,
        max=59
    )
    themes_list_day : EnumProperty(
        name="day",
        items=getTh,
        description="some",
        update=getTh
    )
    themes_list_night : EnumProperty(
        name="night",
        items=getTh,
        description="some",
        update=getTh
    )
    statusDayNightTheme  : StringProperty(
        name="",
        default=statusDayNightTheme_,
    )

#adding a new theme to blender's themes folder
class AddNewTheme(Operator):
    bl_idname = "forks_space.add_new_theme"
    bl_label = "Add new theme"
    path = None
    def structure(self,context):
        props = context.scene.f_themes
        self.path = props.path

    def addTheme(self):
        try:
            global maxId
            original = self.path
            pathCopy = ThemeDirectory +"\\"+os.path.basename(original)
            shutil.copyfile(original, pathCopy)
            th = (str(maxId),os.path.basename(original),"")
            thExist = False
            for ths in Themes:
                if ths[1] == os.path.basename(original):
                    thExist = True
            if thExist == False:
                Themes.append(th)
                maxId += 1
            print(Themes)
        except:
            print("Enter correct path")
        
            
    def execute(self, context):
        self.structure(context)
        self.addTheme()
        return {"FINISHED"}

#set theme for blender
class SetThemes(Operator):
    bl_idname = "forks_space.set_theme"
    bl_label = "Set Themes"

    def structure(self,context):
        pass

    def setThemeExecute(self):
        if Themes:
            pathDir = ThemeDirectory + "\\"
            file = pathDir + Themes[int(bpy.context.scene.f_themes.themes_list)][1]
            file = file.replace("\\","\\\\")
            bpy.ops.script.execute_preset(filepath = file, menu_idname="USERPREF_MT_interface_theme_presets")
            
    def execute(self, context):
        self.structure(context)
        self.setThemeExecute()
        return {"FINISHED"}

#set the theme depending on the day once
def mathTimeAndChangeTheme():
    if isOnSetThemeByTimesOfDay:
        print(isOnSetThemeByTimesOfDay)
        if Themes:
            theme = ""
            if dayTime():
                theme = bpy.context.scene.f_themes.themes_list_day
            else:
                theme = bpy.context.scene.f_themes.themes_list_night

            file_th = ThemeDirectory +"\\"+ Themes[int(theme)][1]
            file_th = file_th.replace("\\","/")
            bpy.ops.script.execute_preset(filepath=file_th, menu_idname="USERPREF_MT_interface_theme_presets")

#periodically check for the time of day and if it changes then change the subject    
def mathTimeAndChangeThemePeriod():
    try:
        if isOnSetThemeByTimesOfDay:
            if Themes:
                global dayTimeChangePre
                global dayTimeChangePost
                dayTimeChangePre = dayTime()
                if dayTimeChangePre != dayTimeChangePost:
                    dayTimeChangePost = dayTimeChangePre
                    if dayTimeChangePost:
                        theme = bpy.context.scene.f_themes.themes_list_day
                    else:
                        theme = bpy.context.scene.f_themes.themes_list_night
                    file_th = ThemeDirectory +"\\"+ Themes[int(theme)][1]
                    file_th = file_th.replace("\\","\\\\")
                    bpy.ops.script.execute_preset(filepath=file_th, menu_idname="USERPREF_MT_interface_theme_presets")
    except:
        print("Error mathTimeAndChangeThemePeriod")

#enable or disable the function depending on the time of day
class SetThemeByTimesOfDay(Operator):
    bl_idname = "forks_space.set_theme_by_time_of_day"
    bl_label = "Set Themes By Time Of Day"


    def setThemeExecute(self):
        global isOnSetThemeByTimesOfDay
        global statusDayNightTheme_
        if not isOnSetThemeByTimesOfDay:
            isOnSetThemeByTimesOfDay = True
            mathTimeAndChangeTheme()
            statusDayNightTheme_ = "on"
        else:
            isOnSetThemeByTimesOfDay = False
            statusDayNightTheme_ = "off"
        print("isOnSetThemeByTimesOfDay = ",isOnSetThemeByTimesOfDay)

        global dayTheme
        global nightTheme
        dayTheme = Themes[int(bpy.context.scene.f_themes.themes_list_day)][1]
        nightTheme = Themes[int(bpy.context.scene.f_themes.themes_list_night)][1]

        saveStatusToJson()

    def execute(self, context):
        self.setThemeExecute()
        return {"FINISHED"}


    

class OBJECT_PT_SetThemes(Panel):
    bl_label = "set theme"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "set theme"

    def draw(self, context):
        layout = self.layout
        props = context.scene.f_themes
        col = layout.column()
        col.prop(props, "path")
        spl = col.split(align=True)
        col.operator("forks_space.add_new_theme")
        spl = col.split()
        spl.prop(props, "themes_list")
        spl = col.split()
        col.operator("forks_space.set_theme")
        spl = col.split(align=True)
        spl.label(text="start night theme")
        spl = col.split(align=True)
        spl.prop(props, "startHour")
        spl.prop(props, "startMinutes")
        spl = col.split(align=True)
        spl.label(text="end night theme")
        spl = col.split(align=True)
        spl.prop(props, "EndHour")
        spl.prop(props, "EndMinutes")
        spl = col.split(align=True)
        spl.prop(props, "themes_list_day")
        spl.prop(props, "themes_list_night")
        spl = col.split(align=True)
        spl.operator("forks_space.set_theme_by_time_of_day")
        spl.label(text=statusDayNightTheme_)

        
        

        

classes = [
    ThemesProps,
    AddNewTheme,
    SetThemes,
    SetThemeByTimesOfDay,
    OBJECT_PT_SetThemes
]

def register():
    for cl in classes:
        register_class(cl)
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_callback)
    bpy.types.Scene.f_themes = PointerProperty(type=ThemesProps)

def unregister():
    for cl in reversed(classes):
        unregister_class(cl)

    del bpy.types.Scene.f_themes

def startSetup():
    global startSettings
    if startSettings:
        loadStatusToJson()
        loadThemes()
        startSettings = False


@persistent
def depsgraph_callback(scene, depsgraph):
    if not os.path.exists(ThemeDirectory):
            print("create folder")
            os.mkdir(ThemeDirectory)
    print(ThemeDirectory)
    startSetup()
    mathTimeAndChangeThemePeriod()
    

        
def loadThemes():
    print(ThemeDirectory)
    onlyfiles = [f for f in listdir(ThemeDirectory) if isfile(join(ThemeDirectory, f))]
    i = 0
    for file in onlyfiles:
        th = (str(i),file,"")
        print(th)        
        Themes.append(th)
        if dayTheme == file:
            bpy.context.scene.f_themes.themes_list_day = str(i)
        elif nightTheme == file:
            bpy.context.scene.f_themes.themes_list_night = str(i)
        i+=1
    global maxId
    maxId = i
    loadUiVariables()
    mathTimeAndChangeTheme()

def main():
    register()
            
            
    


if __name__ == '__main__':
    main()
        