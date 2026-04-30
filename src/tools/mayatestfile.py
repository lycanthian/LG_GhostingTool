# for testing inside of maya
import maya.cmds as mc
meshes = mc.ls(sl=True)
meshes = meshes
currentFrame = cmds.currentTime(query=True)

prevFrames = 3
prevFrames = int(prevFrames)
nextFrames = 3
nextFrames = int(nextFrames)
currentFrame = int(currentFrame)

for i in range(currentFrame - prevFrames, currentFrame):
    mc.currentTime(i)
    duplicateName="Ghost_pSphere1_"+str(i)
    mc.duplicate("pSphere1", n=duplicateName)
    prevMatName = "PrevShader"
    PrevSG = cmds.listConnections(f"{prevMatName}", destination=True, type='shadingEngine')
    mc.sets(f"{duplicateName}", edit=True, forceElement=f"{PrevSG}")
    print(f"{duplicateName}")
    
    mc.currentTime(0)
    mc.setAttr(f"{duplicateName}.v", 0)
    mc.setKeyframe(f"{duplicateName}.v")
    
    mc.currentTime(i-1)
    mc.setAttr(f"{duplicateName}.v", 0)
    mc.setKeyframe(f"{duplicateName}.v")
    
    mc.currentTime(i)
    mc.setAttr(f"{duplicateName}.v", 1)
    mc.setKeyframe(f"{duplicateName}.v")
    
    mc.currentTime(i+nextFrames)
    mc.setAttr(f"{duplicateName}.v", 1)
    mc.setKeyframe(f"{duplicateName}.v")
    
    mc.currentTime(i+nextFrames+1)
    mc.setAttr(f"{duplicateName}.v", 0)
    mc.setKeyframe(f"{duplicateName}.v")

    mc.currentTime(i)

for i in range(currentFrame, currentFrame + nextFrames):
    mc.currentTime(i)
    duplicateName="Ghost_pSphere1_"+str(i)
    mc.duplicate("pSphere1", n=duplicateName)
    nextMatName = "NextShader"
    NextSG = cmds.listConnections(f"{nextMatName}", destination=True, type='shadingEngine')
    mc.sets(f"{duplicateName}", edit=True, forceElement=f"{NextSG}")
    print(f"{duplicateName}")
    
    mc.currentTime(0)
    mc.setAttr(f"{duplicateName}.v", 0)
    mc.setKeyframe(f"{duplicateName}.v")
    
    mc.currentTime(i-prevFrames-1)
    mc.setAttr(f"{duplicateName}.v", 0)
    mc.setKeyframe(f"{duplicateName}.v")
    
    mc.currentTime(i-prevFrames)
    mc.setAttr(f"{duplicateName}.v", 1)
    mc.setKeyframe(f"{duplicateName}.v")
    
    mc.currentTime(i)
    mc.setAttr(f"{duplicateName}.v", 1)
    mc.setKeyframe(f"{duplicateName}.v")
    
    mc.currentTime(i+1)
    mc.setAttr(f"{duplicateName}.v", 0)
    mc.setKeyframe(f"{duplicateName}.v")

    mc.currentTime(i)