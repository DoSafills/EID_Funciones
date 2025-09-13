from sympy import N

def build_explanation(analyzer, analysis, eval_res=None):
    lineas = []
    lineas.append("=== RESOLUCIÓN PASO A PASO ===")
    lineas.append("Primero vemos el dominio de la función:")
    lineas.append(str(analysis['domain']))
    lineas.append("El rango no se calculó en detalle.")

    lineas.append("Intersecciones con el eje X:")
    if analysis['x_intercepts']:
        for xi in list(analysis['x_intercepts']):
            lineas.append(f"f({xi}) = {N(analyzer.expr.subs(analyzer.var, xi))}")
    else:
        lineas.append("No hay intersecciones reales con X.")

    if analysis['y_intercept'] is not None:
        lineas.append(f"Con Y: f(0)={analysis['y_intercept']}")
    else:
        lineas.append("No hay intersección con Y.")

    if eval_res:
        xv, yv = eval_res['ordered_pair']
        lineas.append(f"Al evaluar en {xv}, f(x)≈{yv}")

    return "\n".join(lineas)
