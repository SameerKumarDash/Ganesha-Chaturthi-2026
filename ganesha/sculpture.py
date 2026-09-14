"""Modeled celestial anatomy, replacing the vector-outline presentation."""
import math
import random
import bpy
from mathutils import Vector
from setup_scene import collection,sphere
from shaders.celestial_surface import celestial
from shaders.divine_glow import emission
from animation.timeline import frame

# Rounded tiered mukut: (height, half-width, half-height, depth) of each fused shell.
CROWN_TIERS=((4.32,1.18,.48,.78),(4.78,1.08,.46,.70),(5.20,.90,.42,.58),(5.58,.68,.36,.44),(5.90,.44,.30,.30),(6.16,.21,.24,.17))

def smooth_samples(anchors,steps=8):
    points=[Vector(p[:3]) for p in anchors]; radii=[p[3] for p in anchors]
    result=[]
    for i in range(len(points)-1):
        a=points[max(0,i-1)]; b=points[i]; c=points[i+1]; d=points[min(len(points)-1,i+2)]
        for k in range(steps):
            t=k/steps
            co=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
            radius=radii[i]+(radii[i+1]-radii[i])*(t*t*(3-2*t))
            result.append((co,radius))
    result.append((points[-1],radii[-1])); return result

def tube(name,anchors,mat,col,sides=20,steps=8):
    sampled=smooth_samples(anchors,steps); verts=[]; faces=[]
    for i,(co,r) in enumerate(sampled):
        tangent=(sampled[min(i+1,len(sampled)-1)][0]-sampled[max(0,i-1)][0]).normalized()
        guide=Vector((0,0,1))
        if abs(tangent.dot(guide))>.95: guide=Vector((0,1,0))
        u=tangent.cross(guide).normalized(); v=tangent.cross(u).normalized()
        for j in range(sides):
            angle=j*math.tau/sides
            verts.append(tuple(co+r*(u*math.cos(angle)+v*math.sin(angle))))
        if i:
            for j in range(sides):
                a=(i-1)*sides+j; b=(i-1)*sides+(j+1)%sides
                faces.append((a,b,b+sides,a+sides))
    faces.extend([tuple(reversed(range(sides))),tuple(range((len(sampled)-1)*sides,len(sampled)*sides))])
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); col.objects.link(obj); mesh.materials.append(mat)
    for p in mesh.polygons: p.use_smooth=True
    return obj

def filament(name,points,mat,col,radius=.012,closed=False):
    curve=bpy.data.curves.new(name,'CURVE'); curve.dimensions='3D'; curve.bevel_depth=radius; curve.bevel_resolution=2
    spline=curve.splines.new('BEZIER'); spline.bezier_points.add(len(points)-1)
    for p,co in zip(spline.bezier_points,points):
        p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    spline.use_cyclic_u=closed
    obj=bpy.data.objects.new(name,curve); col.objects.link(obj); curve.materials.append(mat)
    return obj

def appear(obj,start,end,settings):
    """Hide unmanifested geometry; shader handles progressive surface emergence."""
    obj['manifest_start']=start; obj['manifest_end']=end
    for f,hidden in ((1,True),(frame(start,settings),False)):
        obj.hide_render=hidden; obj.keyframe_insert(data_path='hide_render',frame=f)
        obj.hide_viewport=hidden; obj.keyframe_insert(data_path='hide_viewport',frame=f)

def ear(name,side,mat,col):
    # A dished fan, with folded upper edge and a tapered lower lobe.
    boundary=[(1.0,3.55),(1.45,4.0),(2.2,4.22),(2.9,4.05),(3.18,3.68),(2.98,3.07),
              (2.66,2.56),(2.27,1.92),(1.79,1.72),(1.43,2.18),(1.16,2.71)]
    controls=[(side*x,y,.08,.1) for x,y in boundary]
    controls.append(controls[0]); boundary_samples=smooth_samples(controls,8)[:-1]
    center=Vector((side*2.0,2.92,.12)); count=len(boundary_samples); verts=[tuple(center)]; faces=[]
    rings=14
    for rindex in range(1,rings+1):
        u=rindex/rings
        for point,_ in boundary_samples:
            co=center.lerp(point,u)
            co.z=.02+.42*u*u+.10*math.sin(u*math.pi)
            verts.append(tuple(co))
    for j in range(count): faces.append((0,1+j,1+(j+1)%count))
    for r in range(rings-1):
        for j in range(count):
            a=1+r*count+j; b=1+r*count+(j+1)%count
            faces.append((a,b,b+count,a+count))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.materials.append(mat)
    obj=bpy.data.objects.new(name,mesh); col.objects.link(obj)
    for p in mesh.polygons: p.use_smooth=True
    solid=obj.modifiers.new('Soft ear thickness','SOLIDIFY'); solid.thickness=.14
    return obj

def fuse(name,members,material,col,voxel=.065):
    """One-time voxel union produces continuous anatomy; never runs per frame."""
    bpy.ops.object.select_all(action='DESELECT')
    for obj in members: obj.select_set(True)
    bpy.context.view_layer.objects.active=members[0]
    bpy.ops.object.join(); obj=bpy.context.object; obj.name=name
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    mod=obj.modifiers.new('Continuous anatomical union','REMESH'); mod.mode='VOXEL'; mod.voxel_size=voxel; mod.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    smooth=obj.modifiers.new('Soft anatomical transitions','SMOOTH'); smooth.factor=1.1; smooth.iterations=4
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    obj.data.materials.clear(); obj.data.materials.append(material)
    for p in obj.data.polygons: p.use_smooth=True
    return obj

def build(scene,settings):
    col=collection('Celestial anatomy',scene); ornament=collection('Sacred crown and jewelry',scene)
    mats={name:celestial('Celestial '+name,settings,window,scale,gilded) for name,window,scale,gilded in [
        ('face',(14,34),4.8,0),('ears',(15,22),1.9,0),('trunk',(27,34),3.4,0),
        ('torso',(38,48),1.8,0),('arms',(34,43),3.2,0),('hands',(39,48),2.8,0),
        ('legs',(48,58),1.9,0),('crown',(8,14),4,.28)]}
    gold=emission('Sculptural gold',(1,.52,.19),3.5)
    softgold=emission('Fine antique gold',(1,.49,.16),1.25)
    white=emission('Stellar warm core',(1,.84,.55),7)
    black=emission('Serene eye dark',(.001,.002,.006),.1)
    objects=[]
    def body(name,pos,scale,category):
        obj=sphere(name,pos,1,mats[category],col,48 if settings.quality!='LOW' else 32,24)
        obj.scale=scale; objects.append(obj); return obj
    body('Full rounded celestial torso',(0,.05,0),(1.48,1.85,.88),'torso')
    body('Shoulder chest',(0,1.30,.02),(1.60,.83,.71),'torso')
    body('Elephant head',(0,3.15,.22),(1.16,1.40,.87),'face')
    for side in (-1,1):
        body('Sculpted cheek',(side*.69,2.65,.51),(.51,.72,.52),'face')
        objects.append(ear('Celestial elephant ear',side,mats['ears'],col))
    trunk=tube('Sweeping sculpted trunk',[(0,3.64,.58,.28),(0,3.11,.83,.43),(-.04,2.27,1.06,.43),(-.10,1.50,1.19,.37),
        (.12,.91,1.33,.33),(.65,.55,1.43,.30),(1.12,.26,1.53,.27),(1.27,-.12,1.60,.23),
        (.98,-.48,1.66,.19),(.55,-.45,1.72,.155),(.48,-.14,1.74,.12),(.72,-.04,1.74,.085),(.88,-.18,1.77,.025)],mats['trunk'],col,28,10)
    objects.append(trunk)
    # Sculptural tusks taper and curve, rather than planar outline wedges.
    tuskmat=bpy.data.materials.new('Warm ivory starlight'); tuskmat.use_nodes=True
    bs=tuskmat.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(.75,.49,.22,1)
    bs.inputs['Roughness'].default_value=.23; bs.inputs['Emission Color'].default_value=(1,.61,.25,1); bs.inputs['Emission Strength'].default_value=.7
    for side,length in [(-1,1),(1,.60)]:
        obj=tube('Celestial tusk',[(side*.67,2.42,.92,.17),(side*.81,2.03,1.07,.12),(side*(.84+.1*length),2.02-.29*length,1.23,.007)],tuskmat,col,20,10)
        appear(obj,27,34,settings)
    # Relaxed eyes: inset dark almond surfaces, fine curved upper lids.
    for side in (-1,1):
        eye=sphere('Calm almond eye',(side*.61,3.10,1.005),1,black,col,32,16)
        eye.scale=(.235,.043,.065); eye.rotation_euler.z=side*.08
        appear(eye,22,27,settings)
        lid=filament('Serene luminous eyelid',[(side*.35,3.13,1.028),(side*.56,3.085,1.087),(side*.80,3.125,1.008)],softgold,ornament,.013)
        appear(lid,22,27,settings)
        iris=sphere('Warm quiet eye glint',(side*.61,3.075,1.083),.025,softgold,ornament,12,8); appear(iris,23,27,settings)
        brow=body('Sculpted brow',(side*.61,3.25,.97),(.34,.075,.075),'face'); brow.rotation_euler.z=side*.06
    # Tilak and bindu, applied just above the physical face.
    for pts in [[(-.17,3.73,1.012),(-.12,3.50,1.11),(0,3.44,1.13),(.12,3.50,1.11),(.17,3.73,1.012)],[(0,3.84,.99),(0,3.54,1.13)]]:
        obj=filament('Sacred tilak',pts,gold,ornament,.018); appear(obj,22,27,settings)
    bindu=sphere('Tilak bindu',(0,3.29,1.16),.049,white,ornament,16,8); appear(bindu,25,27,settings)
    # Four arms, rising rear hands and forward blessing / offering hands.
    for side in (-1,1):
        rear=tube('Raised rear arm',[(side*1.20,1.39,-.15,.43),(side*1.85,1.02,-.24,.39),(side*2.67,1.02,-.20,.31),
            (side*3.10,1.52,-.08,.27),(side*3.18,2.13,.02,.23)],mats['arms'],col,24,10); objects.append(rear)
        front=tube('Forward lower arm',[(side*1.21,.86,.17,.45),(side*1.87,.21,.33,.37),(side*2.55,.12,.55,.31),
            (side*2.64,.72,.84,.25)],mats['arms'],col,24,10); objects.append(front)
    # Blessing palm with individually modeled, rounded fingers.
    body('Blessing palm',(-2.52,1.24,1.02),(.40,.55,.22),'hands')
    for i,(x,height) in enumerate([(-2.84,.72),(-2.64,.97),(-2.43,1.04),(-2.22,.86)]):
        obj=tube('Blessing finger',[(x,1.47,1.06,.102),(x-.03,1.80,1.12,.098),(x-.04,1.47+height,1.06,.055),(x-.04,1.52+height,1.03,.015)],mats['hands'],col,16,8); objects.append(obj)
    objects.append(tube('Blessing thumb',[(-2.20,1.04,1.04,.14),(-2.0,1.29,1.13,.12),(-1.98,1.61,1.12,.07)],mats['hands'],col,18,8))
    # Offering hand, curved upward beneath the lotus.
    body('Offering palm',(2.54,.96,.98),(.46,.27,.28),'hands')
    for i in range(4):
        x=2.24+i*.17
        objects.append(tube('Offering finger',[(x,.99,1.02,.09),(x+.08,1.18,1.21,.085),(x+.04,1.43,1.20,.055)],mats['hands'],col,14,8))
    objects.append(tube('Offering thumb',[(2.15,.84,1.03,.13),(2.02,1.10,1.20,.11),(2.13,1.25,1.25,.06)],mats['hands'],col,14,8))
    for side in (-1,1):
        body('Rear holding palm',(side*3.15,2.41,.07),(.29,.40,.22),'hands')
        for i in range(4):
            x=side*(2.94+i*.13)
            objects.append(tube('Rear curled finger',[(x,2.52,.10,.075),(x,2.80,.21,.074),(x-side*.05,2.79,.36,.06),(x-side*.08,2.63,.39,.025)],mats['hands'],col,12,7))
    # Crossed thighs have full volume, with one ankle sweeping in front.
    for side in (-1,1):
        leg=body('Folded cosmic thigh',(side*1.23,-1.93,.15),(1.62,.68,.79),'legs'); leg.rotation_euler.z=side*.24
    objects.append(tube('Crossed lower leg',[(-2.21,-2.0,.38,.48),(-1.51,-2.24,.80,.44),(-.54,-2.60,1.01,.36),(.42,-2.71,1.12,.25)],mats['legs'],col,24,10))
    body('Forward celestial foot',(.74,-2.65,1.15),(.65,.26,.31),'legs')
    objects.append(tube('Second folded shin',[(2.08,-2.12,.32,.43),(1.59,-2.52,.57,.38),(.77,-2.97,.73,.29),(-.09,-3.04,.96,.20)],mats['legs'],col,24,10))
    body('Second celestial foot',(-.48,-3.04,1.02),(.54,.24,.25),'legs')
    # Conical multi-tier crown, actual ellipsoidal shells and detailed filigree.
    for i,(y,rx,ry,rz) in enumerate(CROWN_TIERS):
        body('Celestial crown tier',(0,y,.12),(rx,ry,rz),'crown')
        points=[(rx*math.cos(a),y+.13*math.sin(a),.16+rz*math.sin(a)) for a in [j*math.tau/96 for j in range(96)]]
        obj=filament('Crown gilded circlet',points,softgold,ornament,.012,True); appear(obj,8,14,settings)
        for j in range(12):
            a=j*math.tau/12
            gem=sphere('Crown pearl',(rx*math.cos(a),y+.03,.16+rz*math.sin(a)),.033,white,ornament,10,6); appear(gem,8,14,settings)
    # Sparse vertical ribs only: dense loop filigree read as a wire cage against the reference mukut.
    for j in range(7):
        angle=-1.2+j*2.4/6
        pts=[]
        for i in range(30):
            u=i/29; r=1.15*(1-u)**.62+.03
            pts.append((r*math.sin(angle),4.23+u*2.15,.18+.78*(1-u)*math.cos(angle)))
        obj=filament('Crown vertical filigree',pts,softgold,ornament,.008); appear(obj,8,14,settings)
    for y,r in [(4.25,.115),(4.85,.085),(5.40,.065)]:
        gem=sphere('Central crown jewel',(0,y,.96-(y-4.25)*.36),r,white,ornament,20,12); appear(gem,8,14,settings)
        for scale in (1.7,2.2):
            points=[(r*scale*math.sin(a),y+r*scale*math.cos(a),.94-(y-4.25)*.36) for a in [j*math.tau/8 for j in range(8)]]
            obj=filament('Crown jeweled mandala',points,softgold,ornament,.012,True); appear(obj,8,14,settings)
    # Necklaces and bracelets add readable specular detail without outlining anatomy.
    for r in (1.10,1.30):
        pts=[(r*math.sin(a),1.42-.63*math.cos(a),.79+.16*math.cos(a)) for a in [-1.5+j*3/64 for j in range(65)]]
        obj=filament('Devotional necklace',pts,softgold,ornament,.014); appear(obj,43,48,settings)
        for i,p in enumerate(pts[::3]):
            gem=sphere('Necklace bead',p,.031,softgold,ornament,10,6); appear(gem,43,48,settings)
    for side in (-1,1):
        for y in (.71,.83):
            pts=[(side*2.59+.27*math.cos(a),y,.85+.25*math.sin(a)) for a in [j*math.tau/40 for j in range(40)]]
            obj=filament('Wrist circlet',pts,gold,ornament,.018,True); appear(obj,40,48,settings)
    # Lotus above the offering palm, sculpted petals in a small luminous blossom.
    for layer in range(2):
        for j in range(7):
            a=j*math.tau/7+layer*.4
            root=Vector((2.5,1.60,1.15)); tip=root+Vector((.56*math.cos(a),.46+.20*layer,.28*math.sin(a)))
            mid=root.lerp(tip,.5)+Vector((.13*math.sin(a),.1,.08))
            petal=tube('Lotus luminous petal',[(*root,.04),(*mid,.075),(*tip,.004)],mats['hands'],ornament,12,8); appear(petal,44,48,settings)
    # Sacred curved goad held gently in the rear left hand.
    obj=filament('Sacred curved goad',[(-3.12,2.39,.31),(-3.14,3.14,.32),(-3.34,3.74,.30),(-3.10,4.02,.30),(-2.91,3.77,.31)],gold,ornament,.032); appear(obj,39,46,settings)
    gem=sphere('Rear divine orb',(3.15,3.07,.25),.20,white,ornament,24,16); appear(gem,42,48,settings)
    # Fuse intersecting primitive forms into smooth anatomical surfaces.
    plans=[('Continuous head and trunk','face',lambda o:o.name.startswith(('Elephant head','Sculpted cheek','Sculpted brow','Sweeping sculpted trunk'))),
           ('Continuous chest and belly','torso',lambda o:o.name.startswith(('Full rounded','Shoulder chest'))),
           ('Continuous blessing hand','hands',lambda o:o.name.startswith(('Blessing palm','Blessing finger','Blessing thumb'))),
           ('Continuous offering hand','hands',lambda o:o.name.startswith(('Offering palm','Offering finger','Offering thumb'))),
           ('Unified celestial crown','crown',lambda o:o.name.startswith('Celestial crown tier'))]
    for name,category,predicate in plans:
        members=[o for o in objects if predicate(o)]
        if members:
            objects=[o for o in objects if o not in members]
            objects.append(fuse(name,members,mats[category],col,.04 if category=='hands' else .055))
    windows={'face':(14,34),'ears':(15,22),'trunk':(27,34),'torso':(38,48),'arms':(34,43),'hands':(39,48),'legs':(48,58),'crown':(8,14)}
    for obj in objects:
        key=next((k for k,m in mats.items() if obj.data.materials and obj.data.materials[0]==m),'torso')
        appear(obj,*windows[key],settings)
    return {'anatomy':objects,'collection':col,'ornaments':ornament,'gold':gold,'white':white,'guides':contour_guides()}

def ellipse_outline(cx,cy,z,rx,ry,rotation=0,start=0,sweep=math.tau,count=56):
    c,s=math.cos(rotation),math.sin(rotation); points=[]
    for i in range(count+1):
        a=start+sweep*i/count; x,y=rx*math.cos(a),ry*math.sin(a)
        points.append((cx+x*c-y*s,cy+x*s+y*c,z))
    return points

def tube_outline(anchors,steps=6):
    """Camera-facing silhouette edges of a tapered tube, without straight end caps."""
    sampled=smooth_samples(anchors,steps); left=[]; right=[]
    for i,(co,r) in enumerate(sampled):
        d=sampled[min(i+1,len(sampled)-1)][0]-sampled[max(0,i-1)][0]
        n=Vector((-d.y,d.x,0)).normalized() if d.xy.length>1e-6 else Vector((1,0,0))
        left.append(tuple(co+n*r)); right.append(tuple(co-n*r))
    return left,right

def tube_guides(g,name,category,anchors,width):
    left,right=tube_outline(anchors)
    g.append((name+' outer edge',category,left,width)); g.append((name+' inner edge',category,right,width))

def contour_guides():
    """Golden contour paths in sculpture space, mirroring the modeled anatomy above.

    Each entry is (name, manifestation category, 3D points, stroke width). The
    luminous drawing point traces these, so the outline leads each surface.
    """
    g=[]
    for i,(y,rx,ry,_) in enumerate(CROWN_TIERS):
        g.append((f'Crown tier contour {i}','crown',ellipse_outline(0,y,.14,rx,ry,count=40),2.4))
    g.append(('Head contour','face',ellipse_outline(0,3.15,.24,1.16,1.40,start=-math.pi/2,count=64),2.6))
    for side in (-1,1):
        boundary=[(1.0,3.55),(1.45,4.0),(2.2,4.22),(2.9,4.05),(3.18,3.68),(2.98,3.07),
                  (2.66,2.56),(2.27,1.92),(1.79,1.72),(1.43,2.18),(1.16,2.71)]
        anchors=[(side*x,y,.45,0) for x,y in boundary]; anchors.append(anchors[0])
        g.append(('Great ear contour','ears',[tuple(p) for p,_ in smooth_samples(anchors,6)],2.6))
    for side in (-1,1):
        g.append(('Serene eyelid contour','eyes',[(side*.35,3.13,1.05),(side*.56,3.085,1.10),(side*.80,3.125,1.03)],2.0))
    g.append(('Tilak contour','tilak',[(-.17,3.73,1.03),(-.12,3.50,1.13),(0,3.44,1.15),(.12,3.50,1.13),(.17,3.73,1.03)],2.4))
    tube_guides(g,'Trunk contour','trunk',[(0,3.11,.83,.43),(-.04,2.27,1.06,.43),(-.10,1.50,1.19,.37),
        (.12,.91,1.33,.33),(.65,.55,1.43,.30),(1.12,.26,1.53,.27),(1.27,-.12,1.60,.23),
        (.98,-.48,1.66,.19),(.55,-.45,1.72,.155),(.48,-.14,1.74,.12),(.72,-.04,1.74,.085),(.88,-.18,1.77,.025)],2.4)
    for side in (-1,1):
        tube_guides(g,'Raised arm contour','arms',[(side*1.85,1.02,-.24,.39),(side*2.67,1.02,-.20,.31),
            (side*3.10,1.52,-.08,.27),(side*3.18,2.13,.02,.23)],2.2)
        tube_guides(g,'Forward arm contour','arms',[(side*1.87,.21,.33,.37),(side*2.55,.12,.55,.31),(side*2.64,.72,.84,.25)],2.2)
    g.append(('Blessing palm contour','hands',ellipse_outline(-2.52,1.24,1.05,.40,.55,count=36),2.4))
    g.append(('Offering palm contour','hands',ellipse_outline(2.54,.96,1.0,.46,.27,count=36),2.4))
    for side in (-1,1):
        g.append(('Holding palm contour','hands',ellipse_outline(side*3.15,2.41,.1,.29,.40,count=28),2.2))
    g.append(('Chest contour','torso',ellipse_outline(0,1.30,.04,1.60,.83,start=.15,sweep=math.pi-.3,count=40),2.8))
    g.append(('Belly contour','torso',ellipse_outline(0,.05,.02,1.48,1.85,start=math.pi,sweep=math.pi,count=48),3.0))
    for side in (-1,1):
        g.append(('Folded thigh contour','legs',ellipse_outline(side*1.23,-1.93,.17,1.62,.68,side*.24,count=56),3.0))
    tube_guides(g,'Crossed shin contour','legs',[(-2.21,-2.0,.38,.48),(-1.51,-2.24,.80,.44),(-.54,-2.60,1.01,.36),(.42,-2.71,1.12,.25)],2.4)
    tube_guides(g,'Second shin contour','legs',[(2.08,-2.12,.32,.43),(1.59,-2.52,.57,.38),(.77,-2.97,.73,.29),(-.09,-3.04,.96,.20)],2.4)
    g.append(('Forward foot contour','feet',ellipse_outline(.74,-2.65,1.17,.65,.26,count=32),2.4))
    g.append(('Second foot contour','feet',ellipse_outline(-.48,-3.04,1.04,.54,.24,count=32),2.4))
    return g
