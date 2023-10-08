#Toggleable Wheel Rig
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
from maya.api import OpenMaya as om
import math
from functools import partial

side = ['L', 'R']

def settingsWindow():
	if cmds.window('wheelControlWindow', exists=True):
		cmds.deleteUI('wheelControlWindow')

	cmds.window('wheelControlWindow', w=500, title="Auto Roll Rig Controls")
	mainLayout = cmds.columnLayout(columnWidth = 500)
	cmds.text("Make sure you have a character rig selected!")
	createRig = cmds.button(p=mainLayout, label='Create Rig', c=createWheelControls, width = 500)
	breakConnections = cmds.button(p=mainLayout, label = 'Break Connections', width = 500, c=resetWheelConnections)
	cmds.text("Do this after changing keyframes.")
	cmds.button(label='Recalculate', c=recalculateWheels, width = 500)
	cmds.showWindow('wheelControlWindow')

def bakeWheels():
	ns = getNamespace()
	if not ns:
		cmds.warning('No rig selected!')
		return
	else:
		firstFrame = cmds.playbackOptions(q=True, min=True)
		lastFrame = cmds.playbackOptions(q=True, max=True)
		for s in side:
			cmds.bakeResults(s + '_wheelAutorotate_ctrl.ry', sm =True, t = firstFrame + ':' + lastFrame)
	
	return
def getNamespace(*args):
	try:
		namespace = pm.selected()[0].namespace()
	except:
		cmds.warning("No rig selected!")
		return
	return namespace
	
def recalc(side, *args):
	namespace = getNamespace()
	#save frame position
	# currentFrame = cmds.currentTime(q=True)
	#set frame to initial frame
	initialFrame = cmds.playbackOptions(q=True, min=True)
	cmds.currentTime(initialFrame, e=True)

	ctrl = namespace + side + '_wheelAutorotate_ctrl'
	#delete keys on wheel translateY
	deleteConnection(namespace + side + '_wheelAutorotate_ctrl.ry')

	createKeys(namespace,side,ctrl)

def recalculateWheels(*args):
	recalc('L')
	recalc('R')

def resetWheelConnections(*args):
	ns = getNamespace()
	if not ns:
		cmds.warning('No rig selected!')
		return
	deleteConnection(ns + 'L_wheelAutorotate_ctrl.ry')
	deleteConnection(ns + 'R_wheelAutorotate_ctrl.ry')

def createKeys(namespace, side, *args):
	radius = 16.009159
	#32.071, 32.058
	#16.009331

	wheelRotateY = namespace + side + '_wheelAutorotate_ctrl.rotateY'

	ikCtrl = namespace + side + '_wheel_IK_ctrl'
	ikForward = namespace + side + '_wheel_forward'

	wheelVector = om.MVector(cmds.xform(ikCtrl, q=True, t=True, ws=True))
	wheelOldVector = om.MVector(cmds.xform(ikCtrl, q=True, t=True, ws=True))
	forwardVector = cmds.xform(ikForward, q=True, t=True, ws=True)
	for frame in range(int(cmds.playbackOptions(q=True, min=True)), 1 + int(cmds.playbackOptions(q=True, max=True))):
		#print(side + 'wheel frame: ' + str(frame))
		cmds.currentTime(frame, e=True)
		wheelVector = om.MVector(cmds.xform(ikCtrl, q=True, t=True, ws=True))
		#print('current pos: ' + str(wheelVector))
		#print('old pos: ' + str(wheelOldVector))
		forwardVector = om.MVector(cmds.xform(ikForward, q=True, t=True, ws=True))
		#print('forward: ' + str(forwardVector))
		shouldRoll = int(cmds.getAttr(namespace+"wheel_controls.autoRoll"+side))

		dirVector = (forwardVector - wheelVector).normal()
		translateVector = (wheelVector - wheelOldVector).normal()
		distance = (wheelVector - wheelOldVector).length()
		#print('distance: ' + str(distance))
		#print('translate: ' + str(translateVector))
		dot = translateVector * dirVector
		#print('dir: ' + str(dirVector))
		#print('dot: ' + str(dot))
		currentAngle = cmds.getAttr(wheelRotateY)
		newAngle = (currentAngle + shouldRoll * ((360 * ((distance*dot) / (math.pi * 2 * radius))))) % 360
		cmds.setKeyframe(wheelRotateY, v=newAngle, t=frame)
		#print('\n')
		wheelOldVector = om.MVector(cmds.xform(ikCtrl, q=True, t=True, ws=True))

def deleteConnection(plug, *args):
	if cmds.connectionInfo(plug, isDestination=True):
		plug = cmds.connectionInfo(plug, getExactDestination=True)
		readOnly = cmds.ls(plug, ro=True)
		#delete -icn doesn't work if destination attr is readOnly 
		if readOnly:
			source = cmds.connectionInfo(plug, sourceFromDestination=True)
			cmds.disconnectAttr(source, plug)
		else:
			cmds.delete(plug, icn=True)
	
def createWheelControls(*args):
	try:
		namespace = pm.selected()[0].namespace()
	except:
		cmds.warning("No rig selected!")
		return
	controls = namespace + 'wheel_controls'
	try:
		if not cmds.objExists(controls):
			deleteConnection(namespace + 'L_wheelAutorotate_ctrl.ry')
			deleteConnection(namespace + 'R_wheelAutorotate_ctrl.ry')
			ctrls = cmds.group(em=True, name = controls)
			locLGroup = cmds.group(em=True, name= namespace + 'L_Group')
			locRGroup = cmds.group(em=True, name= namespace + 'R_Group')
			locL = cmds.spaceLocator(n=namespace + 'L_wheel_forward')
			locR = cmds.spaceLocator(n=namespace + 'R_wheel_forward')
			cmds.parent(locL, locLGroup)
			cmds.parent(locR, locRGroup)
			cmds.parent(locLGroup, ctrls)
			cmds.parent(locRGroup, ctrls)
			cmds.parentConstraint(namespace + 'L_wheel_IK_ctrl', locLGroup)
			cmds.parentConstraint(namespace + 'R_wheel_IK_ctrl', locRGroup)
			cmds.xform(locL, os=True, r=True, t=(0, 0, 1))
			cmds.xform(locR, os=True, r=True, t=(0, 0, 1))
			cmds.addAttr(ctrls, longName='autoRollL', attributeType='bool', keyable=True, defaultValue = 1)
			cmds.addAttr(ctrls, longName='autoRollR', attributeType='bool', keyable=True, defaultValue = 1)
		else:
			cmds.warning("Controls already exist")
	except:
		cmds.warning("Couldn't create controls.")

