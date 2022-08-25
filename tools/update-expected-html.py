#!/usr/bin/env python3
"""
usage: update-expected-html.py [-h] [--single-process] DATA_DIR

Script to update "...-expected.html" test data files with output from mjml
reference implementation (NodeJS).

positional arguments:
  DATA_DIR

options:
  -h, --help        show this help message and exit
  --single-process  run HTML generation in a single process (slower but easier
                    to debug)
"""

import argparse
from collections import namedtuple
from multiprocessing import Pool
import os
from pathlib import Path
import subprocess
import sys


Job = namedtuple('Job', ('mjml_path', 'expected_path', 'mjml_bin'))

def job_for_file(mjml_path, mjml_js):
    expected_path = mjml_path.parent / (mjml_path.stem + '-expected.html')
    return Job(
        str(mjml_path.resolve()),
        str(expected_path.resolve()),
        mjml_bin = mjml_js,
    )

def _gather_data_files_in_directory(source_dir):
    for mjml_path in source_dir.glob('*.mjml'):
        if mjml_path.name.startswith('_'):
            # "_header.mjml" / "_footer.mjml"
            continue
        yield mjml_path

def _gather_jobs(source_path, mjml_js):
    if isinstance(source_path, str):
        source_path = Path(source_path)

    if source_path.is_dir():
        for mjml_path in _gather_data_files_in_directory(source_path):
            job = job_for_file(mjml_path, mjml_js)
            yield job
    else:
        assert source_path.suffix == '.mjml'
        job = job_for_file(source_path, mjml_js)
        yield job

def _update_expected_html(job):
    mjml_cmd = str(job.mjml_bin)
    cmd = [mjml_cmd, job.mjml_path, '-o', job.expected_path]
    subprocess.run(cmd)

def detect_mjml_js():
    if 'MJML' in os.environ:
        return os.environ['MJML']
    sys.stderr.write('unable to detect mjml executable, use env variable MJML\n')
    sys.exit(20)

def main(argv=sys.argv):
    parser = argparse.ArgumentParser(
        description='''
            Script to update "...-expected.html" test data files with output from
            mjml reference implementation (NodeJS).''',
    )
    parser.add_argument('--single-process', action='store_true',
        help='run HTML generation in a single process (slower but easier to debug)')
    parser.add_argument('data_dir', metavar='DATA_DIR', type=str)
    args = parser.parse_args(args=argv[1:])
    input_ = args.data_dir

    mjml_js = detect_mjml_js()

    # ensure we are using the expected mjml version
    subprocess.run([str(mjml_js), '--version'])

    jobs = tuple(_gather_jobs(input_, mjml_js))
    if not jobs:
        sys.stderr.write('no mjml files found...\n')
    if args.single_process:
        for job in jobs:
            _update_expected_html(job)
    else:
        with Pool() as p:
            p.map(_update_expected_html, jobs)

if __name__ == '__main__':
    main()

