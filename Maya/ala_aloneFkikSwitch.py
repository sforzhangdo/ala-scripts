import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mm
import math
from maya.api import OpenMaya as om
def getTopRelative():
	selected = cmds.ls(sl=1,fl=1,l=1,o=1)
	l = []
	for i in selected:
		l.append("|"+i.split('|')[1])
	return(l[2][1:])

def settingsWindow():
	if cmds.window('settingsWindow', exists=True):
		cmds.deleteUI('settingsWindow')

	cmds.window('settingsWindow', w=500, title="Alone IK/FK Tools")
	mainLayout = cmds.columnLayout(cat=['both', 5], adj=True)
	cmds.text(p=mainLayout, l="NOTE: This tool was made specifically for ALA's Alone project. It is not guaranteed to work on other rigs!")
	cmds.separator(h=10, style='none')
	cmds.text(align='center', l='Switch', fn='boldLabelFont')
	cmds.separator(h=5, style='none')
	switchButtons = cmds.rowColumnLayout(p=mainLayout, numberOfColumns=2, adj=True, columnWidth=([1, 250], [2, 250]))
	cmds.button(l='FK', c=switchFK)
	cmds.button(l='IK', c=switchIK)
	cmds.text(p=mainLayout, align='center', l='FK/IK Matching', fn='boldLabelFont')
	cmds.separator(h=5, style='none')
	matchButtons = cmds.rowColumnLayout(p=mainLayout, numberOfColumns=2, adj=True, columnWidth=([1, 250], [2, 250]))
	cmds.button(l='FK into IK', c=FKtoIK)
	cmds.button(l='IK into FK', c=IKtoFK)

	cmds.showWindow('settingsWindow')

FkJnts = ['_shoulder_FK_JNT', '_elbow_FK_JNT', '_wrist_FK_JNT']
IkJnts = ['_shoulder_IK_JNT', '_elbow_IK_JNT', '_wrist_IK_JNT']
FkCtrls = ['_shoulder_FK_ctrl', '_elbow_FK_ctrl', '_wrist_FK_ctrl']
IkCtrls = ['_shoulder_IK_ctrl', '_elbow_IK_ctrl', '_wrist_IK_ctrl']

fkikCtrl = 'FKIK'
masterCtrl = '_hand_master_ctrl'

def calculate_pole_vector(p1, p2, p3, poleDistance=1):
	"""
	An Autodesk Maya PyMEL script that calculates a pole vector position
	based on 3 input PyNode objects. example: leg, knee, ankle bones.
	Chris Lesage chris@rigmarolestudio.com

	This function takes 3 PyMEL PyNodes as inputs.
	Creates a pole vector position at a "nice" distance away from a triangle of positions.
	Normalizes the bone lengths relative to the knee to calculate straight ahead
	without shifting up and down if the bone lengths are different.
	Returns a pymel.core.datatypes.Vector

	"""
	vec1 = p1.getTranslation(space='world') # "hips"
	vec2 = p2.getTranslation(space='world') # "knee"
	vec3 = p3.getTranslation(space='world') # "ankle"
	temp1 = 0.0
	temp2 = 0.0
	if getLimb() == 'L': #Christa: ALONE rig hard code fix. Delete if you don't need it.
		temp1 = cmds.getAttr(p1 + '.translateZ')
		temp2 = cmds.getAttr(p3 + '.translateZ')

		cmds.setAttr(p1 + '.translateZ', 0)
		cmds.setAttr(p3 + '.translateZ', 0)
		
		vec1 = p1.getTranslation(space='world')
		vec2 = p2.getTranslation(space='world')


	# 1. Calculate a "nice distance" based on average of the two bone lengths.
	legLength = (vec2-vec1).length()
	kneeLength = (vec3-vec2).length()
	distance = (legLength + kneeLength) * 0.5 * poleDistance
	
	# 2. Normalize the length of leg and ankle, relative to the knee.
	# This will ensure that the pole vector goes STRAIGHT ahead of the knee
	# Avoids up-down offset if there is a length difference between the two bones.
	vec1norm = ((vec1 - vec2).normal() * distance) + vec2
	vec3norm = ((vec3 - vec2).normal() * distance) + vec2
	
	# 3. given 3 points, calculate a pole vector position
	mid = vec1norm + (vec2-vec1norm).projectionOnto(vec3norm-vec1norm)

	# 4. Move the pole vector in front of the knee by the "nice distance".
	midPointer = vec2 - mid
	poleVector = (midPointer.normal() * distance) + vec2
	if getLimb() == 'L':
		cmds.setAttr(p1 + '.translateZ', temp1)
		cmds.setAttr(p3 + '.translateZ', temp2)
	return poleVector

def switchIK(*args):
	try:
		namespace = pm.selected()[0].namespace()
		#Get the selected limb (L/R)
		selected = cmds.ls(sl=True)
		limb = selected[0].rpartition(':')[2][0]
		#Switch to IK
		cmds.setAttr(namespace + limb + masterCtrl + '.' + fkikCtrl, 1)
	except:
		cmds.warning('Please select a valid limb.')

def switchFK(*args):
	try:
		namespace = pm.selected()[0].namespace()
		#Get the selected limb (L/R)
		selected = cmds.ls(sl=True)
		limb = selected[0].rpartition(':')[2][0]
		#Switch to FK
		cmds.setAttr(namespace + limb + masterCtrl + '.' + fkikCtrl, 0)
	except:
		cmds.warning('Please select a valid limb.')

def FKtoIK(*args):
	try:
		namespace = pm.selected()[0].namespace()
		#Get the selected limb (L/R)
		selected = cmds.ls(sl=True)
		limb = selected[0].rpartition(':')[2][0]

		#Match FK limbs to IK limbs. Assuming consistent naming, we can just loop through the joints and tack the namespace in front.

		for fk, ik in zip(FkCtrls, IkJnts):
			fkCtrl = namespace + limb + fk
			ikJoint = namespace + limb + ik
			cmds.matchTransform(fkCtrl, ikJoint)
			if limb == 'L':
				cmds.setAttr(fkCtrl + '.translateZ', 0)
		cmds.select(namespace + limb + masterCtrl)
	except:
		cmds.warning('Please select a valid limb.')

def IKtoFK(*args):
	try:
		#Store FK values
		namespace = pm.selected()[0].namespace()
		limb = getLimb()
		poleCtrl = namespace + limb + IkCtrls[1]
		temp = []
		fkBoneChain = namespace + limb + FkCtrls[0]
		#Copy bones
		copy = cmds.duplicate(fkBoneChain, n='copy_' + limb + FkCtrls[0], rc=True)
		copyList = cmds.listRelatives(copy, ad=True, pa=True)
		for name in copyList:
			cmds.rename(name, 'copy_' + name)
		ik_handle = namespace + limb + IkCtrls[2]	
		#Match FK to IK
		cmds.select(fkBoneChain)
		FKtoIK()
		#Spawn locator
		locator = cmds.spaceLocator()
		#Match to pole vector
		cmds.matchTransform(locator, poleCtrl)
		#Parent locator to elbow
		cmds.parent(locator, namespace + limb + FkJnts[1])
		#Move bones back to original FK values
		for i in range(len(FkCtrls)):
			bone = limb + FkCtrls[i]
			cmds.matchTransform(namespace + bone, 'copy_' + bone)
		# #Match IK wrist and pole vector to locator
		cmds.matchTransform(poleCtrl, locator)
		cmds.matchTransform(ik_handle, namespace + limb + FkCtrls[2])
		# #Clean up
		cmds.delete('copy_' + limb + FkCtrls[0])
		cmds.delete(locator)
		if limb == 'R':
			mm.eval('rotate -r -os -fo 0 0 180 ' + ik_handle + ';')
		cmds.select(namespace + limb + masterCtrl)
	except:
		cmds.warning('Please select a valid limb.')
	return

def getMDagPath(node):
	selList=om.MSelectionList()
	selList.add(node)
	return selList.getDagPath(0)
	
def getMObject(node):
	selList=om.MSelectionList()
	selList.add(node)
	return selList.getDependNode(0)

def matchTransformation(targetNode, followerNode, translation=True, rotation=True):
	followerMTransform=om.MFnTransform(getMDagPath(followerNode))
	targetMTransform=om.MFnTransform(getMDagPath(targetNode))
	targetMTMatrix=om.MTransformationMatrix(om.MMatrix(cmds.xform(targetNode, matrix=True, ws=1, q=True)))
	if translation:
		targetRotatePivot=om.MVector(targetMTransform.rotatePivot(om.MSpace.kWorld))
		followerMTransform.setTranslation(targetRotatePivot,om.MSpace.kWorld)
	if rotation:
		#using the target matrix decomposition
		#Worked on all cases tested
		followerMTransform.setRotation(targetMTMatrix.rotation(True),om.MSpace.kWorld)
		
		#Using the MFnTransform quaternion rotation in world space
		#Doesn't work when there is a -1 scale on the object itself
		#Doesn't work when the object has frozen transformations and there is a -1 scale on a parent group.
		#followerMTransform.setRotation(MFntMainNode.rotation(om.MSpace.kWorld, asQuaternion=True),om.MSpace.kWorld)

class Vector3():
	"""
	Data type class for convenient Vector3 calculation

	Initialize:
	using list or tuple: v = Vector3([1, 2, 3])
	using list of arguments (3): v = Vector3(1, 2, 3)
	"""

	def __init__(self, *args):
		self._vector = None

		# list
		if len(args) == 1:
			if isinstance(args[0], (tuple, list)):
				if len(args[0]) == 3:
					self._vector = args[0]

		# three separate arguments
		elif len(args) == 3:
			self._vector = args

		if not self._vector:
			raise TypeError('initialize failure, check input type')

	def __repr__(self):
		return '{}({}, {}, {})'.format(
			self.__class__.__name__,
			self.x,
			self.y,
			self.z
		)

	def __neg__(self):
		return self.__class__(-self.x, -self.y, -self.z)

	def __mul__(self, other):
		return self.__class__(self.x * other, self.y * other, self.z * other)

	def __rmul__(self, other):
		return self.__mul__(other)

	def __div__(self, other):
		try:
			return self.__class__(
				self.x / other,
				self.y / other,
				self.z / other
			)
		except ZeroDivisionError:
			raise ZeroDivisionError

	def __sub__(self, other):
		return self.__class__(self.x - other.x, self.y - other.y, self.z - other.z)

	def __rsub__(self, other):
		return -self.__sub__(other)

	def __add__(self, other):
		return self.__class__(self.x + other.x, self.y + other.y, self.z + other.z)

	def __radd__(self, other):
		return self.__add__(other)

	def normalize(self):
		if self._vector:
			return self / self.length

		return self.__class__.zero_vector()

	@classmethod
	def zero_vector(cls):
		return cls(0, 0, 0)

	@property
	def length(self):
		return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

	@property
	def x(self):
		return self._vector[0]

	@property
	def y(self):
		return self._vector[1]

	@property
	def z(self):
		return self._vector[2]

	def as_list(self):
		return [self.x, self.y, self.z]
	
def getLimb():
	selected = cmds.ls(sl=True)
	limb = selected[0].rpartition(':')[2][0]
	return limb
