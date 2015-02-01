#!/opt/local/bin/python2.7
"""
GET https://www7.dpf.gov.br/sinpa/realizarReagendamento.do?dispatcher=exibirSolicitacaoReagendamento&validate=false

POST https://www7.dpf.gov.br/sinpa/realizarReagendamento.do
dispatcher=processarConsultaAgendamento&validate=true&origem=exibirSolicitacaoAgendamento&operacao=reagendar&cpf=302.131.598-48&protocolo=&dataNascimento=30%2F09%2F1981&senha=xndm7n

POST https://www7.dpf.gov.br/sinpa/realizarReagendamento.do
dispatcher=exibirInclusaoAgendamento&postoId=1375&validate=false&ufPosto=SP&cidadePosto=7107
"""

import re
import requests
import StringIO
from PIL import Image
from lxml import html

cpf = raw_input("Digite o CPF:")
dtNasc = raw_input("Digite a data de nascimento:")

s = requests.Session()
r = s.get("https://www7.dpf.gov.br/sinpa/realizarReagendamento.do?dispatcher=exibirSolicitacaoReagendamento&validate=false", verify=False)
#print r.text

print "Buscando captcha\n\n\n"

r = s.get("https://www7.dpf.gov.br/sinpa/jcaptcha.do", verify=False)

im = Image.open(StringIO.StringIO(r.content))
im.save("captcha.jpg", "JPEG")
im.show()

captcha = raw_input("Digite o captcha:")

print "Validando o captcha\n\n\n"

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

for posto in postosElem:
	postoId = re.sub(r"[^\d]+", r"", posto.get("href"))
	postoName = posto.text.strip().split("\n")[0].strip().rstrip("-")
	print "\nPosto: %s - %s" % (postoId, postoName)

	payload = {
		"dispatcher": "exibirInclusaoAgendamento",
		"postoId": postoId,
		"validate": "false",
		"ufPosto": "SP",
		"cidadePosto": "7107"
	}

	r = s.post("https://www7.dpf.gov.br/sinpa/realizarReagendamento.do", data=payload, verify=False)
	tree = html.fromstring(r.content)
	datas = tree.xpath("//option")

	for data in datas:
		print "%s - %s" % (data.get("value"), data.text)

print