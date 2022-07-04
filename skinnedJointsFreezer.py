# -*- coding:utf-8 -*-

'''
Use this tool to freeze the joints bound to a mesh, no need to unbind the skin first.
Usage    : Select one or more skinned meshes, then run this script, notice, DO NOT select any other object, otherwise,
           an error should occur, if the error occurs, you should try to click Undo button to check if the last action
           is performed by yourself, not by the code
Author   ：Y.Gaotian
E-mail   : ygaotian@outlook.com || 2975410710@qq.com
Create   ：2022-07-04
License  : Code licensed under the MIT License
Important: Unlawful use of my code is prohibited
All rights reserved
'''

import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma


def getSkinClusterMObj(geoDag):
    '''
    geoDag: The MDagPath of the selected geometry
    '''
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

    selListIter = om.MItSelectionList(actvSelList)
    while (not selListIter.isDone()):
        actvSelDag = selListIter.getDagPath()
        actvSelShape = actvSelDag.extendToShape()
        actvSelObj = actvSelShape.node()

        # get skin cluster
        skinClusterObj = getSkinClusterMObj(actvSelDag)

        # make MFnSkinCluster
        mfnSkinCluster = oma.MFnSkinCluster(skinClusterObj)

        # get all joints
        jointsDagPathList = mfnSkinCluster.influenceObjects()
        jointInfluencesIDList = om.MIntArray()
        JID = 0
        for i in jointsDagPathList:
            jointInfluencesIDList.append(JID)
            JID += 1

        # record weights
        allWeightsList = []  # A 2-D list that contains the weight of all joints on every vertex
        vtxOnMeshIter = om.MItMeshVertex(actvSelObj)
        while (not vtxOnMeshIter.isDone()):
            '''
            getWights() returns a tuple that contains a list of weight of every joint, and, the number of joints
            So allWeightsList should appends getWeights()[0]
            '''
            allWeightsList.append(mfnSkinCluster.getWeights(actvSelShape, vtxOnMeshIter.currentItem())[0])
            # print mfnSkinCluster.getWeights(actvSelShape, vtxOnMeshIter.currentItem())[0]
            vtxOnMeshIter.next()

        # unbinding
        cmds.skinCluster(actvSelDag.fullPathName(), e=1, ub=1)

        # freeze joints
        for each in jointsDagPathList:
            cmds.makeIdentity(each, apply=1, r=1)

        # rebind the skin
        cmds.skinCluster(actvSelDag.fullPathName(), jointsDagPathList)

        # restore weights
        new_skinClusterObj = getSkinClusterMObj(actvSelDag)
        new_mfnSkinCluster = oma.MFnSkinCluster(new_skinClusterObj)
        new_vtxOnMeshIter = om.MItMeshVertex(actvSelObj)
        while (not new_vtxOnMeshIter.isDone()):
            currentVtx = new_vtxOnMeshIter.currentItem()
            currentVtxID = new_vtxOnMeshIter.index()
            new_mfnSkinCluster.setWeights(actvSelDag,
                                          currentVtx,
                                          jointInfluencesIDList,
                                          allWeightsList[currentVtxID])
            new_vtxOnMeshIter.next()

        selListIter.next()


rebinding()
