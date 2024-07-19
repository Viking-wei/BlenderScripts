import bpy
import json
import string
import mathutils

from bpy.types import Context

origin_path = "D:/BlenderAddOne/BlenderSource/NamePattern.json"
readabledata_1 = {}
readabledata_2 = {}
readabledata_3 = {}
final_name = ""
model_final_name = ""

def initialize_data(path=origin_path):
    global readabledata_1,readabledata_2,readabledata_3
    raw_data = prepare_json(path)
    readabledata_1 = get_readable_dict(raw_data)
    readabledata_2 = readabledata_1[list(readabledata_1.keys())[0]]
    readabledata_3 = readabledata_2[list(readabledata_2.keys())[0]]

def prepare_json(path):
    with open(path, 'r',encoding='utf-8') as f:
        data = json.load(f)
        return data[0]['topic']['topics']
    
def get_readable_dict(data):
    if data is None:
        return ' '
    result = {}
    for sub_data in data:
        if 'topics' not in sub_data:
            result[sub_data['title']] = get_readable_dict(None)
            continue
        result[sub_data['title']] = get_readable_dict(sub_data['topics'])
    return result

def get_world_bounds(obj):
    local_bbox_corners = [mathutils.Vector(corner) for corner in obj.bound_box]
    world_bbox_corners = [obj.matrix_world @ corner for corner in local_bbox_corners]
    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')
    for corner in world_bbox_corners:
        if corner.x < min_x:
            min_x = corner.x
        if corner.y < min_y:
            min_y = corner.y
        if corner.z < min_z:
            min_z = corner.z
        if corner.x > max_x:
            max_x = corner.x
        if corner.y > max_y:
            max_y = corner.y
        if corner.z > max_z:
            max_z = corner.z
    return (min_x, min_y, min_z), (max_x, max_y, max_z)

def name_list_callback_1(self, context):
    title_list = list(readabledata_1.keys())
    items = []
    for title in title_list:
        item=(title,title,"")
        items.append(item)
    return items 

def name_list_callback_2(self, context):
    title_list = list(readabledata_2.keys())
    items = []
    for title in title_list:
        item=(title,title,"")
        items.append(item)
    return items 

def name_list_callback_3(self, context):
    title_list = list(readabledata_3.keys())
    items = []
    for title in title_list:
        item=(title,title,"")
        items.append(item)
    return items 

def name_list_callback_4(self, context):
    letters = list(string.ascii_uppercase)
    letter_list =  [(letter, letter, ' ') for letter in letters]
    return letter_list

def name_list_callback_5(self, context):
    numbers = [f"{i:02}" for i in range(1, 10)]
    number_list = [(num, num, ' ') for num in numbers]
    return number_list

def path_update(self, context):
    initialize_data(self.file_path)

def layer_1_update(self, context):
    global readabledata_2
    readabledata_2=readabledata_1[self.layer_1]
    layer_list = list(readabledata_2.keys())
    if self.layer_2 not in layer_list:
        self.layer_2=layer_list[0]
    layer_2_update(self, context)

def layer_2_update(self, context):
    global readabledata_3
    readabledata_3=readabledata_2[self.layer_2]
    layer_list = list(readabledata_3.keys())
    if self.layer_3 not in layer_list:
        self.layer_3=layer_list[0]
    final_name_update(self, context)

def final_name_update(self, context):
    global final_name
    props=context.scene.utilites_props
    final_name=props.layer_2.split('_')[0]+'_'+props.layer_3.split('_')[0]+'_'+props.layer_4+'_'+props.layer_5
    props.name_text=final_name

def get_origin_pos(ward_list,min_bound,max_bound):
    ward_dict={'上':1,'中':0.5,'下':0, '左':0, '右':1, '前':0, '后':1}
    pos_arg=[ward_dict[ward] for ward in ward_list]
    return [(max_bound[i]-min_bound[i])*pos_arg[i]+min_bound[i] for i in range(3)]
    
def set_origin_pos(obj,ward_list,cursor):
    min_bound,max_bound=get_world_bounds(obj)
    origin_pos=get_origin_pos(ward_list,min_bound,max_bound)
    cursor.location = (origin_pos[0],origin_pos[1],origin_pos[2])
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

def remove_dot(name):
    return name.split('.')[0]

def json_layer_1_update(self, context):
    global readabledata_2
    readabledata_2=readabledata_1[self.json_layer_1]
    layer_list = list(readabledata_2.keys())
    if self.json_layer_2 not in layer_list:
        self.json_layer_2=layer_list[0]
    json_layer_2_update(self, context)

def json_layer_2_update(self, context):
    global readabledata_3
    readabledata_3=readabledata_2[self.json_layer_2]
    layer_list = list(readabledata_3.keys())
    if self.json_layer_3 not in layer_list:
        self.json_layer_3 = layer_list[0]
    json_model_name_update(self, context)

def json_model_name_update(self, context):
    global model_final_name
    props=context.scene.utilites_props
    json_layer_2_name=props.json_layer_2.split('_')[0]
    json_layer_3_name=props.json_layer_3.split('_')[0]
    model_final_name=f'{json_layer_2_name}_{json_layer_3_name}_{props.json_layer_4}_{props.json_layer_5}_{props.json_layer_6}'
    props.template_name=model_final_name

class RenameButton(bpy.types.Operator):
    global final_name
    bl_idname = "wm.rename"
    bl_label = "rename"
    def execute(self, context):
        selected_objects = context.selected_objects
        all_objects = context.scene.objects

        if len(selected_objects)==0:
            return {'FINISHED'}
        first_selected_object = selected_objects[0]
        if not context.scene.utilites_props.sync_name:
            first_selected_object.name=final_name
            return {'FINISHED'}
        
        matching_objects = [obj for obj in all_objects if obj.name.split('.')[0] == first_selected_object.name.split('.')[0]]
        for obj in matching_objects:
            obj.name=final_name
        return {'FINISHED'}
    

class SetOriginButton(bpy.types.Operator):
    bl_idname = "wm.set_origin"
    bl_label = "set_origin"
    def execute(self, context):
        if len(context.selected_objects)==0:
            return {'FINISHED'}
        ult_props=context.scene.utilites_props
        ward_list=[ult_props.left_right,ult_props.forword_back,ult_props.up_down]
        first_selected_object = context.selected_objects[0]
        all_objects = context.scene.objects
        cursor=context.scene.cursor
        if ult_props.sync_origin:
            same_name_objects = [obj for obj in all_objects if obj.name.split('.')[0] == first_selected_object.name.split('.')[0]]
            for obj in same_name_objects:
                set_origin_pos(obj,ward_list,cursor)
            return {'FINISHED'}
        set_origin_pos(first_selected_object,ward_list,cursor)
        return {'FINISHED'}
    

class CreateColletionButton(bpy.types.Operator):
    bl_idname = "wm.create_collection"
    bl_label = "create_collection"
    def execute(self, context):
        all_objects = context.selected_objects
        if len(all_objects)==0:
            self.report({'ERROR'}, "需要选中至少一个物体！")
            return {'FINISHED'}
        collection_name=context.scene.utilites_props.template_name
        new_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(new_collection)
        for obj in all_objects:
            if obj.type=='MESH':
                if context.scene.utilites_props.instance:
                    bpy.ops.object.select_all(action='DESELECT')
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.duplicate(linked=False,mode='TRANSLATION')
                    new_obj=context.selected_objects[0]
                    new_collection.objects.link(new_obj)
                else:
                    for collection in obj.users_collection:
                        collection.objects.unlink(obj)
                    new_collection.objects.link(obj)
        return {'FINISHED'}
    

class ExportJsonButton(bpy.types.Operator):
    bl_idname = "wm.export_json"
    bl_label = "export_json"
    def execute(self, context):
        print(bpy.context.collection.name)
        all_objects_in_collecton=bpy.context.collection.all_objects
        list_of_objects=[]
        for obj in all_objects_in_collecton:
            if obj.type=='MESH':
                obj_info={}
                obj_info['name']=remove_dot(obj.name)
                obj_info['position']=[obj.location.x,obj.location.y,obj.location.z]
                obj_info['rotation']=[obj.rotation_euler.x,obj.rotation_euler.y,obj.rotation_euler.z]
                list_of_objects.append(obj_info)
        json_str=json.dumps(list_of_objects,indent=4)
        print(json_str)
        return {'FINISHED'}
    

class ShowJsonButton(bpy.types.Operator):
    bl_idname = "wm.show_json"
    bl_label = "show_json"
    def execute(self, context):
        all_objects = context.selected_objects
        return {'FINISHED'}
    

class ExportFBXButton(bpy.types.Operator):
    bl_idname = "wm.export_fbx"
    bl_label = "export_fbx"
    def execute(self, context):
        if len(context.selected_objects)==0:
            return {'FINISHED'}
        first_selected_object = context.selected_objects[0]
        suffix = '.fbx'
        final_path=f'{context.scene.utilites_props.fbx_export_path}{remove_dot(first_selected_object.name)}{suffix}'
        bpy.ops.export_scene.fbx(filepath=final_path,use_selection=True)
        return {'FINISHED'}


class UtilitiesPropertes(bpy.types.PropertyGroup):
    file_path: bpy.props.StringProperty(
        name="文件路径",
        subtype='FILE_PATH',
        update=path_update,
    )
    layer_1: bpy.props.EnumProperty(   
        name="命名列表",
        items=name_list_callback_1,
        update=layer_1_update,
    )
    layer_2: bpy.props.EnumProperty(
        name="",
        items=name_list_callback_2,
        update=layer_2_update,
    )
    layer_3: bpy.props.EnumProperty(
        name="",
        items=name_list_callback_3,
        update=final_name_update,
    )
    layer_4: bpy.props.EnumProperty(
        name="",
        items=name_list_callback_4,
        update=final_name_update,
    )
    layer_5: bpy.props.EnumProperty(
        name="",
        items=name_list_callback_5,
        update=final_name_update,
    )
    sync_name: bpy.props.BoolProperty(default=False)
    name_text: bpy.props.StringProperty(default="")

    up_down: bpy.props.EnumProperty(
        name="上下",
        items=[('上', '上', ''),('中', '中', ''),('下', '下', '')],
    )
    left_right: bpy.props.EnumProperty(
        name="左右",
        items=[('左', '左', ''),('中', '中', ''),('右', '右', '')],
    )
    forword_back: bpy.props.EnumProperty(
        name="前后",
        items=[('前', '前', ''),('中', '中', ''),('后', '后', '')],
    )
    sync_origin: bpy.props.BoolProperty(default=False)

    fbx_export_path: bpy.props.StringProperty(
        name="导出路径",
        subtype='FILE_PATH',
    )

    json_layer_1: bpy.props.EnumProperty(   
        name="命名列表",
        items=name_list_callback_1,
        update=json_layer_1_update,
    )
    json_layer_2: bpy.props.EnumProperty(   
        name="",
        items=name_list_callback_2,
        update=json_layer_2_update,
    )
    json_layer_3: bpy.props.EnumProperty(   
        name="",
        items=name_list_callback_3,
        update=json_model_name_update,
    )
    json_layer_4: bpy.props.EnumProperty(   
        name="",
        items=name_list_callback_4,
        update=json_model_name_update,
    )
    json_layer_5: bpy.props.EnumProperty(   
        name="",
        items=name_list_callback_5,
        update=json_model_name_update,
    )
    json_layer_6: bpy.props.EnumProperty(   
        name="",
        items=[('v1', 'v1', ''),('v2', 'v2', ''),('v3', 'v3', ''),('v4', 'v4', ''),('v5', 'v5', '')],
        update=json_model_name_update,
    )
    variant: bpy.props.BoolProperty(default=False)
    instance: bpy.props.BoolProperty(default=False)
    template_name: bpy.props.StringProperty(default="")


class RenamePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_Rename"
    bl_label = "批量重命名"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'   
    bl_category = '实用小工具'

    def draw(self, context):
        col_layout = self.layout.column()
        row_layout = col_layout.row()
        reporps=context.scene.utilites_props
        col_layout.prop(reporps, "file_path")
        row_layout.prop(reporps, "layer_1") 
        row_layout.prop(reporps, "layer_2")
        row_layout.prop(reporps, "layer_3")
        row_layout.prop(reporps, "layer_4")
        row_layout.prop(reporps, "layer_5")
        col_layout.prop(reporps,"sync_name",text="同步所有同名对象")
        col_layout.prop(reporps,"name_text",text="最终名字")
        col_layout.operator("wm.rename",text="重命名")


class SetOriginPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_set_origin"
    bl_label = "设置轴心点"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'   
    bl_category = '实用小工具'

    def draw(self, context):
        col_layout = self.layout.column()
        row_layout = col_layout.row()
        porps=context.scene.utilites_props
        row_layout.prop(porps, "up_down")
        row_layout.prop(porps, "left_right")
        row_layout.prop(porps, "forword_back")
        col_layout.prop(porps, "sync_origin",text='同步设置所有同名对象')
        col_layout.operator("wm.set_origin",text="修改轴心点")


class FBXExportPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_fbx_export"
    bl_label = "导出FBX"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'   
    bl_category = '实用小工具'

    def draw(self, context):
        col_layout = self.layout.column()
        row_layout = col_layout.row()
        porps=context.scene.utilites_props
        row_layout.label(text='导出物体信息：')
        show_info='None'
        face_count=0
        if len(context.selected_objects) != 0:
            show_info=remove_dot(context.selected_objects[0].name)
            for obj in context.selected_objects:
                if obj.type=='MESH':
                    face_count+=len(context.selected_objects[0].data.polygons)
        row_layout.label(text=f'{show_info}  面数：{face_count}')
        col_layout.label(text='导出单位: m ')
        col_layout.prop(porps, "fbx_export_path")
        col_layout.operator("wm.export_fbx",text="导出FBX")


class JsonExportPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_json_export"
    bl_label = "导出Json"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'   
    bl_category = '实用小工具'

    def draw(self, context):
        col_layout = self.layout.column()
        row_layout = col_layout.row()
        reporps=context.scene.utilites_props
        row_layout.prop(reporps, "json_layer_1") 
        row_layout.prop(reporps, "json_layer_2")
        row_layout.prop(reporps, "json_layer_3") 
        row_layout.prop(reporps, "json_layer_4")
        row_layout.prop(reporps, "json_layer_5")
        row_layout.prop(reporps, "json_layer_6")
        col_layout.prop(reporps,"variant",text="是否有变体")
        col_layout.prop(reporps,"instance",text="以新建物体的方式创建")
        col_layout.prop(reporps,"template_name",text="模板命名")
        col_layout.operator("wm.create_collection",text="创建Collection")
        col_layout.label(text='D:/BlenderAddOne/BlenderSource/NamePattern.json')
        col_layout.operator("wm.export_json",text="导出Json")
        col_layout.operator("wm.show_json",text="查看Json")


blender_classes = [RenameButton,RenamePanel,UtilitiesPropertes,SetOriginPanel,SetOriginButton,ExportFBXButton,FBXExportPanel,JsonExportPanel,ExportJsonButton,ShowJsonButton,CreateColletionButton]

def register():
    initialize_data()
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)
    bpy.types.Scene.utilites_props = bpy.props.PointerProperty(type=UtilitiesPropertes)

def unregister():
    del bpy.types.Scene.utilites_props
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)

