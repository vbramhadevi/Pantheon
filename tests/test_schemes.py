#!/usr/bin/env python

import os
from os import path
import sys
import time
import signal
import argparse
import csv
from datetime import datetime
import random

import context
from helpers import utils
from helpers.subprocess_wrappers import Popen, check_output, call


def simulate_metrics():
    """Simulates RTT, throughput, loss rate, and latency."""
    rtt = round(random.uniform(20, 100), 2)           # in ms
    throughput = round(random.uniform(0.5, 5.0), 2)    # in Mbps
    loss_rate = round(random.uniform(0, 0.05), 4)      # in %
    latency = round(random.uniform(10, 60), 2)         # in ms
    return rtt, throughput, loss_rate, latency


def collect_metrics_csv(scheme, port):
    """Returns open CSV writer and file handle for metrics logging."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    filename = f'metrics_{scheme}_{port}_{timestamp}.csv'
    filepath = path.join(log_dir, filename)

    f = open(filepath, 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(['time', 'rtt', 'throughput', 'loss_rate', 'latency'])
    return f, writer


def test_schemes(args):
    wrappers_dir = path.join(context.src_dir, 'wrappers')

    if args.all:
        schemes = utils.parse_config()['schemes'].keys()
    elif args.schemes is not None:
        schemes = args.schemes.split()

    for scheme in schemes:
        sys.stderr.write('Testing %s...\n' % scheme)
        src = path.join(wrappers_dir, scheme + '.py')

        run_first = check_output([src, 'run_first']).strip()
        run_second = 'receiver' if run_first == 'sender' else 'sender'

        port = utils.get_open_port()

        cmd = [src, run_first, port]
        first_proc = Popen(cmd, preexec_fn=os.setsid)

        time.sleep(3)

        cmd = [src, run_second, '127.0.0.1', port]
        second_proc = Popen(cmd, preexec_fn=os.setsid)

        # Set up metrics collection
        metrics_file, writer = collect_metrics_csv(scheme, port)

        start_time = time.time()
        duration = 60  # seconds

        try:
            while time.time() - start_time < duration:
                rtt, throughput, loss_rate, latency = simulate_metrics()
                now = datetime.now().strftime('%H:%M:%S')
                writer.writerow([now, rtt, throughput, loss_rate, latency])
                time.sleep(1)

        except Exception as e:
            sys.exit(f'Metrics collection error: {e}')
        finally:
            metrics_file.close()

        signal.signal(signal.SIGALRM, utils.timeout_handler)
        signal.alarm(60)

        try:
            for proc in [first_proc, second_proc]:
                proc.wait()
                if proc.returncode != 0:
                    sys.exit('%s failed in tests' % scheme)
        except utils.TimeoutError:
            pass
        except Exception as exception:
            sys.exit('test_schemes.py: %s\n' % exception)
        else:
            signal.alarm(0)
            sys.exit('test exited before time limit')
        finally:
            utils.kill_proc_group(first_proc)
            utils.kill_proc_group(second_proc)


def cleanup():
    cleanup_src = path.join(context.base_dir, 'tools', 'pkill.py')
    cmd = [cleanup_src, '--kill-dir', context.base_dir]
    call(cmd)


def main():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true',
                       help='test all the schemes specified in src/config.yml')
    group.add_argument('--schemes', metavar='"SCHEME1 SCHEME2..."',
                       help='test a space-separated list of schemes')

    args = parser.parse_args()

    try:
        test_schemes(args)
    except:
        cleanup()
        raise
    else:
        sys.stderr.write('Passed all tests!\n')


if __name__ == '__main__':
    main()