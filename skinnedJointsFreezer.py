# -*- coding:utf-8 -*-

"""
Use this tool to freeze the joints bound in a mesh, no need to unbind the skin first.
Usage    : Select one or more skinned meshes, then run this script, notice, DO NOT select any other object, otherwise,
           an error should occur, if the error occurs, you should try to click Undo button to check if the last action
           is performed by yourself, not by the code
Author   : Y.Gaotian
E-mail   : ygaotian@outlook.com || 2975410710@qq.com
Create   : 2022-07-05
License  : Code licensed under the MIT License
Important: Unlawful use of my code is prohibited
All rights reserved
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma


def get_skin_cluster_mobj(geoDag):
    """
    geoDag: The MDagPath of the selected geometry
    """
    # get the fullPathName list of the skinCluster
    skinClusterTextList = cmds.ls(cmds.listHistory(geoDag.fullPathName()), type="skinCluster")
    if len(skinClusterTextList) < 1:
        return "No Skin Cluster Is Found"

    # return the MObject for that skinCluster node
    clusterSelList = om.MSelectionList()
    clusterSelList.add(skinClusterTextList[0])
    clusterMObj = clusterSelList.getDependNode(0)
    return clusterMObj


def rebinding():
    actvSelList = om.MGlobal.getActiveSelectionList()
    if actvSelList.length() < 1:
        return "Please Select At Least One Geometry"

    listOfJointsDagPathList = []  # a list contains the joint influences list of every geo in MSelectionList
    listOfJointInfluencesIDList = []  # a list contains the joint influences IDs list of each geo in this ↑
    listOfAllJoints = []  # a set of all the joints we want to freeze
    listOfAllWeightsList = []  # a list contains allWeightsList created in every loop

    # progressBar
    progressBar = cmds.progressWindow(title="Processing",
                                      status="Recording Weights: Please wait",
                                      isInterruptable=1)

    try:
        selListIter = om.MItSelectionList(actvSelList)
        while not selListIter.isDone():
            currentSelItemDag = selListIter.getDagPath()
            currentSelItemShape = currentSelItemDag.extendToShape()
            currentSelItemObj = currentSelItemShape.node()

            # get skin cluster
            skinClusterObj = get_skin_cluster_mobj(currentSelItemDag)

            # make MFnSkinCluster
            mfnSkinCluster = oma.MFnSkinCluster(skinClusterObj)

            # get all joints
            jointsDagPathList = mfnSkinCluster.influenceObjects()
            listOfJointsDagPathList.append(jointsDagPathList)
            jointInfluencesIDList = om.MIntArray()
            JID = 0
            for i in jointsDagPathList:
                # record all joints we need to freeze
                if i not in listOfAllJoints:
                    listOfAllJoints.append(i)
                # record all joint influences' IDs into the list in this loop
                jointInfluencesIDList.append(JID)
                JID += 1
            # gathering the jointInfluencesIDList into a list
            listOfJointInfluencesIDList.append(jointInfluencesIDList)

            # record weights
            allWeightsList = []  # A 2-D list that contains the weight of all joints on every vertex
            vtxOnMeshIter = om.MItMeshVertex(currentSelItemObj)
            cmds.progressWindow(progressBar, edit=1, maxValue=vtxOnMeshIter.count())
            while not vtxOnMeshIter.isDone():
                """
                getWights() returns a tuple that contains a list of weight of every joint, and, the number of joints
                So allWeightsList should appends getWeights()[0]
                """
                allJointsWeightAtCurrentVtx = mfnSkinCluster.getWeights(currentSelItemShape,
                                                                        vtxOnMeshIter.currentItem())[0]
                allWeightsList.append(allJointsWeightAtCurrentVtx)

                # progress++
                cmds.progressWindow(progressBar, edit=1, step=1)
                vtxOnMeshIter.next()

            listOfAllWeightsList.append(allWeightsList)

            # unbinding
            cmds.skinCluster(currentSelItemDag.fullPathName(), e=1, ub=1)
            selListIter.next()

        # progress amount reset
        cmds.progressWindow(progressBar, edit=1, progress=0, status="Freezing Rotation: Please wait",
                            maxValue=len(listOfAllJoints))

        # freeze joints
        for each in listOfAllJoints:
            cmds.makeIdentity(each, apply=1, r=1)
            # progress++
            cmds.progressWindow(progressBar, edit=1, step=1)

        # rebinding and restore weights
        currentGeoIndex = 0
        new_selListIter = om.MItSelectionList(actvSelList)

        # progress amount reset
        cmds.progressWindow(progressBar, edit=1, progress=0, status="Rebinding Skins: Please wait")

        while not new_selListIter.isDone():
            new_currentSelItemDag = new_selListIter.getDagPath()
            new_currentSelItemObj = new_currentSelItemDag.extendToShape().node()

            jointNamesForSkinningList = []
            for i in listOfJointsDagPathList[currentGeoIndex]:
                jointNamesForSkinningList.append(i.fullPathName())

            # bind skin
            cmds.skinCluster(new_currentSelItemDag.fullPathName(),
                             jointNamesForSkinningList, tsb=1)

            new_skinClusterObj = get_skin_cluster_mobj(new_currentSelItemDag)
            new_mfnSkinCluster = oma.MFnSkinCluster(new_skinClusterObj)
            new_vtxOnMeshIter = om.MItMeshVertex(new_currentSelItemObj)

            # progressBar set maxValue
            cmds.progressWindow(progressBar, edit=1, maxValue=new_vtxOnMeshIter.count())

            # get jointInfluencesIDList and allWeightsList corresponding to the current loop
            new_jointInfluencesIDList = listOfJointInfluencesIDList[currentGeoIndex]
            new_allWeightsList = listOfAllWeightsList[currentGeoIndex]
            while not new_vtxOnMeshIter.isDone():
                currentVtx = new_vtxOnMeshIter.currentItem()
                currentVtxID = new_vtxOnMeshIter.index()
                new_mfnSkinCluster.setWeights(new_currentSelItemDag, currentVtx,
                                              new_jointInfluencesIDList, new_allWeightsList[currentVtxID])

                # progress++
                cmds.progressWindow(progressBar, edit=1, step=1)
                new_vtxOnMeshIter.next()

            currentGeoIndex += 1
            new_selListIter.next()
    except:
        cmds.progressWindow(progressBar, edit=1, endProgress=1)
        raise
    cmds.progressWindow(progressBar, edit=1, endProgress=1)


rebinding()