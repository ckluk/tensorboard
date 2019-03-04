# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Dumps demo data for the profile dashboard.

The data for profile plugin data is not generated by tensorflow workflow at this
point, so we simply dump the embedded raw data to the log directory.

TODO(ioeric): demonstrate how to setup the plugin when API for writing the data
is available.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import shutil

from absl import app
import tensorflow as tf

from google.protobuf import text_format
from tensorboard.backend.event_processing import plugin_asset_util
from tensorboard.plugins.profile import profile_demo_data
from tensorboard.plugins.profile import profile_plugin
from tensorboard.plugins.profile import trace_events_pb2


tf.compat.v1.enable_eager_execution()


# Directory into which to write tensorboard data.
LOGDIR = '/tmp/profile_demo'


# Suffix for the empty eventfile to write. Should be kept in sync with TF
# profiler kProfileEmptySuffix constant defined in:
#   tensorflow/core/profiler/rpc/client/capture_profile.cc.
EVENT_FILE_SUFFIX = '.profile-empty'


def _maybe_create_directory(directory):
  try:
    os.makedirs(directory)
  except OSError:
    print('Directory %s already exists.' %directory)


def write_empty_event_file(logdir):
  w = tf.compat.v2.summary.create_file_writer(
      logdir, filename_suffix=EVENT_FILE_SUFFIX)
  w.close()


def dump_data(logdir):
  """Dumps plugin data to the log directory."""
  # Create a tfevents file in the logdir so it is detected as a run.
  write_empty_event_file(logdir)

  plugin_logdir = plugin_asset_util.PluginDirectory(
      logdir, profile_plugin.ProfilePlugin.plugin_name)
  _maybe_create_directory(plugin_logdir)

  for run in profile_demo_data.RUNS:
    run_dir = os.path.join(plugin_logdir, run)
    _maybe_create_directory(run_dir)
    if run in profile_demo_data.TRACES:
      with open(os.path.join(run_dir, 'trace'), 'w') as f:
        proto = trace_events_pb2.Trace()
        text_format.Merge(profile_demo_data.TRACES[run], proto)
        f.write(proto.SerializeToString())

    if run not in profile_demo_data.TRACE_ONLY:
      shutil.copyfile('tensorboard/plugins/profile/profile_demo.op_profile.json',
                      os.path.join(run_dir, 'op_profile.json'))
      shutil.copyfile(
          'tensorboard/plugins/profile/profile_demo.memory_viewer.json',
          os.path.join(run_dir, 'memory_viewer.json'))
      shutil.copyfile(
          'tensorboard/plugins/profile/profile_demo.google_chart_demo.json',
          os.path.join(run_dir, 'google_chart_demo.json'))
      shutil.copyfile(
          'tensorboard/plugins/profile/profile_demo.end_2_end.json',
          os.path.join(run_dir, 'end_2_end.json'))

  # Unsupported tool data should not be displayed.
  run_dir = os.path.join(plugin_logdir, 'empty')
  _maybe_create_directory(run_dir)
  with open(os.path.join(run_dir, 'unsupported'), 'w') as f:
    f.write('unsupported data')


def main(unused_argv):
  print('Saving output to %s.' % LOGDIR)
  dump_data(LOGDIR)
  print('Done. Output saved to %s.' % LOGDIR)


if __name__ == '__main__':
  app.run(main)
