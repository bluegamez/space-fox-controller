#!/usr/bin/env python3

import fliclib
import queue
import threading
import logging
import grpc
import controller_pb2
import controller_pb2_grpc
import sys
import uuid

from enum import Enum
from typing import List, Iterable

client = fliclib.FlicClient("localhost")

button_mapping = {}

type_mapping = {
    fliclib.ClickType.ButtonClick: controller_pb2.Action.Type.SINGLE_CLICK,
    fliclib.ClickType.ButtonSingleClick: controller_pb2.Action.Type.SINGLE_CLICK,
    fliclib.ClickType.ButtonDoubleClick: controller_pb2.Action.Type.DOUBLE_CLICK,
    fliclib.ClickType.ButtonHold: controller_pb2.Action.Type.LONG_PRESS,
}

q = queue.Queue()

controllerId = uuid.uuid4()

def actions() -> Iterable[controller_pb2.Action]:
    while True:
        yield q.get()

def sender(name):
    logging.basicConfig()

    with grpc.insecure_channel(sys.argv[1]) as channel:
        stub = controller_pb2_grpc.SpaceFoxStub(channel)
        response = stub.ControllerActions(actions())
        print(response)

def got_button(bd_addr):
    cc = fliclib.ButtonConnectionChannel(bd_addr)
    cc.on_button_single_or_double_click_or_hold = \
        lambda channel, click_type, was_queued, time_diff: \
            q.put(controller_pb2.Action(controllerId=str(controllerId), type=type_mapping[click_type], button=button_mapping[channel.bd_addr]))

    cc.on_connection_status_changed = \
        lambda channel, connection_status, disconnect_reason: \
            print(channel.bd_addr + " " + str(connection_status) + (" " + str(disconnect_reason) if connection_status == fliclib.ConnectionStatus.Disconnected else ""))
    client.add_connection_channel(cc)

def got_info(items):
    btns = []
    for bd_addr in items["bd_addr_of_verified_buttons"]:
        btns.append((int(bd_addr.replace(":", ""), base=16), bd_addr))

        got_button(bd_addr)

    btns.sort(key=lambda e: e[0])

    button_mapping[btns[0][1]] = controller_pb2.Action.Button.LEFT
    button_mapping[btns[1][1]] = controller_pb2.Action.Button.RIGHT
    print(button_mapping)

client.get_info(got_info)

client.on_new_verified_button = got_button

x = threading.Thread(target=sender, args=(1,))
x.start()

client.handle_events()
