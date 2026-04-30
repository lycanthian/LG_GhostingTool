from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QColorDialog
from PySide6.QtGui import QColor
from core.MayaWidget import MayaWidget
import maya.cmds as mc
import importlib
import core.MayaUtilities
importlib.reload(core.MayaUtilities)

class GhostingTool:
    def __init__(self):
        self.meshes = []

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

        PrevShader = mc.shadingNode("lambert", asShader=True, n="PrevShader")
        mc.setAttr(PrevShader + '.color', self.prevColorRGBF[0], self.prevColorRGBF[1], self.prevColorRGBF[2], type='double3')
        PrevSG = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name=PrevShader + 'SG')
        mc.connectAttr(PrevShader + '.outColor', PrevSG + '.surfaceShader', force=True)
        print(f"new color for previous frames is {self.prevColorRGBF}")
        
    def SetNextColor(self, newNextColor):
        self.nextColorRGBF = newNextColor
        self.nextColorRGBF = self.nextColorRGBF.removeprefix('(').removesuffix(')')
        splitList = self.nextColorRGBF.split(",")
        for i in range(len(splitList)):
            splitList[i] = float(splitList[i])
        self.nextColorRGBF = splitList

        NextShader = mc.shadingNode("lambert", asShader=True, n="NextShader")
        mc.setAttr(NextShader + '.color', self.nextColorRGBF[0], self.nextColorRGBF[1], self.nextColorRGBF[2], type='double3')
        NextSG = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name=NextShader + 'SG')
        mc.connectAttr(NextShader + '.outColor', NextSG + '.surfaceShader', force=True)
        print(f"new color for next frames is {self.nextColorRGBF}")

    def SetPrevFrames(self, newPrevFramesAmt):
        self.prevFramesAmt = newPrevFramesAmt
        print(f"New previous frames amount is {self.prevFramesAmt}")

    def SetNextFrames(self, newNextFramesAmt):
        self.nextFramesAmt = newNextFramesAmt
        print(f"New next frames amount is {self.nextFramesAmt}")
        
    def GhostFrames(self):
        print("Ghosting frames!")
        meshes = self.meshes
        currentFrame = mc.currentTime(query=True)
        currentFrame = int(currentFrame)
        prevFramesAmt = int(self.prevFramesAmt)
        nextFramesAmt = int(self.nextFramesAmt)

        for i in range(currentFrame - prevFramesAmt, currentFrame):
            mc.currentTime(i)
            mc.duplicate('pSphere1', n="Ghost"+meshes+str(i))

        for i in range(currentFrame, currentFrame + nextFramesAmt):
            mc.currentTime(i)
            mc.duplicate('pSphere1', n="Ghost"+meshes+str(i))


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

        self.frameNumberLayout = QHBoxLayout()
        self.frameNumberLayout.addWidget(QLabel("Prev Frames:"))
        self.prevFrameNumberLineEdit = QLineEdit()
        self.frameNumberLayout.addWidget(self.prevFrameNumberLineEdit)
        self.frameNumberLayout.addWidget(QLabel("Next Frames:"))
        self.nextFrameNumberLineEdit = QLineEdit()
        self.frameNumberLayout.addWidget(self.nextFrameNumberLineEdit)

        self.frameNumberBtnLayout = QHBoxLayout()
        self.setPrevFramesBtn = QPushButton("Set Prev Frames")
        self.frameNumberBtnLayout.addWidget(self.setPrevFramesBtn)
        self.setPrevFramesBtn.clicked.connect(self.SetPrevFramesBtnClicked)
        self.setNextFramesBtn = QPushButton("Set Next Frames")
        self.frameNumberBtnLayout.addWidget(self.setNextFramesBtn)
        self.setNextFramesBtn.clicked.connect(self.SetNextFramesBtnClicked)
        
        self.masterLayout.addLayout(self.frameNumberLayout)
        self.masterLayout.addLayout(self.frameNumberBtnLayout)

        self.ghostFramesBtn = QPushButton("Ghost Frames")
        self.masterLayout.addWidget(self.ghostFramesBtn)
        self.ghostFramesBtn.clicked.connect(self.GhostFramesBtnClicked)

    def MeshSelectBtnClicked(self):
        self.ghostingTool.SetSelectedAsMesh()
        self.meshSelectLineEdit.setText(",".join(self.ghostingTool.meshes))

    def SetPrevColorBtnClicked(self):
        dialog = QColorDialog()
        newColor = QColorDialog.getColor(initial=QColor("blue"), title="Select a Color")
        prevColorRGBF = newColor
        prevColorRGBF = str(prevColorRGBF).replace("PySide6.QtGui.QColor.fromRgbF","")
        self.ghostingTool.SetPrevColor(prevColorRGBF)

    def SetNextColorBtnClicked(self):
        dialog = QColorDialog()
        newColor = QColorDialog.getColor(initial=QColor("blue"), title="Select a Color")
        nextColorRGBF = newColor
        nextColorRGBF = str(nextColorRGBF).replace("PySide6.QtGui.QColor.fromRgbF","")
        self.ghostingTool.SetNextColor(nextColorRGBF)

    def SetPrevFramesBtnClicked(self):
        self.ghostingTool.SetPrevFrames(self.prevFrameNumberLineEdit.text())

    def SetNextFramesBtnClicked(self):
        self.ghostingTool.SetNextFrames(self.nextFrameNumberLineEdit.text())

    def GhostFramesBtnClicked(self):
        self.ghostingTool.GhostFrames()

    def GetWidgetHash(self):
        return "400b2d649f76aa2add750afbfa95af38"

def Run():
    ghostingToolWidget = GhostingToolWidget()
    ghostingToolWidget.show()

Run()