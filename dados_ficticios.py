"""
Dados fictícios para demonstração do relatório de faturamento
Cenário: 3 ônibus, 6 ordens de serviço (2 por ônibus)
"""

from datetime import datetime, timedelta
import random

# Configuração dos ônibus
ONIBUS = [
    {
        "id": 1,
        "prefixo": "101",
        "placa": "ABC-1234",
        "modelo": "Volvo B270R",
        "ano": 2020,
        "cliente": "Consórcio BRT"
    },
    {
        "id": 2,
        "prefixo": "102", 
        "placa": "DEF-5678",
        "modelo": "Mercedes-Benz O500",
        "ano": 2021,
        "cliente": "Consórcio BRT"
    },
    {
        "id": 3,
        "prefixo": "103",
        "placa": "GHI-9012", 
        "modelo": "Scania K310",
        "ano": 2019,
        "cliente": "Consórcio BRT"
    }
]

# Catálogo de serviços e preços
SERVICOS = [
    {"id": 1, "descricao": "Troca de Farol Dianteiro", "categoria": "Elétrica", "preco": 350.00},
    {"id": 2, "descricao": "Troca de Farol Traseiro", "categoria": "Elétrica", "preco": 280.00},
    {"id": 3, "descricao": "Troca de Para-choque Dianteiro", "categoria": "Funilaria", "preco": 1200.00},
    {"id": 4, "descricao": "Troca de Para-choque Traseiro", "categoria": "Funilaria", "preco": 1100.00},
    {"id": 5, "descricao": "Alinhamento de Faróis", "categoria": "Elétrica", "preco": 150.00},
    {"id": 6, "descricao": "Pintura de Para-choque", "categoria": "Pintura", "preco": 800.00},
    {"id": 7, "descricao": "Troca de Lâmpadas", "categoria": "Elétrica", "preco": 95.00},
    {"id": 8, "descricao": "Reparo de Para-choque", "categoria": "Funilaria", "preco": 450.00}
]

def gerar_ordens_servico(mes=3, ano=2026):
    """
    Gera ordens de serviço fictícias para o mês especificado
    Cada ônibus tem 2 ordens de serviço
    """
    ordens = []
    os_id = 1
    
    # Configurar datas dentro do mês
    data_base = datetime(ano, mes, 15)
    
    for onibus in ONIBUS:
        # Cada ônibus terá 2 ordens de serviço
        for ordem_num in range(1, 3):
            # Definir serviços diferentes para cada ordem
            if ordem_num == 1:
                # Primeira ordem: serviços de farol
                servicos_executados = [
                    SERVICOS[0],  # Troca Farol Dianteiro
                    SERVICOS[6],  # Troca Lâmpadas
                    SERVICOS[4]   # Alinhamento Faróis
                ]
            else:
                # Segunda ordem: serviços de para-choque
                servicos_executados = [
                    SERVICOS[2],  # Troca Para-choque Dianteiro
                    SERVICOS[5],  # Pintura
                    SERVICOS[7]   # Reparo
                ]
            
            # Calcular valor total
            valor_total = sum(s['preco'] for s in servicos_executados)
            
            # Data aleatória dentro do mês
            dias_offset = random.randint(1, 28)
            data_conclusao = datetime(ano, mes, dias_offset)
            
            # Status da OS
            if data_conclusao <= datetime.now():
                status = "FINALIZADO"
            else:
                status = "EM_ANDAMENTO"
            
            ordem = {
                "id_ordem": os_id,
                "numero_os": f"OS-{ano}{mes:02d}-{os_id:03d}",
                "data_abertura": (data_conclusao - timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d"),
                "data_conclusao": data_conclusao.strftime("%Y-%m-%d"),
                "status": status,
                "cliente_nome": onibus["cliente"],
                "cliente_id": onibus["id"],
                "veiculo_prefixo": onibus["prefixo"],
                "veiculo_placa": onibus["placa"],
                "veiculo_modelo": onibus["modelo"],
                "servicos": servicos_executados,
                "qtd_servicos": len(servicos_executados),
                "valor_total": valor_total,
                "descricao_servicos": ", ".join([s['descricao'] for s in servicos_executados]),
                "categorias": list(set([s['categoria'] for s in servicos_executados]))
            }
            ordens.append(ordem)
            os_id += 1
    
    return ordens

def calcular_resumo_faturamento(ordens, mes, ano):
    """
    Calcula resumo estatístico do faturamento
    """
    if not ordens:
        return {
            "total_faturamento": 0,
            "total_os": 0,
            "total_servicos": 0,
            "ticket_medio": 0,
            "por_cliente": {},
            "por_veiculo": {},
            "por_categoria": {},
            "por_servico": {}
        }
    
    # Filtrar apenas ordens finalizadas
    ordens_finalizadas = [o for o in ordens if o['status'] == 'FINALIZADO']
    
    # Totais gerais
    total_faturamento = sum(o['valor_total'] for o in ordens_finalizadas)
    total_os = len(ordens_finalizadas)
    total_servicos = sum(o['qtd_servicos'] for o in ordens_finalizadas)
    ticket_medio = total_faturamento / total_os if total_os > 0 else 0
    
    # Por cliente
    por_cliente = {}
    for o in ordens_finalizadas:
        cliente = o['cliente_nome']
        por_cliente[cliente] = por_cliente.get(cliente, 0) + o['valor_total']
    
    # Por veículo
    por_veiculo = {}
    for o in ordens_finalizadas:
        veiculo = f"{o['veiculo_prefixo']} - {o['veiculo_placa']}"
        por_veiculo[veiculo] = por_veiculo.get(veiculo, 0) + o['valor_total']
    
    # Por categoria de serviço
    por_categoria = {}
    for o in ordens_finalizadas:
        for categoria in o['categorias']:
            # Distribuir valor proporcionalmente entre categorias
            valor_por_categoria = o['valor_total'] / len(o['categorias'])
            por_categoria[categoria] = por_categoria.get(categoria, 0) + valor_por_categoria
    
    # Por tipo de serviço
    por_servico = {}
    for o in ordens_finalizadas:
        for servico in o['servicos']:
            desc = servico['descricao']
            por_servico[desc] = por_servico.get(desc, 0) + servico['preco']
    
    return {
        "total_faturamento": total_faturamento,
        "total_os": total_os,
        "total_servicos": total_servicos,
        "ticket_medio": ticket_medio,
        "por_cliente": por_cliente,
        "por_veiculo": por_veiculo,
        "por_categoria": por_categoria,
        "por_servico": por_servico
    }

# Dados pré-gerados para o mês atual (Março/2026)
ORDENS_MARCO_2026 = gerar_ordens_servico(3, 2026)

# Resumo para março
RESUMO_MARCO_2026 = calcular_resumo_faturamento(ORDENS_MARCO_2026, 3, 2026)