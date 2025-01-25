def plot_polynomial(expr):
    import matplotlib.pyplot as plt
    import numpy as np
    from sympy import lambdify, Poly, solve
    from mpl_toolkits.mplot3d import Axes3D

    vars = list(expr.free_symbols)
    dims = len(vars)

    colors = {'foreground': '#f8f8f2', 'comment': '#6272a4', 'purple': '#bd93f9'}
    
    def get_range(expr, var):
        deriv = expr.diff(var)
        critical_points = [p for p in solve(deriv, var) if p.is_real]
        
        try:
            deg = Poly(expr, var).degree()
            default_range = (-5, 5) if deg <= 2 else (-3, 3) if deg <= 4 else (-2, 2)
        except:
            default_range = (-5, 5)
            
        if critical_points:
            points = [float(p.evalf()) for p in critical_points]
            max_abs = max(abs(min(points)), abs(max(points)))
            return (-max_abs*1.5, max_abs*1.5)
        return default_range

    if dims == 1:
        x_range = get_range(expr, vars[0])
        plt.figure(figsize=(8, 8), facecolor='none')
        ax = plt.gca()
        ax.set_facecolor('none')

        x_points = np.linspace(x_range[0], x_range[1], 1000)
        f = lambdify(vars[0], expr, 'numpy')
        y_points = f(x_points)
        
        # Filter out infinities and nans
        mask = np.isfinite(y_points)
        x_points, y_points = x_points[mask], y_points[mask]

        if len(y_points) > 0:
            plt.plot(x_points, y_points, color=colors['purple'], linewidth=2)
            y_max = float(max(abs(np.min(y_points)), abs(np.max(y_points))))
            plt.ylim(-y_max*1.1, y_max*1.1)

        plt.grid(True, color=colors['comment'], alpha=0.3)
        plt.axhline(y=0, color=colors['comment'], alpha=0.3)
        plt.axvline(x=0, color=colors['comment'], alpha=0.3)
        
        plt.xlabel(str(vars[0]), color=colors['foreground'])
        plt.ylabel('f(' + str(vars[0]) + ')', color=colors['foreground'])

    elif dims == 2:
        x_range = get_range(expr, vars[0])
        y_range = get_range(expr, vars[1])
        
        fig = plt.figure(figsize=(8, 8), facecolor='none')
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor('none')
        
        x_points = np.linspace(x_range[0], x_range[1], 100)
        y_points = np.linspace(y_range[0], y_range[1], 100)
        X, Y = np.meshgrid(x_points, y_points)
        
        f = lambdify(vars, expr, 'numpy')
        Z = f(X, Y)
        
        # Filter out infinities and nans
        mask = np.isfinite(Z)
        if np.any(mask):
            surf = ax.plot_surface(X, Y, Z, cmap='plasma', alpha=0.8)
            fig.colorbar(surf)
        
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        
        ax.set_xlabel(str(vars[0]), color=colors['foreground'])
        ax.set_ylabel(str(vars[1]), color=colors['foreground'])
        ax.set_zlabel('f(' + str(vars[0]) + ',' + str(vars[1]) + ')', color=colors['foreground'])

    for axis in [ax.xaxis, ax.yaxis, ax.zaxis] if dims == 2 else [ax.xaxis, ax.yaxis]:
        axis.label.set_color(colors['foreground'])
        axis.set_tick_params(colors=colors['foreground'])

    return plt
from sympy import symbols, expand

t = symbols('t')
expr_1d = expand((t - 1) * (t + 2) * (t - 3))
plot_1d = plot_polynomial(expr_1d)
plot_1d.savefig('polynomial_1d.png', transparent=True)

a, b = symbols('a b')
expr_2d = a**2 + b**2 - 2*a*b
plot_2d = plot_polynomial(expr_2d)
plot_2d.savefig('polynomial_2d.png', transparent=True)

