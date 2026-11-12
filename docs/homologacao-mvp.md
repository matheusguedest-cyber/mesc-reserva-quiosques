# Relatório de Homologação — MVP MESC

## 1. Objetivo

Validar o funcionamento das principais funcionalidades do MVP de reserva de quiosques do Clube de Campo MESC, verificando autenticação, consulta de disponibilidade, confirmação de reservas e persistência dos dados.

## 2. Ambiente de testes

- **Aplicação:** Python e Flask
- **Banco de dados:** SQLite
- **Ambiente de desenvolvimento:** GitHub Codespaces
- **Testes automatizados:** pytest
- **Quantidade de testes automatizados:** 20
- **Resultado:** 20 aprovados, sem falhas

## 3. Cenários de homologação manual

| ID | Cenário | Resultado |
|---|---|---|
| CT01 | Realizar login com associado válido | Aprovado |
| CT02 | Consultar disponibilidade de quiosques por data | Aprovado |
| CT03 | Realizar reserva de quiosque disponível | Aprovado |
| CT04 | Exibir mensagem de confirmação da reserva | Aprovado |
| CT05 | Atualizar quiosque reservado para ocupado | Aprovado |
| CT06 | Persistir reserva no banco SQLite | Aprovado |
| CT07 | Ocultar botão de reserva para quiosque ocupado | Aprovado |

## 4. Evidência de persistência

Foi realizada uma reserva utilizando a interface do aplicativo, com os seguintes dados:

- **ID da reserva:** 3
- **ID do associado:** 101
- **Quiosque:** 03
- **Data reservada:** 20/11/2026
- **Status:** confirmada

A consulta SQL confirmou a existência do registro na tabela de reservas.

## 5. Testes automatizados

Foram executados 20 testes utilizando pytest, distribuídos entre:

- Autenticação: 6 testes.
- Consulta de disponibilidade: 3 testes.
- Serviço de reservas: 6 testes.
- Rotas de reserva: 5 testes.

Todos os testes foram aprovados.

## 6. Pendências e limitações

- Confirmar com a administração do MESC o horário e o período de abertura semanal das reservas às terças-feiras.
- Implementar a regra de abertura semanal após sua confirmação.
- Validar a aplicação e o script de atualização do índice em PostgreSQL.
- Realizar testes de usabilidade com representantes dos associados.
- Realizar testes de desempenho no ambiente de hospedagem definitivo.

## 7. Conclusão

O MVP demonstrou funcionamento satisfatório nos cenários executados de autenticação, consulta de disponibilidade e reserva de quiosques.

A integração entre interface, regras de negócio e persistência foi validada por testes automatizados e verificações manuais.

A homologação técnica dos cenários descritos foi concluída, permanecendo pendentes a validação com usuários reais e a implementação das regras operacionais específicas do clube.