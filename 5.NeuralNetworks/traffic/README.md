| Model | Model Configuration                              |  Loss      | Accuracy   |
|-------|--------------------------------------------------|------------|------------|
|   1   | single Conv2D(32,(3,3))                          | 1.1782     |  0.9130    |
|   2   | + MaxPooling2D(pool_size=(2, 2))                 | 0.8184     |  0.9222    |
|   3   | + 2nd Conv2d(32,(3,3))                           | 0.4915     |  0.9271    |
|   4   | 2 x Conv2D(64,(3,3)) + 1 x MaxPooling2D((2,2))   | 0.2691     |  0.9555    |
|   5   | 3 x Conv2D(64,(3,3)) + 2 x MaxPooling2D((2,2))   | 0.2339     |  0.9653    |
|   6   | + additional Dense(64, activation='relu')        | 0.1659     |  0.9606    |
|   7   | + Dropout(0.5)                                   | 0.1677     |  0.9523    |
|   8   | replace Dropout(0.3)                             | 0.1534     |  0.9602    |
|   9   | replace Dropout(0.7)                             | 3.5042     |  0.0556    |
|  10   | replace Conv2D(32,(3,3)) + 2 x Conv2D(64,(3,3))  | 0.1279     |  0.9664    |
|  --   | replace 2 x MaxPooling2D((3,3))                  | ValueError | ValueError |
|  11   | replace Dense(128, activation='relu')            | 0.1868     |  0.9658    |

## model.py ##
model-10.h5 -->  loss: 0.0887 - accuracy: 0.9760
