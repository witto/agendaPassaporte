#!/usr/bin/python
# -*- coding: UTF8 -*-

import re
import requests
import StringIO
import random
import sys
import time
from PIL import Image
from lxml import html
from datetime import datetime
from dateutil import parser

def carregarMunicipios(uf):
	params = {
		"dispatcher": "carregaMunicipio",
		"dummy": random.randint(10000000, 99999999),
		"ufPosto": uf,
		"utilizaCidadeSessao": "false"
	}
	r = requests.get("https://www7.dpf.gov.br/sinpa/realizarAgendamento.do", params=params, verify=False)
	tree = html.fromstring(r.content)
	cidadesElem = tree.xpath("//option")
	return [{"id": x.get("value"), "name": x.text} for x in cidadesElem]

def carregarPostos(cidade):
	params = {
		"dispatcher": "carregaPostos",
		"dummy": random.randint(10000000, 99999999),
		"municipio": cidade
	}
	r = requests.get("https://www7.dpf.gov.br/sinpa/realizarAgendamento.do", params=params, verify=False)
	tree = html.fromstring(r.content)
	postosElem = tree.xpath("//a")
	return [{"id": re.sub(r"[^\d]+", r"", x.get("href")), "name": x.text} for x in postosElem]

def iniciarSessao(cpf, dtNasc):
	s = requests.Session()
	r = s.get("https://www7.dpf.gov.br/sinpa/realizarReagendamento.do?dispatcher=exibirSolicitacaoReagendamento&validate=false", verify=False)
	r = s.get("https://www7.dpf.gov.br/sinpa/jcaptcha.do", verify=False)

	im = Image.open(StringIO.StringIO(r.content))
	im.save("captcha.jpg", "JPEG")
	im.show()

	captcha = raw_input("Digite o captcha:")

	print "Validando captcha"

	payload = {
		"dispatcher": "processarConsultaAgendamento", 
		"validate": "true",
		"origem": "exibirSolicitacaoAgendamento",
		"operacao": "reagendar",
		"cpf": cpf,
		"protocolo": None,
		"dataNascimento": dtNasc,
		"senha": captcha
	}

	r = s.post("https://www7.dpf.gov.br/sinpa/realizarReagendamento.do", data=payload, verify=False)
	tree = html.fromstring(r.content)
	postosElem = tree.xpath("//span[@id='postos']/a")
	return None if (len(postosElem) == 0) else s

def carregarDatas(session, uf, cidade, posto):
	payload = {
		"dispatcher": "exibirInclusaoAgendamento",
		"postoId": posto,
		"validate": "false",
		"ufPosto": uf,
		"cidadePosto": cidade
	}

	r = session.post("https://www7.dpf.gov.br/sinpa/realizarReagendamento.do", data=payload, verify=False)
	tree = html.fromstring(r.content)
	#print r.content
	datas = tree.xpath("//option")
	print datas[0].get("value")
	return [parser.parse(x.get("value"), dayfirst=True) for x in datas if len(x.get("value").strip()) > 0]


uf = raw_input("Digite seu estado (UF):").upper()
cidades = carregarMunicipios(uf)
print cidades[10]

for i in range(0, len(cidades)):
	print "%2s) %s" % (i+1, cidades[i]["name"])

cidadeIndex = raw_input("Digite o número da cidade: ")
cidade = cidades[int(cidadeIndex)-1]
postos = carregarPostos(cidade["id"])

cpf = raw_input("Digite o CPF: ")
dtNasc = raw_input("Digite a data de nascimento: ")

s = iniciarSessao(cpf, dtNasc)
if not s:
	print "Falha ao iniciar sessão"
	sys.exit()

print "Sessão iniciada com sucesso.\n"

while True:
	print datetime.now()
	print "Iniciando consultas\n"
	for posto in postos:
		print "Posto %s" % posto["name"]
		print "Datas disponíveis:"
		datas = carregarDatas(s, uf, cidade["id"], posto["id"])
		for data in datas:
			print data.strftime("%d/%m/%Y")
		print
	print "\n\n"
	time.sleep(300)
