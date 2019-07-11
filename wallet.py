# BOTC Wallet 1.0
# Wallet interface for the BOTC platform
# Written by vortex

from txndata import *

import struct, binascii, hashlib, requests, json

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto import Random

# endpoints (as of BOTC v1.0)
ANNOUNCE = "/announce"
FINDBLOCK = "/blockchain/find/"
REGISTER = "/register"
NEWTXN = "/txn/new"

# wallet instance
class Wallet:
	'''
	The BOTC wallet instance

	This class interacts with a BOTC node and it sets up a key pair to send and recieve coins
	'''
	def __init__(self, url):
		self.private_key = RSA.generate(1024, Random.new().read)
		self.public_key = self.private_key.publickey()
		self.coins = 0
		self.identity = binascii.hexlify(self.public_key.exportKey('DER')).decode('utf-8')
		self.url = url

	def sendRequest(self, reqtype, **kwargs):
		if reqtype == "announce":
			return requests.get(self.url + ANNOUNCE).json()
		if reqtype == "findBlock":
			return requests.post(self.url + FINDBLOCK + kwargs["hash"]).json()
		if reqtype == "register":
			return requests.get(self.url + REGISTER).json()
		if reqtype == "newTxn":
			return requests.post(self.url + NEWTXN, data=kwargs).json()

	def sendTransaction(self, recp, amount):
		if self.coins < amount:
			return False

		self.coins -= amount
		txndata = make_txndata(self.identity, recp, amount)
		signer = PKCS1_v1_5.new(RSA.importKey(self.private_key.exportKey('DER')))

		signature = binascii.hexlify(signer.sign(SHA.new(txndata)))

		self.sendRequest("newTxn", txndata=binascii.hexlify(txndata).decode('utf-8'), signature=signature)
		
	def recieve(self):
		req = self.sendRequest("announce")

		for i in req["blockchain"]:
			if i["txndata"]["recipient"] == self.identity:
				self.coins += i["txndata"]["amount"]

class CustomWallet:
	'''
	The BOTC wallet but you import the key
	'''
	def __init__(self, privkey, url):
		self.private_key = RSA.importKey(privkey)
		self.public_key = self.private_key.publickey()
		
		self.coins = 0
		self.identity = binascii.hexlify(self.public_key.exportKey('DER')).decode('utf-8')
		self.url = url

	def sendRequest(self, reqtype, **kwargs):
		if reqtype == "announce":
			return requests.get(self.url + ANNOUNCE).json()
		if reqtype == "findBlock":
			return requests.post(self.url + FINDBLOCK + kwargs["hash"]).json()
		if reqtype == "register":
			return requests.get(self.url + REGISTER).json()
		if reqtype == "newTxn":
			return requests.post(self.url + NEWTXN, data=kwargs).json()

	def sendTransaction(self, recp, amount):
		if self.coins < amount:
			return False

		self.coins -= amount
		txndata = make_txndata(self.identity, recp, amount)
		signer = PKCS1_v1_5.new(RSA.importKey(self.private_key.exportKey('DER')))

		signature = binascii.hexlify(signer.sign(SHA.new(txndata)))

		self.sendRequest("newTxn", txndata=binascii.hexlify(txndata).decode('utf-8'), signature=signature)

	def recieve(self):
		req = self.sendRequest("announce")
		c = 0 # coins recieved
		cs = 0 # coins sent

		for i in req["blockchain"]:
			if i["txndata"]["recipient"] == self.identity:
				c += i["txndata"]["amount"]

			if i["txndata"]["sender"] == self.identity:
				cs += i["txndata"]["amount"]

		if self.coins == c:
			self.coins += 0

		if self.coins < c:
			if (c - cs) != self.coins:
				self.coins += c
			else:
				self.coins += 0

		if self.coins > c:
			self.coins += 0
		