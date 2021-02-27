from tensorflow.keras import Sequential, layers, losses, optimizers

def build_model(vocab_size):
    model = Sequential([
        layers.Embedding(vocab_size, 1000),
        # layers.Bidirectional(layers.LSTM(64, return_sequences=True), input_shape=(None, vector_dimensions)),
        layers.Bidirectional(layers.LSTM(64)),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.5),
        # Two dense layer allow make separate predictions about each class
        layers.Dense(2)
    ])

    model.summary()
    
    model.compile(
        optimizer=optimizers.Adam(1e-4),
        loss=losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )

    return model