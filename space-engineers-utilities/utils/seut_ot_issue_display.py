import bpy
import time
import textwrap

from bpy.types              import Operator
from bpy.props              import StringProperty


class SEUT_OT_IssueDisplay(Operator):
    """Displays a list of the last 10 notifications originating from SEUT"""
    bl_idname = "wm.issue_display"
    bl_label = "SEUT Notifications"
    bl_options = {'REGISTER', 'UNDO'}


    issues_sorted = []


    def execute(self, context):

        wm = context.window_manager
        
        SEUT_OT_IssueDisplay.issues_sorted.clear()
        SEUT_OT_IssueDisplay.issues_sorted = sorted(wm.seut.issues, key=lambda issue: issue.timestamp)
        
        wm.seut.issue_alert = False
        
        return context.window_manager.invoke_popup(self, width=600)


    def draw(self, context):

        wm = context.window_manager
        layout = self.layout

        layout.label(text="SEUT Notifications", icon='INFO')

        if len(SEUT_OT_IssueDisplay.issues_sorted) < 1:
            layout.separator(factor=1.0)
            layout.label(text="SEUT has not generated any notifications so far.")
        else:
            split = layout.split(factor=0.75)
            split.label(text="This list displays the last 50 notifications generated by SEUT.")
            split.operator('wm.clear_issues', icon='REMOVE')
            split = layout.split(factor=0.90)
            split.label(text="")
            split.prop(wm.seut, 'display_errors', icon='CANCEL', text="")
            split.prop(wm.seut, 'display_warnings', icon='ERROR', text="")
            split.prop(wm.seut, 'display_infos', icon='INFO', text="")
            layout.separator(factor=1.0)
        
        for issue in SEUT_OT_IssueDisplay.issues_sorted:

            if issue.issue_type == 'ERROR' and not wm.seut.display_errors:
                continue
            if issue.issue_type == 'WARNING' and not wm.seut.display_warnings:
                continue
            if issue.issue_type == 'INFO' and not wm.seut.display_infos:
                continue

            box = layout.box()

            split = box.split(factor=0.85)

            row = split.row()
            if issue.issue_type == 'ERROR':
                row.alert = True
                row.label(text="", icon='CANCEL')
            elif issue.issue_type == 'WARNING':
                row.label(text="", icon='ERROR')
            else:
                row.label(text="", icon='INFO')
            row.label(text=issue.issue_type)
            row.label(text=issue.code)
            row.label(text=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(issue.timestamp)))

            col = box.column()
            if issue.issue_type == 'ERROR':
                col.alert = True

            wrapp = textwrap.TextWrapper(width=110)
            text_list = wrapp.wrap(text=issue.text)
            for text in text_list:
                row = col.row()
                row.scale_y = 0.75
                row.label(text=text)

            row = split.row()
            if issue.issue_type == 'ERROR':
                row.alert = True
            if issue.issue_type == 'ERROR' or issue.issue_type == 'WARNING':
                semref = row.operator('wm.semref_link', text="SEMREF", icon='INFO')
                semref.section = ''
                semref.page = 'troubleshooting'
                semref.code = '#' + issue.code.lower()
        
        layout.separator(factor=1.0)
        split = layout.split(factor=0.75)
        split.label(text="Should no relevant error be listed here, please check the Blender System Console:")
        split.operator('wm.console_toggle', icon='CONSOLE')


class SEUT_OT_ClearIssues(Operator):
    """Clears all current issues"""
    bl_idname = "wm.clear_issues"
    bl_label = "Clear Notifications"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        
        wm = context.window_manager
        
        wm.seut.issues.clear()
        SEUT_OT_IssueDisplay.issues_sorted.clear()
        
        return {'FINISHED'}