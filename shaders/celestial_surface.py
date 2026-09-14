"""Procedural galactic surfaces for the sculptural reference direction.

All textures are shader math, noise and Voronoi fields: no image assets.
"""
import bpy
from shaders.divine_glow import driver,time_expression

class Graph:
    def __init__(self,tree): self.n=tree.nodes; self.l=tree.links
    def node(self,kind): return self.n.new(kind)
    def put(self,value,socket):
        if hasattr(value,'node'): self.l.new(value,socket)
        else:
            if socket.type=='RGBA' and isinstance(value,(int,float)): value=(value,value,value,1)
            socket.default_value=value
    def math(self,operation,a,b=None):
        n=self.node('ShaderNodeMath'); n.operation=operation
        self.put(a,n.inputs[0])
        if b is not None: self.put(b,n.inputs[1])
        return n.outputs[0]
    def vector(self,operation,a,b=None):
        n=self.node('ShaderNodeVectorMath'); n.operation=operation
        self.put(a,n.inputs[0])
        if b is not None: self.put(b,n.inputs[1])
        return n.outputs['Value'] if operation in ('LENGTH','DISTANCE','DOT_PRODUCT') else n.outputs['Vector']
    def scale(self,vec,factor):
        n=self.node('ShaderNodeVectorMath'); n.operation='SCALE'; self.put(vec,n.inputs[0]); self.put(factor,n.inputs['Scale']); return n.outputs[0]
    def noise(self,vec,scale,detail=3,settings=None):
        n=self.node('ShaderNodeTexNoise'); n.noise_dimensions='4D'
        self.put(vec,n.inputs['Vector']); n.inputs['Scale'].default_value=scale; n.inputs['Detail'].default_value=detail
        if settings: driver(n.inputs['W'],f'{time_expression(settings)}*.022')
        return n.outputs['Fac']
    def ramp(self,value,stops):
        n=self.node('ShaderNodeValToRGB'); r=n.color_ramp
        for e in list(r.elements)[2:]: r.elements.remove(e)
        for i,(p,c) in enumerate(stops):
            e=r.elements[i] if i<2 else r.elements.new(p); e.position=p; e.color=(*c,1)
        self.put(value,n.inputs[0]); return n.outputs['Color']
    def color(self,operation,a,b,factor=1):
        n=self.node('ShaderNodeMixRGB'); n.blend_type=operation
        n.inputs[0].default_value=factor; self.put(a,n.inputs[1]); self.put(b,n.inputs[2]); return n.outputs[0]

def spiral(g,coordinate,settings,turns=11.5):
    """Density, emissive color and radius of a logarithmic multi-arm galaxy."""
    separate=g.node('ShaderNodeSeparateXYZ'); g.put(coordinate,separate.inputs[0])
    x,y=separate.outputs['X'],separate.outputs['Y']
    radius=g.math('SQRT',g.math('ADD',g.math('MULTIPLY',x,x),g.math('MULTIPLY',y,y)))
    theta=g.math('ARCTAN2',y,x)
    turbulence=g.noise(coordinate,7,4,settings)
    angle=g.math('ADD',g.math('MULTIPLY',theta,3),g.math('MULTIPLY',g.math('LOGARITHM',g.math('ADD',radius,.085),2.71828),turns))
    angle=g.math('ADD',angle,g.math('MULTIPLY',turbulence,2.5))
    # Broad luminous arms with dust lanes, like the reference's photographic spirals.
    stripe=g.math('POWER',g.math('ADD',.5,g.math('MULTIPLY',.5,g.math('SINE',angle))),1.8)
    fall=g.math('MAXIMUM',0,g.math('SUBTRACT',1,g.math('MULTIPLY',radius,.75)))
    clouds=g.noise(coordinate,22,5,settings)
    filaments=g.noise(coordinate,85,3,settings)
    clumps=g.math('MULTIPLY',g.math('POWER',clouds,1.6),2.6)
    structure=g.math('MULTIPLY',clumps,g.math('MULTIPLY',filaments,1.3))
    density=g.math('MULTIPLY',g.math('MULTIPLY',stripe,g.math('POWER',fall,1.4)),structure)
    disc=g.math('MULTIPLY',g.math('EXPONENT',g.math('MULTIPLY',radius,-3.5)),g.math('ADD',.25,g.math('MULTIPLY',stripe,.6)))
    density=g.math('ADD',density,g.math('MULTIPLY',disc,.55))
    core=g.math('ADD',g.math('EXPONENT',g.math('MULTIPLY',radius,-23)),g.math('MULTIPLY',g.math('EXPONENT',g.math('MULTIPLY',radius,-8)),.35))
    palette=g.ramp(clouds,[(.18,(.006,.015,.05)),(.36,(.03,.09,.24)),(.5,(.21,.12,.3)),(.65,(.55,.4,.35)),(.83,(.9,.67,.34))])
    color=g.color('MULTIPLY',palette,g.math('MULTIPLY',density,2.2))
    gold=g.color('MULTIPLY',(1,.48,.12,1),g.math('MULTIPLY',core,3))
    cellular=g.node('ShaderNodeTexVoronoi'); cellular.inputs['Scale'].default_value=95
    g.put(coordinate,cellular.inputs['Vector'])
    stellar=g.math('POWER',g.math('MAXIMUM',0,g.math('SUBTRACT',1,g.math('MULTIPLY',cellular.outputs['Distance'],7))),4)
    stellar=g.math('MULTIPLY',stellar,g.math('MULTIPLY',density,40))
    stars=g.color('MULTIPLY',(.64,.76,1,1),stellar)
    return g.math('ADD',density,core),g.color('ADD',g.color('ADD',color,gold),stars),radius

def celestial(name,settings,window=(8,65),galaxy_scale=1.8,gilded=0.0):
    mat=bpy.data.materials.new(name); mat.use_nodes=True; mat.surface_render_method='DITHERED'
    tree=mat.node_tree; tree.nodes.clear(); g=Graph(tree)
    out=g.node('ShaderNodeOutputMaterial'); geo=g.node('ShaderNodeNewGeometry')
    tex=g.node('ShaderNodeTexCoord')
    # World-space cloud field is continuous across anatomical mesh joints.
    pos=geo.outputs['Position']; large=g.noise(pos,1.4,5,settings); fine=g.noise(pos,8,3,settings)
    palette=g.ramp(large,[(.18,(.001,.002,.008)),(.34,(.004,.013,.035)),(.46,(.018,.055,.13)),(.56,(.14,.07,.19)),(.68,(.10,.23,.38)),(.83,(.40,.32,.25))])
    local=g.vector('SUBTRACT',tex.outputs['Generated'],(.5,.5,.5))
    local=g.scale(local,galaxy_scale)
    density,galaxy,_=spiral(g,local,settings)
    # Small cellular points read as stellar sparks on the skin of the universe.
    vor=g.node('ShaderNodeTexVoronoi'); vor.distance='EUCLIDEAN'; vor.feature='F1'
    g.put(pos,vor.inputs['Vector']); vor.inputs['Scale'].default_value=48
    star=g.math('POWER',g.math('MAXIMUM',0,g.math('SUBTRACT',1,g.math('MULTIPLY',vor.outputs['Distance'],8))),5)
    facing=g.node('ShaderNodeLayerWeight'); facing.inputs['Blend'].default_value=.25
    rim=g.math('POWER',facing.outputs['Facing'],4)
    rim=g.math('MULTIPLY',rim,g.math('ADD',.28,g.math('MULTIPLY',fine,1.4)))
    # Gold veins occur on only a narrow band of a higher-frequency field.
    veins=g.math('POWER',g.math('MAXIMUM',0,g.math('SUBTRACT',1,g.math('MULTIPLY',g.math('ABSOLUTE',g.math('SUBTRACT',fine,.54)),45))),4)
    veins=g.math('MULTIPLY',veins,g.math('POWER',large,3))
    gold=g.color('MULTIPLY',(1,.45,.12,1),g.math('ADD',g.math('MULTIPLY',rim,5.0),g.math('MULTIPLY',veins,.16)))
    starlight=g.color('MULTIPLY',(.75,.82,1,1),g.math('MULTIPLY',star,18))
    galaxy_strength=.12 if name.endswith('face') else (.55 if name.endswith('arms') else 1.05)
    emission=g.color('ADD',g.color('ADD',g.color('MULTIPLY',galaxy,galaxy_strength),gold),starlight)
    # Faint nebular body glow keeps the form translucent-luminous rather than a dark statue.
    emission=g.color('ADD',emission,g.color('MULTIPLY',palette,.14))
    if gilded:
        emission=g.color('ADD',emission,g.color('MULTIPLY',(1,.55,.2,1),g.math('MULTIPLY',g.math('ADD',.3,fine),gilded)))
    base=g.color('ADD',palette,g.color('MULTIPLY',galaxy,.15))
    bsdf=g.node('ShaderNodeBsdfPrincipled'); g.put(g.color('MULTIPLY',base,.17),bsdf.inputs['Base Color'])
    bsdf.inputs['Metallic'].default_value=.02; bsdf.inputs['Roughness'].default_value=.9
    if 'Specular IOR Level' in bsdf.inputs: bsdf.inputs['Specular IOR Level'].default_value=.12
    g.put(emission,bsdf.inputs['Emission Color']); bsdf.inputs['Emission Strength'].default_value=1.5
    bump=g.node('ShaderNodeBump'); bump.inputs['Strength'].default_value=.13; bump.inputs['Distance'].default_value=.055
    g.put(fine,bump.inputs['Height']); g.put(bump.outputs[0],bsdf.inputs['Normal'])
    # A traveling, noise-broken material boundary assembles actual surface area.
    progress=g.node('ShaderNodeValue'); progress.label='Anatomical manifestation'
    t=time_expression(settings); start,end=window
    driver(progress.outputs[0],f'min(1.1,max(-.1,({t}-{start})/{max(.1,end-start)}*1.2-.1))')
    split=g.node('ShaderNodeSeparateXYZ'); g.put(tex.outputs['Generated'],split.inputs[0])
    threshold=g.math('ADD',g.math('MULTIPLY',g.math('SUBTRACT',1,split.outputs['Y']),.8),g.math('MULTIPLY',large,.2))
    visible=g.math('GREATER_THAN',progress.outputs[0],threshold)
    transparent=g.node('ShaderNodeBsdfTransparent'); mix=g.node('ShaderNodeMixShader')
    g.put(visible,mix.inputs[0]); g.put(transparent.outputs[0],mix.inputs[1]); g.put(bsdf.outputs[0],mix.inputs[2]); g.put(mix.outputs[0],out.inputs['Surface'])
    return mat

def galaxy_disc(name,settings):
    mat=bpy.data.materials.new(name); mat.use_nodes=True; mat.surface_render_method='BLENDED'
    mat.node_tree.nodes.clear(); g=Graph(mat.node_tree)
    out=g.node('ShaderNodeOutputMaterial'); tex=g.node('ShaderNodeTexCoord')
    coord=g.scale(g.vector('SUBTRACT',tex.outputs['Generated'],(.5,.5,0)),2.4)
    density,color,radius=spiral(g,coord,settings,13.0)
    emit=g.node('ShaderNodeEmission'); g.put(color,emit.inputs['Color']); emit.inputs['Strength'].default_value=3
    trans=g.node('ShaderNodeBsdfTransparent'); mix=g.node('ShaderNodeMixShader')
    alpha=g.math('MINIMUM',1,g.math('MULTIPLY',density,1.5))
    g.put(alpha,mix.inputs[0]); g.put(trans.outputs[0],mix.inputs[1]); g.put(emit.outputs[0],mix.inputs[2]); g.put(mix.outputs[0],out.inputs[0])
    return mat

def rich_cloud(name,settings):
    mat=bpy.data.materials.new(name); mat.use_nodes=True; mat.surface_render_method='BLENDED'
    mat.node_tree.nodes.clear(); g=Graph(mat.node_tree)
    out=g.node('ShaderNodeOutputMaterial'); tex=g.node('ShaderNodeTexCoord')
    raw=tex.outputs['Generated']; split=g.node('ShaderNodeSeparateXYZ'); g.put(raw,split.inputs[0])
    xy=g.node('ShaderNodeCombineXYZ'); g.put(split.outputs['X'],xy.inputs['X']); g.put(split.outputs['Y'],xy.inputs['Y'])
    # Larger billows and wider ridges avoid a uniform mottled texture behind the figure.
    coord=xy.outputs[0]; broad=g.noise(coord,2.6,6,settings); detail=g.noise(coord,17,6,settings)
    ridge=g.math('POWER',g.math('MAXIMUM',0,g.math('SUBTRACT',1,g.math('MULTIPLY',g.math('ABSOLUTE',g.math('SUBTRACT',broad,.52)),4))),2.4)
    mask=g.math('MULTIPLY',ridge,g.math('MULTIPLY',g.math('POWER',detail,3.4),1.35))
    radial=g.vector('DISTANCE',coord,(.5,.5,0))
    fall=g.math('MAXIMUM',0,g.math('SUBTRACT',1,g.math('MULTIPLY',radial,1.9)))
    mask=g.math('MULTIPLY',mask,g.math('MULTIPLY',fall,2))
    color=g.ramp(detail,[(.15,(.004,.01,.03)),(.35,(.02,.06,.15)),(.5,(.08,.21,.40)),(.62,(.27,.15,.31)),(.77,(.65,.42,.24)),(.92,(1,.7,.35))])
    emit=g.node('ShaderNodeEmission'); g.put(color,emit.inputs['Color']); emit.inputs['Strength'].default_value=2
    trans=g.node('ShaderNodeBsdfTransparent'); mix=g.node('ShaderNodeMixShader')
    g.put(mask,mix.inputs[0]); g.put(trans.outputs[0],mix.inputs[1]); g.put(emit.outputs[0],mix.inputs[2]); g.put(mix.outputs[0],out.inputs[0])
    return mat
