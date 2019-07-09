# BOTC txndata library

import struct

pfmt = "324s324sQ"

def make_txndata(sender, recp, amount):
	return struct.pack(pfmt, bytes(sender, 'utf-8'), bytes(recp, 'utf-8'), amount)

def get_txndata(txndata):
	raw = struct.unpack(pfmt, txndata)

	return {"sender": raw[0].decode('ascii'), "recipient": raw[1].decode('ascii'), "amount": raw[2]}
    