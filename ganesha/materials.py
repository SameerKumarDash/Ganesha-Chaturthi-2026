from shaders.divine_glow import emission, driver, time_expression

def build_materials(settings):
    t=time_expression(settings)
    gold=[]
    for i in range(4):
        mat=emission(f'Divine Gold Stroke {i}',(1,.55+.025*i,.16),2.0)
        emit=next(n for n in mat.node_tree.nodes if n.type=='EMISSION')
        driver(emit.inputs['Strength'],f'(1.6+{i}*.14)*(1+.045*sin({t}*.8+{i}))*(1+.22*min(1,max(0,({t}-58)/7)))')
        gold.append(mat)
    return {'gold':gold,'core':emission('White-Hot Core',(1,.88,.61),5),
            'aura':emission('Blue Secondary Aura',(.10,.19,.4),.4),
            'halo':emission('Halo Gold',(1,.57,.22),.7),
            'tip_gold':emission('Drawing Tip Gold',(1,.58,.2),3)}
