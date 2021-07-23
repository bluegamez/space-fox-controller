#!/usr/bin/env python3

import fliclib

client = fliclib.FlicClient("localhost")

def done(bd_addr):
	print("Button " + bd_addr + " was successfully added!")
	client.close()

def on_adv_packet(scanner, bd_addr, name, rssi, is_private, already_verified, already_connected_to_this_device, already_connected_to_other_device):
	if already_verified:
		return
	
	if is_private:
		print("Button " + bd_addr + " is currently private. Hold it down for 7 seconds to make it public.")
		return
	
	print("Found public button " + bd_addr + ", now connecting...")
	client.remove_scanner(scanner)
	
	def restart_scan():
		print("Restarting scan")
		client.add_scanner(scanner)
	
	def on_create(channel, error, connection_status):
		if connection_status == fliclib.ConnectionStatus.Ready:
			done(bd_addr)
		elif error != fliclib.CreateConnectionChannelError.NoError:
			print("Failed: " + str(error))
			restart_scan()
		else:
			client.set_timer(30 * 1000, lambda: client.remove_connection_channel(channel))
	
	def on_removed(channel, removed_reason):
		print("Failed: " + str(removed_reason))
		restart_scan()
	
	def on_connection_status_changed(channel, connection_status, disconnect_reason):
		if connection_status == fliclib.ConnectionStatus.Ready:
			done(bd_addr)
	
	channel = fliclib.ButtonConnectionChannel(bd_addr)
	channel.on_create_connection_channel_response = on_create
	channel.on_removed = on_removed
	channel.on_connection_status_changed = on_connection_status_changed
	client.add_connection_channel(channel)
	
scanner = fliclib.ButtonScanner()
scanner.on_advertisement_packet = on_adv_packet
client.add_scanner(scanner)

client.handle_events()
