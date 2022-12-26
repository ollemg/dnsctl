# dns-changer
Python CLI para administrar mudanças de DNS


Ferramenta está em desenvolvimento;


O problema que o dnsctl se propõe a resolver é:
  - multiplos links de internet sem BGP;
  - Blocos de endereço com diferentes mascaras;



Então com um arquivo de configuração (ver o exemplo domain.yml) será possível
centralizar as configurações de zona dns.

exemplo:

~~~yaml
cidr:
  - name: OI
    addr: 1.1.1.0/24

  - name: VIVO
    addr: 2.2.2.0/24

  - name: CLARO
    addr: 3.3.3.0/24

records:
  - name: app1
    type: A
    addr: [ 1.1.1.10, 2.2.2.10, 3.3.3.10 ]
    mode: failover
    reverse: true
    info: Aplicação mailgw
~~~

A configuração 'cidr' serve para descrever os links de internet. 

OBS: importante configurar a mascara corretamente.

a configuração de 'records' se propõe a descrever os registros A ou CNAME

Existem 3 modos para registros A:
  - failover
  - roundrobin
  - standalone


## Exemplos da cli:

A CLI vai gerar um arquivo com as entradas DNS no arquivo .db com os endereços configurados no domain.yml

~~~
dnsctl failover --link OI
~~~
