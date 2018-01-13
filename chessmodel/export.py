import os
import tensorflow as tf
import shutil
from options import *
from model import Model

def export_model(sess, export_path_base, version=1.4):
    if not os.path.isdir(export_path_base):
        os.makedirs(export_path_base)
    export_path = os.path.join(
          tf.compat.as_bytes(export_path_base),
          tf.compat.as_bytes(str(version)))
    print('Exporting trained model to', export_path)
    if os.path.isdir(export_path):
        shutil.rmtree(export_path)
    builder = tf.saved_model.builder.SavedModelBuilder(export_path)
    builder.add_meta_graph_and_variables(sess, [tf.saved_model.tag_constants.SERVING])
    builder.save()

tf.reset_default_graph()

with tf.Session() as sess:
    saver = tf.train.import_meta_graph(os.path.join(FLAGS.output_dir, 'model.ckpt-0.meta'))
    saver.restore(sess, tf.train.latest_checkpoint(FLAGS.output_dir))
    export_model(sess, os.path.join('.', 'model'))
