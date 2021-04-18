import modern_robotics as mr

def FK(Mlist, Slist, thetalist):
    
    # find the transforms of the link ends at each point
    Tlist = []
    chain = np.eye(4)
    for linkM, screw, theta in zip(Mlist, Slist, thetalist):
        
        # get pose of link at theta
        se3mat = mr.VecTose3(screw)
        chain = chain @ mr.MatrixExp6(se3mat*theta)
        linkT = chain @ linkM
        Tlist.append(linkT.copy())
        
    return Tlist

def update(links, Tlist):
    
    print(wires)
    print(wires2)
    
    for link, T in zip(links, Tlist):
        link.tf = T @ link.relpose
        link.update()
        
    wires._verts3d = (
        np.array([Tlist[1][0,3], ArmMs[0].tf[0,3], ArmMs[1].tf[0,3], ArmMs[2].tf[0,3]]),
        np.array([Tlist[1][1,3], ArmMs[0].tf[1,3], ArmMs[1].tf[1,3], ArmMs[2].tf[1,3]]),
        np.array([Tlist[1][2,3], ArmMs[0].tf[2,3], ArmMs[1].tf[2,3], ArmMs[2].tf[2,3]])
    )
    
    # TODO numba-fy this!
    
    # Find the whisker position

    # set arm_joint as origin
    x_1, y_1 = 0, 0
    # get relative location of crown connection in plane
    x_2, y_2 = np.sqrt(np.sum((ArmMs[0].tf[0:2,3]-Tlist[1][0:2,3])**2)), ArmMs[0].tf[2,3]-Tlist[1][2,3]
    # get relative location of whisker joint in plane
    x_3, y_3 = np.sqrt(np.sum((whisk_joint.tf[0:2,3]-Tlist[1][0:2,3])**2)), whisk_joint.tf[2,3]-Tlist[1][2,3]

    # get slope of wire
    m = (y_2-y_1)/(x_2-x_1)

    # find the intersection point on the bottom side of whisker
    ip = collision.tf[0:3,3] - collision.tf[0:3,2]*0.195 + collision.tf[0:3,1]*46.231/2

    # find radius of circle
    whisk_chord = ip - whisk_joint.tf[0:3,3]
    r = np.sqrt(np.sum(whisk_chord**2))

    # solve intersection of circle and line (and take solution with greater z)
    a = 1 + m**2
    b = -2*x_3-2*y_3*m
    c = x_3**2 + y_3**2 - r**2

    # find the coincident points in plane
    x_c = (-b + np.sqrt(b**2 - 4*a*c))/(2*a)
    y_c = m*x_c

    # find the length of the wire to the coincident point
    wire_len = np.sqrt(x_c**2 + y_c**2)

    # find the 3D intersection point by tracing the wire
    wire_vec = ArmMs[0].tf[0:3,3] - Tlist[1][0:3,3]
    wire_unit = wire_vec / np.linalg.norm(wire_vec)
    p = Tlist[1][0:3,3] + wire_unit * wire_len
    
    angled_in = np.sqrt(np.sum(ForearmMs[1].tf[0:2,3])**2) < np.sqrt(np.sum(whisk_joint.tf[0:2,3])**2)
    below_wire = ForearmMs[1].tf[2,3] < p[2]
        
    if angled_in and below_wire:
        # find the angle needed to intersect this point
        R = np.eye(3)
        y_vec = p - whisk_joint.tf[0:3,3]
        R[:,1] = y_vec / np.linalg.norm(y_vec)
        R[:,2] = np.array([[1,0,0],[0, 0,-1],[0, 1,0]]) @ R[:,1] 
        R[:,0] = np.cross(R[:,1], R[:,2])
        
        # set the joint rotation to this angle
        T = whisk_joint.tf.copy()
        T[0:3,0:3] = R
        
        # set the pose of the link
        rel_pose = whisk_joint.inv_tf @ whisker.tf

        newT = T @ rel_pose
        whisker.tf = newT.copy()
        whisker.update()
        
    # Find the antenna position
    
    angled_in = np.sqrt(np.sum(ForearmMs[0].tf[0:2,3])**2) < np.sqrt(np.sum(ant_joint.tf[0:2,3])**2)
    below_whisker = ForearmMs[0].tf[2,3] < ForearmMs[1].tf[2,3]
    
    if angled_in and below_whisker:
        # find the top face of the whisker
        p = collision.tf[0:3,3] + collision.tf[0:3,2]*0.195 + collision.tf[0:3,1]*46.231/2
        
        # find the angle needed to intersect this point
        R = np.eye(3)
        y_vec = p - ant_joint.tf[0:3,3]
        R[:,1] = y_vec / np.linalg.norm(y_vec)
        R[:,2] = np.array([[1,0,0],[0, 0,-1],[0, 1,0]]) @ R[0:3,1] 
        R[:,0] = np.cross(R[0:3,1], R[0:3,2])
        
        # set the joint rotation to this angle
        T = ant_joint.tf.copy()
        T[0:3,0:3] = R
        
        # set the pose of the link
        rel_pose = ant_joint.inv_tf @ antenna.tf

        newT = T @ rel_pose
        antenna.tf = newT.copy()
        antenna.update()
        
    # Find the wire connections
    
    verts = []
    verts.append(Tlist[2][0:3,3])
    
    # is ant attached?
    
    e1 = ant_M.tf[0:3,1]
    p1 = ant_M.tf[0:3,3]

    p2 = wire_pt.tf[0,3]
    e2 = wire_pt.tf[0:3,3] - Tlist[2][0:3,3]
    e2 /= np.linalg.norm(e2)

    n = np.cross(e1,e2)
    n2 = np.cross(n,e2)
    c1 = p1 + (np.dot(p2-p1, n2)/np.dot(e1, n2)) * e1
    
    ant_attached = ant_M.tf[2,3] > c1[2]
    
    if ant_attached:
        verts.append(ant_M.tf[0:3,3])
    
        # is whisk attached?

        e3 = whisk_M.tf[0:3,1]
        p3 = whisk_M.tf[0:3,3]

        p4 = wire_pt.tf[0,3]
        e4 = ant_M.tf[0:3,3] - wire_pt.tf[0:3,3]
        e4 /= np.linalg.norm(e4)

        n3 = np.cross(e3,e4)
        n4 = np.cross(n3,e4)
        c2 = p3 + (np.dot(p4-p3, n4)/np.dot(e3, n4)) * e3

        whisk_attached = whisk_M.tf[2,3] > c2[2]
    
        if whisk_attached:
            verts.append(whisk_M.tf[0:3,3])
            
    verts.append(wire_pt.tf[0:3,3])
    
    verts = np.array(verts)
    print(why)
    why, = assm.ax.plot(*verts, 'k')
    
#     print(tuple(np.array(verts)))
#     wires2._verts3d = tuple(np.array(verts.copy()))