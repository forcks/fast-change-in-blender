import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.utils import register_class, unregister_class
from bpy.props import StringProperty,EnumProperty,IntProperty,BoolProperty,PointerProperty
from bpy_extras.io_utils import ImportHelper
from os import listdir
from os import listdir
from os.path import isfile, join
import shutil
import os
import time
import threading
import datetime

Themes = []
maxId = 0
dayTimeChangePre = False
dayTimeChangePost = False
isOnSetThemeByTimesOfDay = False

def dayTime():
    now = datetime.datetime.now()
    StartTime = [9,0]
    EndTime = [23,0]
    start_time = datetime.time(StartTime[0], StartTime[1])
    end_time = datetime.time(EndTime[0], EndTime[1])
    
    global dayTimeChangePre 
    global dayTimeChangePost 

    if start_time <= now.time() <= end_time:
        print("day")
        return True
    else:
        print("night")
        return False

def mathTimeAndChangeTheme():
    pathDir = bpy.utils.resource_path('USER') + "\\scripts\\presets\\interface_theme\\"
    theme = ""
    if dayTime():
        #theme = bpy.context.object.f_themes.themes_list_day
        print(bpy.context.object.f_themes.themes_list_night)
    else:
        theme = bpy.context.object.f_themes.themes_list_night
    file = pathDir + Themes[int(theme)][1]
    file = file.replace("\\","\\\\")
    bpy.ops.script.execute_preset(filepath = file, menu_idname="USERPREF_MT_interface_theme_presets")

    while isOnSetThemeByTimesOfDay:
        dayTimeChangePre = dayTime()

        if dayTimeChangePre != dayTimeChangePost:
            dayTimeChangePost = dayTimeChangePre
            if dayTimeChangePost:
                theme = bpy.context.object.f_themes.themes_list_day
            else:
                theme = bpy.context.object.f_themes.themes_list_night
            file = pathDir + Themes[int(theme)][1]
            file = file.replace("\\","\\\\")
            bpy.ops.script.execute_preset(filepath = file, menu_idname="USERPREF_MT_interface_theme_presets")
            
            
        time.sleep(5)




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
    startHour : IntProperty(
        name="start hour",
        default=6,
        min=0,
        max=59
    )
    startMinutes : IntProperty(
        name="start minutes",
        default=0,
        min=0,
        max=59
    )
    EndHour : IntProperty(
        name="end hour",
        default=21,
        min=0,
        max=24
    )
    EndMinutes : IntProperty(
        name="end minutes",
        default=0,
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

    
        
    
class AddNewTheme(Operator):
    bl_idname = "forks_space.add_new_theme"
    bl_label = "Add new theme"
    path = None
    def structure(self,context):
        props = context.object.f_themes
        self.path = props.path

    def addTheme(self):
        global maxId
        original = self.path
        pathCopy = bpy.utils.resource_path('USER') + "\\scripts\\presets\\interface_theme\\"+os.path.basename(original)
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
        
            
    def execute(self, context):
        self.structure(context)
        self.addTheme()
        return {"FINISHED"}

class SetThemes(Operator):
    bl_idname = "forks_space.set_theme"
    bl_label = "Set Themes"

    def structure(self,context):
        pass

    def setThemeExecute(self):
        pathDir = bpy.utils.resource_path('USER') + "\\scripts\\presets\\interface_theme\\"
        file = pathDir + Themes[int(bpy.context.object.f_themes.themes_list)][1]
        file = file.replace("\\","\\\\")
        bpy.ops.script.execute_preset(filepath = file, menu_idname="USERPREF_MT_interface_theme_presets")
            
    def execute(self, context):
        self.structure(context)
        self.setThemeExecute()
        return {"FINISHED"}

t2 = threading.Thread(target=mathTimeAndChangeTheme)
class SetThemeByTimesOfDay(Operator):
    bl_idname = "forks_space.set_theme_by_time_of_day"
    bl_label = "Set Themes By Time Of Day"

    def structure(self,context):
        pass

    def setThemeExecute(self):
        global isOnSetThemeByTimesOfDay
        if not isOnSetThemeByTimesOfDay:
            isOnSetThemeByTimesOfDay = True
            t2.start()
        else:
            isOnSetThemeByTimesOfDay = False


        #bpy.ops.script.execute_preset(filepath = file, menu_idname="USERPREF_MT_interface_theme_presets")
            
    def execute(self, context):
        self.structure(context)
        self.setThemeExecute()
        return {"FINISHED"}


    

class OBJECT_PT_SetThemes(Panel):
    bl_label = "set theme"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "set theme"

    def draw(self, context):
        layout = self.layout
        props = context.object.f_themes
        col = layout.column()
        col.prop(props, "path")
        spl = col.split(align=True)
        col.operator("forks_space.add_new_theme")
        spl = col.split()
        spl.prop(props, "themes_list")
        spl = col.split()
        col.operator("forks_space.set_theme")
        spl = col.split(align=True)
        spl.prop(props, "startHour")
        spl.prop(props, "startMinutes")
        spl = col.split(align=True)
        spl.prop(props, "EndHour")
        spl.prop(props, "EndMinutes")
        spl = col.split(align=True)
        spl.prop(props, "themes_list_day")
        spl.prop(props, "themes_list_night")
        spl = col.split(align=True)
        col.operator("forks_space.set_theme_by_time_of_day")
        
        

        

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
    bpy.types.Object.f_themes = PointerProperty(type=ThemesProps)

def unregister():
    for cl in reversed(classes):
        unregister_class(cl)
    del bpy.types.Object.f_themes

        
def main():
    pathDir = bpy.utils.resource_path('USER') + "\\scripts\\presets\\interface_theme\\"
    onlyfiles = [f for f in listdir(pathDir) if isfile(join(pathDir, f))]
    i = 0
    for file in onlyfiles:
        th = (str(i),file,"")
        print(th)        
        Themes.append(th)
        i+=1
    maxId = i
    


    register()



if __name__ == '__main__':
    #asyncio.run(main())
    t1 = threading.Thread(target=main)
    t1.run()
    #t2 = threading.Timer(mathTimeAndChangeTheme)
    #t2.start()
    