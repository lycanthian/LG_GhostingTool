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

    def SetPrevColor(self, newPrevColor):
        self.prevColorRGBF = newPrevColor
        self.prevColorRGBF = self.prevColorRGBF.removeprefix('(').removesuffix(')')
        splitList = self.prevColorRGBF.split(",")
        for i in range(len(splitList)):
            splitList[i] = float(splitList[i])
        self.prevColorRGBF = splitList
        print(f"new color for previous frames is {self.prevColorRGBF}")
        
    def SetNextColor(self, newNextColor):
        self.nextColorRGBF = newNextColor
        self.nextColorRGBF = self.nextColorRGBF.removeprefix('(').removesuffix(')')
        splitList = self.nextColorRGBF.split(",")
        for i in range(len(splitList)):
            splitList[i] = float(splitList[i])
        self.nextColorRGBF = splitList
        print(f"new color for next frames is {self.nextColorRGBF}")

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

        self.masterLayout.addWidget(QLabel("Now set colors for past and forward frames."))
        
        self.colorBtnLayout = QHBoxLayout()
        self.setPrevColorBtn = QPushButton("Set Previous Color")
        self.masterLayout.addWidget(self.setPrevColorBtn)
        self.setPrevColorBtn.clicked.connect(self.SetPrevColorBtnClicked)

        self.setNextColorBtn = QPushButton("Set Next Color")
        self.masterLayout.addWidget(self.setNextColorBtn)
        self.setNextColorBtn.clicked.connect(self.SetNextColorBtnClicked)


    def MeshSelectBtnClicked(self):
        self.ghostingTool.SetSelectedAsMesh()
        self.meshSelectLineEdit.setText(",".join(self.ghostingTool.meshes))

    def SetPrevColorBtnClicked(self):
        dialog = QColorDialog()
        newColor = QColorDialog.getColor(initial=QColor("blue"), title="Select a Color")
        prevColorRGBF = newColor
        prevColorRGBF = str(prevColorRGBF).replace("PySide6.QtGui.QColor.fromRgbF","")
        print(f"new control color:", prevColorRGBF)
        self.ghostingTool.SetPrevColor(prevColorRGBF)

    def SetNextColorBtnClicked(self):
        dialog = QColorDialog()
        newColor = QColorDialog.getColor(initial=QColor("blue"), title="Select a Color")
        nextColorRGBF = newColor
        nextColorRGBF = str(nextColorRGBF).replace("PySide6.QtGui.QColor.fromRgbF","")
        print(f"new control color:", nextColorRGBF)
        self.ghostingTool.SetNextColor(nextColorRGBF)

    def GetWidgetHash(self):
        return "400b2d649f76aa2add750afbfa95af38"

def Run():
    ghostingToolWidget = GhostingToolWidget()
    ghostingToolWidget.show()

Run()