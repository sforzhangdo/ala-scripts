import maya.cmds as cmds
import maya.mel as mm
from functools import partial

labelArray = ['X', 'Y', 'Z']
#Window layout
def selectCurvesWin():
    if cmds.window('selectCurves', exists=True):
        cmds.deleteUI('selectCurves')

    cmds.window('selectCurves', title='Select Curves', rtf=True)
    mainLayout = cmds.columnLayout()

    cmds.text(label='Translate')
    transLayout = cmds.rowColumnLayout(p=mainLayout, nc=2)
    translateGrp = cmds.checkBoxGrp('translate', p=transLayout, ncb=3, la3=labelArray)
    cmds.button(p=transLayout, label='Select curves', c=partial(selectCurves, 'translate'))

    cmds.text(p=mainLayout, label='Rotate')
    rotLayout = cmds.rowColumnLayout(p=mainLayout, nc=2)
    rotGrp = cmds.checkBoxGrp('rotate', p=rotLayout, ncb=3, la3=labelArray)
    cmds.button(p=rotLayout, label='Select curves', c=partial(selectCurves, 'rotate'))

    cmds.text(p=mainLayout, label='Scale')
    scaleLayout = cmds.rowColumnLayout(p=mainLayout, nc=2)
    scaleGroup = cmds.checkBoxGrp('scale', p=scaleLayout, ncb=3, la3=labelArray)
    cmds.button(p=scaleLayout, label='Select curves', c=partial(selectCurves, 'scale'))

    cmds.separator(h=10, st='none')
    cmds.button(p=mainLayout, label='Select from entire transform', c=selectAll)
    cmds.showWindow('selectCurves')

def selectCurves(group, *args):
    cmds.selectKey(cl=True)
    curToSel = cmds.checkBoxGrp(group, q=True, va3=True) #check which checkboxes are ticked
    selected = []
    curve = ''
    for i in range(len(curToSel)):
        if curToSel[i] == True:
            selected.append(labelArray[i])
    
    for i in cmds.ls(sl=True):
        for j in selected:
            curve = cmds.findKeyframe(i, curve=True, at=group+j)
            if curve != None:
                cmds.selectKey(curve, add=True, k=True)
    mm.eval('isolateAnimCurve true graphEditor1FromOutliner graphEditor1GraphEd;')

def selectAll(*args):
    cmds.selectKey(cl=True)
    groups = ['translate', 'rotate', 'scale']
    for i in groups:
        curToSel = cmds.checkBoxGrp(i, q=True, va3=True)
        selected = []
        curve = ''
        for j in range(len(curToSel)):
            if curToSel[j] == True:
                selected.append(labelArray[j])
        
        for sel in cmds.ls(sl=True):
            for j in selected:
                curve = cmds.findKeyframe(sel, curve=True, at=i+j)
                if curve != None:
                    cmds.selectKey(curve, add=True, k=True)
    mm.eval('isolateAnimCurve true graphEditor1FromOutliner graphEditor1GraphEd;')

selectCurvesWin()