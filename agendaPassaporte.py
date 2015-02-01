#!/opt/local/bin/python2.7
"""
GET https://www7.dpf.gov.br/sinpa/realizarReagendamento.do?dispatcher=exibirSolicitacaoReagendamento&validate=false

POST https://www7.dpf.gov.br/sinpa/realizarReagendamento.do
dispatcher=processarConsultaAgendamento&validate=true&origem=exibirSolicitacaoAgendamento&operacao=reagendar&cpf=302.131.598-48&protocolo=&dataNascimento=30%2F09%2F1981&senha=xndm7n

POST https://www7.dpf.gov.br/sinpa/realizarReagendamento.do
dispatcher=exibirInclusaoAgendamento&postoId=1375&validate=false&ufPosto=SP&cidadePosto=7107
"""

import requests
import StringIO
from PIL import Image

cpf = raw_input("Digite o CPF:")
dtNasc = raw_input("Digite a data de nascimento:")

s = requests.Session()
r = s.get("https://www7.dpf.gov.br/sinpa/realizarReagendamento.do?dispatcher=exibirSolicitacaoReagendamento&validate=false", verify=False)
#print r.text

print "Buscando captcha\n\n\n"

r = s.get("https://www7.dpf.gov.br/sinpa/jcaptcha.do", verify=False)

im = Image.open(StringIO.StringIO(r.content))
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

fp = open("out.html", "w")
fp.write(r.content)
fp.close()