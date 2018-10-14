import os.path

import numpy as np
from keras.callbacks import ModelCheckpoint

from model.autoencoder import conv_ae_1d
from preprocessing.audio_import import array_to_audio
from preprocessing.generator import audio_segment_generator, audio_segments_from_single_file

encoder_setup = [
    (64, (5), 4),
    (128, (5), 4),
    (256, (5), 4),
    (256, (5), 2),
    (512, (5), 2)
]

decoder_setup = [
    (512, (5), 2),
    (256, (5), 2),
    (256, (5), 4),
    (128, (5), 4),
    (64, (5), 4)
]

model = conv_ae_1d(input_shape=(16384, 1), encoder_setup=encoder_setup, decoder_setup=decoder_setup)
print(model.summary())

b = audio_segment_generator(16384, 256, 'train', 'mp3')
d = next(b)
print(d[0].shape)

model.compile(optimizer='sgd', loss='mse')

checkpoint_path = os.path.join('checkpoints', 'epoch-{epoch:02d}-{loss:.4f}.hdf5')
checkpoint = ModelCheckpoint(checkpoint_path, monitor='loss', verbose=1, save_best_only=True, mode='min')

model.fit_generator(b, epochs=2, steps_per_epoch=100, callbacks=[checkpoint])

validation_samples = audio_segments_from_single_file(16384, 'nocturne.mp3')

preds = np.array([], dtype=np.int16)

for s in validation_samples:
    pred = model.predict(np.expand_dims(np.expand_dims(s, -1), 0))
    preds = np.append(preds, (pred * 16384).astype(np.int16))

array_to_audio(preds, 'mix')
# lstm_model = conv_lstm_ae_1d(timesteps=10, input_shape=(16384, 1), encoder_setup=encoder_setup, lstm_num=2,
#                              decoder_setup=decoder_setup)
# print(lstm_model.summary())
