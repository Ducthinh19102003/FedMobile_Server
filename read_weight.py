import numpy as np

weight = np.frombuffer(open('D:\Desktop\server\FedMobile_Server\client_1_weights.bin', 'rb').read(), dtype=np.float64)

print(weight.shape)
print(f'weight: {weight}')