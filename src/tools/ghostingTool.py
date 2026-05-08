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

    def SetGhostColor(self, newGhostColor):
        self.ghostColorRGBF = newGhostColor
        self.ghostColorRGBF = self.ghostColorRGBF.removeprefix('(').removesuffix(')')
        splitList = self.ghostColorRGBF.split(",")
        for i in range(len(splitList)):
            splitList[i] = float(splitList[i])
        self.ghostColorRGBF = splitList

        GhostShader = mc.shadingNode("lambert", asShader=True, n="GhostShader")
        mc.setAttr(GhostShader + '.color', self.ghostColorRGBF[0], self.ghostColorRGBF[1], self.ghostColorRGBF[2], type='double3')
        GhostSG = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name=GhostShader + 'SG')
        mc.connectAttr(GhostShader + '.outColor', GhostSG + '.surfaceShader', force=True)
        print(f"new color for ghosted frames is {self.ghostColorRGBF}")

    def SetPrevFrames(self, newPrevFrames):
        self.prevFrames = newPrevFrames
        print(f"New previous frames amount is {self.prevFrames}")

    def SetNextFrames(self, newnextFrames):
        self.nextFrames = newnextFrames
        print(f"New next frames amount is {self.nextFrames}")
        
    def SetStartRange(self, newStartRange):
        self.startRange = newStartRange
        print(f"The ghost range will start at {self.startRange}.")
    
    def SetEndRange(self, newEndRange):
        self.endRange = newEndRange
        print(f"The ghost range will end at {self.endRange}.")

    def GhostFrames(self):
        print("Ghosting frames!")
        meshes = self.meshes
        currentFrame = mc.currentTime(query=True)
        currentFrame = int(currentFrame)
        prevFrames = int(self.prevFrames)
        nextFrames = int(self.nextFrames)
        startRange = int(self.startRange)
        endRange = int(self.endRange)

        mc.select(clear=True)
        mc.group(empty=True, n=f"GhostedFrames_grp")

        for i in range(startRange, endRange):
            mc.currentTime(i)
            duplicateName="Ghost_"+str(meshes[0])+"_"+str(i)
            mc.duplicate(meshes, n=duplicateName)
            mc.sets(f"{duplicateName}", edit=True, forceElement="GhostShaderSG")
            print(f"{duplicateName}")
            
            mc.currentTime(i-prevFrames-1)
            mc.setAttr(f"{duplicateName}.v", 0)
            mc.setKeyframe(f"{duplicateName}.v")
            
            mc.currentTime(i-prevFrames)
            mc.setAttr(f"{duplicateName}.v", 1)
            mc.setKeyframe(f"{duplicateName}.v")
            
            mc.currentTime(i-1)
            mc.setAttr(f"{duplicateName}.v", 1)
            mc.setKeyframe(f"{duplicateName}.v")
            
            mc.currentTime(i)
            mc.setAttr(f"{duplicateName}.v", 0)
            mc.setKeyframe(f"{duplicateName}.v")
            
            mc.currentTime(i+1)
            mc.setAttr(f"{duplicateName}.v", 1)
            mc.setKeyframe(f"{duplicateName}.v")
            
            mc.currentTime(i+nextFrames)
            mc.setAttr(f"{duplicateName}.v", 1)
            mc.setKeyframe(f"{duplicateName}.v")
            
            mc.currentTime(i+nextFrames+1)
            mc.setAttr(f"{duplicateName}.v", 0)
            mc.setKeyframe(f"{duplicateName}.v")
            
            mc.parent(f"{duplicateName}", "GhostedFrames_grp")
            
            mc.currentTime(i)


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

        self.masterLayout.addWidget(QLabel("Now set colors for ghosted frames."))
        
        self.colorBtnLayout = QHBoxLayout()
        self.setGhostColorBtn = QPushButton("Set Ghosting Color")
        self.masterLayout.addWidget(self.setGhostColorBtn)
        self.setGhostColorBtn.clicked.connect(self.SetGhostColorBtnClicked)

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

        self.rangeLayout = QHBoxLayout()
        self.rangeLayout.addWidget(QLabel("Start Frame:"))
        self.startRangeNumberLineEdit = QLineEdit()
        self.rangeLayout.addWidget(self.startRangeNumberLineEdit)
        self.rangeLayout.addWidget(QLabel("End Range:"))
        self.endRangeNumberLineEdit = QLineEdit()
        self.rangeLayout.addWidget(self.endRangeNumberLineEdit)

        self.rangeBtnLayout = QHBoxLayout()
        self.setStartRangeBtn = QPushButton("Set Start Frame")
        self.rangeBtnLayout.addWidget(self.setStartRangeBtn)
        self.setStartRangeBtn.clicked.connect(self.SetStartRangeBtnClicked)
        self.setEndRangeBtn = QPushButton("Set End Frame")
        self.rangeBtnLayout.addWidget(self.setEndRangeBtn)
        self.setEndRangeBtn.clicked.connect(self.SetEndRangeBtnClicked)
        
        self.masterLayout.addLayout(self.rangeLayout)
        self.masterLayout.addLayout(self.rangeBtnLayout)

        self.ghostFramesBtn = QPushButton("Ghost Frames")
        self.masterLayout.addWidget(self.ghostFramesBtn)
        self.ghostFramesBtn.clicked.connect(self.GhostFramesBtnClicked)

    def MeshSelectBtnClicked(self):
        self.ghostingTool.SetSelectedAsMesh()
        self.meshSelectLineEdit.setText(",".join(self.ghostingTool.meshes))

    def SetGhostColorBtnClicked(self):
        dialog = QColorDialog()
        newColor = QColorDialog.getColor(initial=QColor("blue"), title="Select a Color")
        ghostColorRGBF = newColor
        ghostColorRGBF = str(ghostColorRGBF).replace("PySide6.QtGui.QColor.fromRgbF","")
        self.ghostingTool.SetGhostColor(ghostColorRGBF)

    def SetPrevFramesBtnClicked(self):
        self.ghostingTool.SetPrevFrames(self.prevFrameNumberLineEdit.text())

    def SetNextFramesBtnClicked(self):
        self.ghostingTool.SetNextFrames(self.nextFrameNumberLineEdit.text())

    def SetStartRangeBtnClicked(self):
        self.ghostingTool.SetStartRange(self.startRangeNumberLineEdit.text())

    def SetEndRangeBtnClicked(self):
        self.ghostingTool.SetEndRange(self.endRangeNumberLineEdit.text())

    def GhostFramesBtnClicked(self):
        self.ghostingTool.GhostFrames()

    def GetWidgetHash(self):
        return "400b2d649f76aa2add750afbfa95af38"

def Run():
    ghostingToolWidget = GhostingToolWidget()
    ghostingToolWidget.show()

Run()