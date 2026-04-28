from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtGui import QColor
from core.MayaWidget import MayaWidget
import maya.cmds as mc
import importlib
import core.MayaUtilities
importlib.reload(core.MayaUtilities)

class GhostingTool:
    def __init__(self):
        self.meshes = []
        self.clips = []

    def SetSelectedAsMesh(self):
        selection = mc.ls(sl=True)
        if not selection:
            raise Exception("Please select the meshes of the rig.")

        for obj in selection:
            shapes = mc.listRelatives(obj, s=True)
            if not shapes or mc.objectType(shapes[0]) != "mesh":
                raise Exception(f"{obj} is not a mesh. Please select the meshes of the rig.")
            
            self.meshes = selection

class GhostingToolWidget(MayaWidget):
    def __init__(self):
        super().__init__()
        self.ghostingTool = GhostingTool()
        self.setWindowTitle("Ghosting Tool")

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.masterLayout.addWidget(QLabel("Select the mesh of the object for ghosting."))
        meshSelectLayout = QHBoxLayout()
        self.masterLayout.addLayout(meshSelectLayout)
        meshSelectLayout.addWidget(QLabel("Mesh:"))
        self.meshSelectLineEdit = QLineEdit()
        self.meshSelectLineEdit.setEnabled(False)
        meshSelectLayout.addWidget(self.meshSelectLineEdit)
        meshSelectBtn = QPushButton("<<<")
        meshSelectLayout.addWidget(meshSelectBtn)
        meshSelectBtn.clicked.connect(self.MeshSelectBtnClicked)
    
    def MeshSelectBtnClicked(self):
        self.ghostingTool.SetSelectedAsMesh()
        self.meshSelectLineEdit.setText(",".join(self.ghostingTool.meshes))

    def GetWidgetHash(self):
        return "400b2d649f76aa2add750afbfa95af38"

def Run():
    ghostingToolWidget = GhostingToolWidget()
    ghostingToolWidget.show

Run()