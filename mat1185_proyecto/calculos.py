from sympy import symbols, sympify, solveset, Eq, N, S, log, Pow

class FunctionAnalyzer:
    def __init__(self, expr_str, var_symbol='x'):
        expr_str = expr_str.replace('^', '**')
        self.var = symbols(var_symbol)
        self.expr = sympify(expr_str)

    def analyze(self):
        pasos = []
        dominio = S.Reals

        # Restricciones del denominador
        num, den = self.expr.as_numer_denom()
        if den != 1:
            pasos.append(f"Denominador: {den}")
            raices = solveset(Eq(den, 0), self.var, domain=S.Reals)
            pasos.append(f"Excluyendo raíces: {raices}")
            dominio = dominio - raices
        else:
            pasos.append("No hay denominador problemático.")

        # Restricciones por logaritmos
        for l in self.expr.atoms(log):
            arg = l.args[0]
            pasos.append(f"log({arg}) → argumento > 0")
            dominio = dominio.intersect(solveset(arg > 0, self.var, domain=S.Reals))

        # Restricciones por raíces pares
        for p in self.expr.atoms(Pow):
            if p.exp.is_Rational and p.exp.q % 2 == 0:
                pasos.append(f"Raíz par en {p}, base >=0")
                dominio = dominio.intersect(solveset(p.base >= 0, self.var, domain=S.Reals))

        # Intersecciones
        try:
            x_inter = solveset(Eq(self.expr, 0), self.var, dominio)
        except Exception:
            x_inter = None
        y_int = None
        if 0 in dominio:
            y_int = N(self.expr.subs(self.var, 0))

        return {
            'domain': dominio,
            'range': None,
            'x_intercepts': x_inter,
            'y_intercept': y_int,
            'steps': "\n".join(pasos)
        }

    def evaluate_at(self, x_value):
        x_expr = sympify(str(x_value))
        pasos = []
        pasos.append(f"Sustituyendo x={x_expr}")
        subs = self.expr.subs(self.var, x_expr)
        pasos.append(f"Resultado simbólico: {subs}")
        num_val = N(subs)
        pasos.append(f"Valor numérico: {num_val}")
        return {
            'x': x_expr,
            'subs_expr': subs,
            'numeric': num_val,
            'ordered_pair': (float(N(x_expr)), float(num_val)),
            'steps': "\n".join(pasos)
        }
