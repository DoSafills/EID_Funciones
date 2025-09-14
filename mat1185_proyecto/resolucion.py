from sympy import N

def build_explanation(analyzer, analysis, eval_res=None):
    lines = []
    lines.append("=== RESOLUCIÓN DIDÁCTICA ===")

    # Dominio
    lines.append(f"Dominio: {analysis.get('domain')}")

    # Rango
    lines.append(f"Rango: {analysis.get('range')}")

    # Intersecciones X
    xints = analysis.get('x_intercepts')
    if xints:
        for xi in list(xints):
            check = N(analyzer.expr.subs(analyzer.var, xi))
            lines.append(f"x = {xi} → f({xi}) = {check}")
    else:
        lines.append("No hay intersecciones reales en X.")

    # Intersección Y
    yint = analysis.get('y_intercept')
    if yint is not None:
        lines.append(f"Intersección con Y: f(0) = {yint}")
    else:
        lines.append("No hay intersección con Y.")

    # Evaluación puntual
    if eval_res:
        xv, yv = eval_res['ordered_pair'] if eval_res['ordered_pair'] else (None, None)
        if yv is None:
            lines.append(f"Evaluación en x={eval_res['x']} → No hay solución (el valor es indefinido).")
        else:
            lines.append(f"Evaluación en x={xv} → f(x)={yv}")

    return "\n".join(lines)
