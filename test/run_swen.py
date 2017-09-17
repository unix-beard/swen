#!/usr/bin/env python3

import logging
import argparse
import yaml
import subprocess


logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    level=logging.DEBUG
)


def get_step_id(flow, step_id):
    for idx, s in enumerate(flow):
        if s['id'] == step_id:
            return idx
    return None


def get_next_step(flow, step, rc):
    logging.info("Determining the next step: [returncode={}]".format(rc))
    has_exit_code = False
    has_success = False
    has_failure = False

    if 'on-exit-code' in step:
        logging.debug("Step has 'on-exit-code' attribute: {}".format(step['on-exit-code']))
        has_exit_code = True
    if 'on-success' in step:
        logging.debug("Step has 'on-success' attribute: {}".format(step['on-success']))
        has_success = True
    if 'on-failure' in step:
        logging.debug("Step has 'on-failure' attribute: {}".format(step['on-failure']))
        has_failure = True

    if rc == 0 and has_success:
        return flow[get_step_id(flow, step['on-success'])]

    if rc != 0 and has_failure:
        return flow[get_step_id(flow, step['on-failure'])]


def execute_step(step):
    logging.info("Executing step: {}, id: {}, doc: {}".format(step['step'], step['id'], step['doc']))
    p = subprocess.Popen(step['step'])
    p.wait()
    return p.returncode


def execute_flow(flow):
    logging.info("Executing flow: [{}]".format(flow['id']))
    logging.info("Doc: {}".format(flow['doc']))

    step = flow['flow'][0]

    while step is not None:
        try:
            rc = execute_step(step)
            step = get_next_step(flow['flow'], step, rc)
            logging.info("Next step: {}".format(step))
        except KeyError as ke:
            logging.exception(ke)
            logging.warning("Step (id={}) is missing executable argument".format(s['id']))


def main():
    parser = argparse.ArgumentParser(prog='swen')
    parser.add_argument('-f', '--flow', required=True)

    args = parser.parse_args()

    stream = open(args.flow, 'r')
    execute_flow(yaml.load(stream))


if __name__ == '__main__':
    main()
