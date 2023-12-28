# Author: YGaotian (Kyanos)
# Date: 2023-12-28
# Select two vertices on a mesh, and run this script to get all the vertices on the
# shortest path between them.

import maya.cmds as cmds


def select_shortest_path():
    # 获取当前选择的顶点
    selected_vertices = cmds.ls(selection=True, flatten=True)

    # 确保选择了两个顶点
    if len(selected_vertices) != 2:
        cmds.warning("请选择两个顶点。")
        return

    # 获取两个顶点的索引
    vtx1_index = int(selected_vertices[0].split('[')[-1].split(']')[0])
    vtx2_index = int(selected_vertices[1].split('[')[-1].split(']')[0])

    # 使用polySelect命令获取最短路径上的边
    shortest_path_edges = cmds.polySelect(cmds.ls(selection=True)[0], 
                                            shortestEdgePath=(vtx1_index, vtx2_index),
                                            query=True)
                                            
    # 选中最短路径上的每一个顶点
    if shortest_path_edges:
        shortest_path_edges = [int(edge) for edge in shortest_path_edges]
        shortest_path_vertices = cmds.polyListComponentConversion([selected_vertices[0].split("v")[0]
                                                            + "e[" + str(i) + "]" for i in shortest_path_edges],
                                                            toVertex=True)
        cmds.select(shortest_path_vertices, replace=True)
    else:
        cmds.warning("未找到最短路径。")


select_shortest_path()
