"""Optional F3 operators. No panels or keymap overrides cover the cinema."""
import bpy

class GANESHA_OT_restart(bpy.types.Operator):
    bl_idname='ganesha.restart'; bl_label='Ganesha: Restart Manifestation'
    def execute(self,context):
        context.scene.frame_set(1)
        if not context.screen.is_animation_playing: bpy.ops.screen.animation_play()
        return {'FINISHED'}

class GANESHA_OT_speed(bpy.types.Operator):
    bl_idname='ganesha.speed'; bl_label='Ganesha: Set Playback Speed'
    multiplier: bpy.props.FloatProperty(name='Speed multiplier',default=1,min=.25,max=4)
    def invoke(self,context,event): return context.window_manager.invoke_props_dialog(self)
    def execute(self,context):
        context.scene.render.fps_base=1/self.multiplier
        return {'FINISHED'}

class GANESHA_OT_toggle(bpy.types.Operator):
    bl_idname='ganesha.toggle_layer'; bl_label='Ganesha: Toggle Cosmic Layer'
    layer: bpy.props.EnumProperty(name='Layer',items=[(n,n,'') for n in ('Stars','Galaxies','Nebula','Halo')])
    def invoke(self,context,event): return context.window_manager.invoke_props_dialog(self)
    def execute(self,context):
        col=context.scene.collection.children.get(self.layer)
        if col:
            col.hide_viewport=not col.hide_viewport; col.hide_render=col.hide_viewport
        return {'FINISHED'}

def register():
    for cls in (GANESHA_OT_restart,GANESHA_OT_speed,GANESHA_OT_toggle):
        if not hasattr(bpy.types,cls.__name__): bpy.utils.register_class(cls)

def prepare_view(scene):
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                space=area.spaces.active
                space.region_3d.view_perspective='CAMERA'
                space.region_3d.view_camera_zoom=20
                space.show_region_toolbar=False
                space.show_region_ui=False
                space.overlay.show_overlays=False
                space.show_gizmo=False
                space.shading.type='RENDERED'
                space.shading.use_scene_world_render=True
                space.shading.use_scene_lights_render=True
                space.shading.use_compositor='CAMERA'
    scene.sync_mode='FRAME_DROP'

def cinema_view():
    """Maximize only this session's viewport; Ctrl+Space restores editors."""
    area=next((a for a in bpy.context.screen.areas if a.type=='VIEW_3D'),None)
    if area:
        with bpy.context.temp_override(area=area):
            bpy.ops.screen.screen_full_area(use_hide_panels=True)
