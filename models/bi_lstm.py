import tensorflow as tf
from models._embedding import Embedding_layer
from models._model_params import *


class Bi_LSTM(object):
    def __init__(self,params,train):
        self.train=train
        self.params=params
        self.embedding_layer=Embedding_layer(params['vocab_size'],params['embedding_size'])

    def build(self,inputs):
        with tf.name_scope('embed'):
            embedding_outputs=self.embedding_layer(inputs)

        if self.train:
            embedding_outputs=tf.nn.dropout(embedding_outputs,1.0)

        with tf.name_scope('bi_lstm'):
            cell_fw = tf.nn.rnn_cell.LSTMCell(self.params['lstm_hidden_size'])
            cell_fw = tf.nn.rnn_cell.DropoutWrapper(cell_fw, output_keep_prob=1.0)
            cell_bw = tf.nn.rnn_cell.LSTMCell(self.params['lstm_hidden_size'])
            cell_bw = tf.nn.rnn_cell.DropoutWrapper(cell_bw, output_keep_prob=1.0)
            all_outputs, _ = tf.nn.bidirectional_dynamic_rnn(cell_fw=cell_fw, cell_bw=cell_bw,
                                                             inputs=embedding_outputs,
                                                             sequence_length=None, dtype=tf.float32)
            all_outputs = tf.concat(all_outputs, 2)
            self.h_outputs = all_outputs[:, -1, :]

        with tf.name_scope('output'):
            self.logits = tf.layers.dense(self.h_outputs,units=params['n_class'], name="logits")

    def __call__(self,inputs,targets=None):
        self.build(inputs)
        return self.logits