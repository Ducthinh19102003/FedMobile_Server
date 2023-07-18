import numpy as np

# Define the shape of the model weights
weight_shape = (3841250,)

# Set the seed for reproducibility
np.random.seed(42)

# Generate random weights for 10 clients
num_clients = 10
client_weights = []
for _ in range(num_clients):
    random_weights = np.random.randn(*weight_shape)
    client_weights.append(random_weights)

# Save the weights of each client to binary files
for i in range(num_clients):
    file_path = f"client_{i+1}_weights.bin"
    with open(file_path, "wb") as f:
        f.write(client_weights[i].tobytes())