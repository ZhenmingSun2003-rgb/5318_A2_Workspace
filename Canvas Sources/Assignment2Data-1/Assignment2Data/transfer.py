import numpy as np

data = np.load("X_test.npy")

np.savetxt("X_test.csv", data, delimiter=",", fmt="%.8f")