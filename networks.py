import abc
import os
import threading
import numpy as np
# import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, LSTM, Conv2D, \
    BatchNormalization, Dropout, MaxPooling2D, Flatten
from tensorflow.keras.optimizers import SGD


class Network:
    lock = threading.Lock()

    def __init__(self, input_dim=0, output_dim=0, lr=0.001,
                 shared_network=None, activation='sigmooid', loss='mse'):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.lr = lr
        self.shared_network = shared_network
        self.activation = activation
        self.loss = loss
        self.model = None

    def predict(self, sample):
        with self.lock:
            return self.model.predict(sample)

    def train_on_batch(self, x, y):
        loss = 0.
        with self.lock:
            loss = self.model.train_on_batch(x, y)

        return loss

    def save_model(self, model_path):
        if model_path is not None and self.model is not None:
            self.model.save_weights(model_path, overwrite=True)

    def load_model(self, model_path):
        if model_path is not None:
            self.model.load_weihts(model_path)

    @classmethod  # instance를 만들지 않아도 instance를 만든 것 처럼 class 활용 가능
    def get_shared_network(cls, net='dnn', num_steps=1, input_dim=0):
        if net == 'dnn':
            return DNN.get_network_head(Input((input_dim,)))
        elif net == 'lstm':
            return LSTMNetwork.get_network_head(
                Input((num_steps, input_dim)))
        elif net == 'cnn':
            return CNN.get_network_head(
                Input((1, num_steps, input_dim)))


class DNN(Network):
    # __init__ 의 sequence가 존재하는 이유??
    def __init__(self, *args, num_steps=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_steps = num_steps

        inp = None
        output = None

        if self.shared_network is None:
            inp = Input((self.num_steps, self.input_dim))
            output = self.get_network_head(inp).output

        else:
            inp = self.shared_network.input
            output = self.shared_network.output

        output = Dense(
            self.output_dim, activation=self.activation,
            kernel_initializer='random_normal')(output)
        self.model = Model(inp, output)
        self.model.compile(
            optimizer=SGD(lr=self.lr), loss=self.loss)

    @staticmethod  # instance를 만들지 않아도 instance를 만든 것 처럼 class 활용 가능
    def get_network_head(inp):
        output = Flatten()(inp)

        output = Dense(256, activation='sigmoid',
                       kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = Dropout(0.1)(output)

        output = Dense(128, activation='sigmoid',
                       kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = Dropout(0.1)(output)

        output = Dense(64, activation='sigmoid',
                       kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = Dropout(0.1)(output)

        output = Dense(32, activation='sigmoid',
                       kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = Dropout(0.1)(output)

        return Model(inp, output)

    def train_on_batch(self, x, y):
        x = np.array(x).reshape((-1, self.num_steps, self.input_dim))
        return super().train_on_batch(x, y)

    def predict(self, sample):
        sample = np.array(sample).reshape((1, self.num_steps, self.input_dim))
        return super().predict(sample)


class LSTMNetwork(Network):
    def __init__(self, *args, num_steps=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_steps = num_steps
        inp = None
        output = None

        if self.shared_network is None:
            inp = Input((self.num_steps, self.input_dim))
            output = self.get_network_head(inp).output
        else:
            inp = self.shared_network.input
            output = self.shared_network.output
        # output은 hidden layer를 거쳐서 온 것이고 마지막에 Dense layer로 쓸 수 있는 output으로 가공
        output = Dense(
            self.output_dim, activation=self.activation,
            kernel_initializer='random_normal')(output)
        self.model = Model(inp, output)
        self.model.compile(
            optimizer=SGD(lr=self.lr), loss=self.loss)

    @staticmethod
    def get_network_head(inp):
        output = LSTM(256, dropout=0.1,
                      return_sequences=True, stateful=False,
                      kernel_initializer='random_normal')(inp)
        output = BatchNormalization()(output)

        output = LSTM(128, dropout=0.1,
                      return_sequences=True, stateful=False,
                      kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)

        output = LSTM(64, dropout=0.1,
                      return_sequences=True, stateful=False,
                      kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)

        output = LSTM(32, dropout=0.1, stateful=False,
                      kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)

        return Model(inp, output)

    def train_on_batch(self, x, y):
        x = np.array(x).reshape((-1, self.num_steps, self.input_dim))
        return super().train_on_batch(x, y)

    def predict(self, sample):
        sample = np.array(sample).reshape((1, self.num_steps, self.input_dim))
        return super().predict(sample)


class CNN(Network):
    def __init__(self, *args, num_steps=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_steps = num_steps
        inp = None
        output = None

        if self.shared_network is None:
            inp = Input((self.num_steps, self.input_dim, 1))
            output = self.get_network_head(inp).output
        else:
            inp = self.shared_network.input
            output = self.shared_network.output

        output = Dense(
            self.output_dim, activation=self.activation,
            kernel_initializer='random_normal')(output)
        self.model = Model(inp, output)
        self.model.compile(
            optimizer=SGD(lr=self.lr), loss=self.loss)

    @staticmethod
    def get_network_head(inp):
        output = Conv2D(256, kernel_size=(1, 5),
                        padding='same', activation='sigmoid',
                        kernel_initializer='random_normal')(inp)
        output = BatchNormalization()(output)
        output = MaxPooling2D(pool_size=(1, 2))(output)
        output = Dropout(0.1)(output)

        output = Conv2D(128, kernel_size=(1, 5),
                        padding='same', activation='sigmoid',
                        kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = MaxPooling2D(pool_size=(1, 2))(output)
        output = Dropout(0.1)(output)

        output = Conv2D(64, kernel_size=(1, 5),
                        padding='same', activation='sigmoid',
                        kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = MaxPooling2D(pool_size=(1, 2))(output)
        output = Dropout(0.1)(output)

        output = Conv2D(32, kernel_size=(1, 5),
                        padding='same', activation='sigmoid',
                        kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = MaxPooling2D(pool_size=(1, 2))(output)
        output = Dropout(0.1)(output)

        output = Flatten()(output)

        return Model(inp, output)

    def train_on_batch(self, x, y):
        x = np.array(x).reshape(
            (-1, self.num_steps, self.input_dim, 1))
        return super().train_on_batch(x, y)

    def predict(self, sample):
        sample = np.array(sample).reshape(
            (-1, self.num_steps, self.input_dim, 1))
        return super().predict(sample)
