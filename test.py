from docplex.mp.model import Model
import cplex
print(cplex.__version__)



# Create model
mdl = Model(name="simple_lp")

# Decision variables
x = mdl.continuous_var(name="x", lb=0)
y = mdl.continuous_var(name="y", lb=0)

# Objective
mdl.maximize(3*x + 5*y)

# Constraints
mdl.add_constraint(x + y <= 4)
mdl.add_constraint(x <= 2)

# Solve
solution = mdl.solve(log_output=False)  # logs solver output

# Print results
print("Objective value:", solution.objective_value)
print("x =", solution[x])
print("y =", solution[y])