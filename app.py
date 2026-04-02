from flask import Flask, render_template, request, jsonify
from datetime import datetime, date
import requests
import calendar
import pandas as pd


app = Flask(__name__)

SUPABASE_URL = "https://ooudzxszovimsmfypckz.supabase.co"
SUPABASE_KEY = "sb_publishable_8WyuhLagGwQZFaaWKqXqYA_UJ6toANR"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

MESES = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

Resumo_executivo = [
    {"Item": "Serviços de manutenção (fixo mensal)", "Descrição": "Operação completa", "Valor (R$)": 818496.00},
    {"Item": "Gestão de peças", "Descrição": "Taxa fixa mensal", "Valor (R$)": 8000.00},
    {"Item": "Peças e componentes", "Descrição": "Conforme consumo", "Valor (R$)": None},       # virá da API de peças
    {"Item": "Serviços extraordinários", "Descrição": "Sob demanda", "Valor (R$)": None},       # vem das OS
]


# 3.1
Infra = [
     {"subitem": "Instalações físicas", "Descrição": "Galpão, área técnica, utilidades", "Critério de Apropriação": "Rateio mensal", "% estimado": 0.08, "Valor (R$)": 65479.68},
     {"subitem": "Energia elétrica", "Descrição": "Operação equipamentos e recarga", "Critério de Apropriação": "Consumo estimado", "% estimado": 0.04, "Valor (R$)": 32739.84},
     {"subitem": "Segurança e vigilância", "Descrição": "Patrimonial e operacional", "Critério de Apropriação": "Rateio", "% estimado": 0.01, "Valor (R$)": 8184.96},
     {"subitem": "Manutenção predial", "Descrição": "Conservação da estrutura", "Critério de Apropriação": "Rateio", "% estimado": 0.01, "Valor (R$)": 8184.96}
]


#3.2
Pessoal_tecnico_especializado = [
    {"Subitem": "Engenheiros e supervisores", "Descrição": "Coordenação técnica", "Critério": "Custo direto", "% estimado": 0.06, "Valor (R$)": 49109.76},
    {"Subitem": "Técnicos manutenção elétrica", "Descrição": "Alta tensão e baterias", "Critério": "Custo direto", "% estimado": 0.12, "Valor (R$)": 98219.52},
    {"Subitem": "Técnicos mecânicos", "Descrição": "Sistemas mecânicos", "Critério": "Custo direto", "% estimado": 0.1, "Valor (R$)": 81849.60},
    {"Subitem": "Equipe borracharia", "Descrição": "Pneus e rodagem", "Critério": "Custo direto", "% estimado": 0.03, "Valor (R$)": 24554.88},
    {"Subitem": "Equipe funilaria/pintura", "Descrição": "Pequenas avarias", "Critério": "Custo direto", "% estimado": 0.02, "Valor (R$)": 16369.92},
    {"Subitem": "Plantão 24h", "Descrição": "Turnos e sobreaviso", "Critério": "Adicional operacional", "% estimado": 0.06, "Valor (R$)": 49109.76},
    {"Subitem": "Encargos trabalhistas", "Descrição": "INSS, FGTS, etc.", "Critério": "Proporcional", "% estimado": 0.1, "Valor (R$)": 81849.60}
]

#3.3
maquinario_equipamentos = [
    {
        "Subitem": "Equipamentos diagnóstico",
        "Descrição": "Scanners, software",
        "Critério": "Depreciação",
        "% estimado": 0.04,
        "Valor (R$)": 32739.84
    },
    {
        "Subitem": "Equipamentos alta tensão",
        "Descrição": "Ferramentas HV",
        "Critério": "Depreciação",
        "% estimado": 0.03,
        "Valor (R$)": 24554.88
    },
    {
        "Subitem": "Equipamentos mecânicos",
        "Descrição": "Elevadores, compressores",
        "Critério": "Depreciação",
        "% estimado": 0.04,
        "Valor (R$)": 32739.84
    },
    {
        "Subitem": "Equipamentos gás/biometano",
        "Descrição": "Testes e segurança",
        "Critério": "Depreciação",
        "% estimado": 0.02,
        "Valor (R$)": 16369.92
    }
]


#3.4
ferramentaria = [
    {
        "Subitem": "Ferramentas gerais",
        "Descrição": "Uso contínuo",
        "Critério": "Rateio",
        "% estimado": 0.02,
        "Valor (R$)": 16369.92
    },
    {
        "Subitem": "Ferramentas especiais",
        "Descrição": "Sistemas elétricos/gás",
        "Critério": "Rateio",
        "% estimado": 0.02,
        "Valor (R$)": 16369.92
    },
    {
        "Subitem": "Reposição e desgaste",
        "Descrição": "Consumo",
        "Critério": "Rateio",
        "% estimado": 0.01,
        "Valor (R$)": 8184.96
    }
]

#3.5
volante = [
    {
        "Subitem": "Veículo utilitário",
        "Descrição": "Deslocamento técnico",
        "Critério": "Rateio",
        "% estimado": 0.02,
        "Valor (R$)": 16369.92
    },
    {
        "Subitem": "Combustível/energia",
        "Descrição": "Operação",
        "Critério": "Consumo",
        "% estimado": 0.01,
        "Valor (R$)": 8184.96
    },
    {
        "Subitem": "Manutenção veículo",
        "Descrição": "Preventiva/corretiva",
        "Critério": "Rateio",
        "% estimado": 0.01,
        "Valor (R$)": 8184.96
    }
]

#3.6
gestao_chamados = [
    {
        "Subitem": "Plataforma digital",
        "Descrição": "Gestão de chamados",
        "Critério": "Licença",
        "% estimado": 0.03,
        "Valor (R$)": 24554.88
    },
    {
        "Subitem": "Monitoramento e TI",
        "Descrição": "Suporte técnico",
        "Critério": "Rateio",
        "% estimado": 0.02,
        "Valor (R$)": 16369.92
    },
    {
        "Subitem": "Relatórios e BI",
        "Descrição": "Indicadores e controle",
        "Critério": "Rateio",
        "% estimado": 0.01,
        "Valor (R$)": 8184.96
    }
]

def obter_custos_operacionais():
    categorias = [
        {"titulo": "Infraestrutura da Oficina", "itens": Infra},
        {"titulo": "Pessoal Técnico Especializado(24h)", "itens": Pessoal_tecnico_especializado},
        {"titulo": "Maquinário e Equipamentos", "itens": maquinario_equipamentos},
        {"titulo": "Ferramentaria", "itens": ferramentaria},
        {"titulo": "Veículo de Atendimento Volante", "itens": volante},
        {"titulo": "Sistema de Gestão e Chamados", "itens": gestao_chamados},
    ]

    total_geral = 0
    for cat in categorias:
        subtotal = sum(item["Valor (R$)"] for item in cat["itens"])
        cat["subtotal"] = subtotal
        total_geral += subtotal

    return {"categorias": categorias, "total_geral": total_geral}



def buscar_supabase(tabela, filtros=""):
    url = f"{SUPABASE_URL}/rest/v1/{tabela}?select=*{filtros}"
    r = requests.get(url, headers=HEADERS)
    return r.json() if r.status_code == 200 else []

def obter_dados(mes, ano):
    primeiro_dia = f"{ano}-{mes:02d}-01"
    ultimo_dia_num = calendar.monthrange(ano, mes)[1]
    ultimo_dia = f"{ano}-{mes:02d}-{ultimo_dia_num}"

    ordens_raw = buscar_supabase(
        "Ordens_Servico",
        f"&status=eq.FECHADA&data_fechamento=gte.{primeiro_dia}T00:00:00&data_fechamento=lte.{ultimo_dia}T23:59:59"
    )

    print(f"OS encontradas: {len(ordens_raw)}")

    encaminhamentos_raw = buscar_supabase("OS_Encaminhamentos")
    frota_raw = buscar_supabase("View_Frota_Completa")
    apoio_raw = buscar_supabase("Apoio_Etapas")  # novo

    # índice de apoio por codigo_etapa
    apoio_por_codigo = {a['codigo_etapa']: a['descricao'] for a in apoio_raw}

    enc_por_os = {}
    for e in encaminhamentos_raw:
        num = str(e.get('numero_os_direto', ''))
        enc_por_os.setdefault(num, []).append(e)

    frota_por_prefixo = {str(v['prefixo']): v for v in frota_raw}

    ordens = []
    for os in ordens_raw:
        num_os = str(os['numero_sequencial'])
        prefixo = str(os['prefixo_veiculo'])
        veiculo = frota_por_prefixo.get(prefixo, {})
        encaminhamentos = enc_por_os.get(num_os, [])

        tarefas = list(set(e['tarefa'] for e in encaminhamentos if e.get('tarefa')))

        # descrição via Apoio_Etapas
        descricoes = []
        for e in encaminhamentos:
            codigo = e.get('codigo_etapa')
            desc = apoio_por_codigo.get(codigo, e.get('encaminhamento_descricao', '-'))
            if desc and desc not in descricoes:
                descricoes.append(desc)

        # insumos
        insumos = []
        valor_total = 0
        for e in encaminhamentos:
            if e.get('insumo_descricao'):
                insumos.append({
                    "descricao": e['insumo_descricao'],
                    "quantidade": e.get('insumo_quantidade') or 0,
                    "valor_total": float(e.get('insumo_valor_total') or 0)
                })
                valor_total += float(e.get('insumo_valor_total') or 0)

        ordens.append({
            "numero_os": num_os,
            "data_abertura": formatar_data(os.get('data_abertura')),
            "data_fechamento": formatar_data(os.get('data_fechamento')),
            "prefixo": prefixo,
            "placa": veiculo.get('placa', '-'),
            "modelo": veiculo.get('modelo', '-'),
            "familia": veiculo.get('familia', '-'),
            "km_atual": os.get('km_atual', '-'),
            "tarefas": ", ".join(tarefas) if tarefas else '-',
            "descricao": " | ".join(descricoes) if descricoes else os.get('defeito_relatado', '-'),
            "defeito_relatado": os.get('defeito_relatado', '-'),
            "is_dano_severo": os.get('is_dano_severo', False),  # novo
            "insumos": insumos,                                  # novo
            "valor_total": valor_total,
        })

    modelos = {}
    for o in ordens:
        m = o['modelo']
        p = o['prefixo']
        modelos.setdefault(m, {}).setdefault(p, []).append(o)

    return {
        "ordens": ordens,
        "modelos": modelos,
        "periodo": {
            "inicio": primeiro_dia,
            "fim": ultimo_dia,
            "mes": MESES.get(mes, ''),
            "ano": ano
        },
        "resumo": {
            "total_faturamento": sum(o['valor_total'] for o in ordens),
            "total_os": len(ordens),
        }
    }

def formatar_data(dt_str):
    if not dt_str:
        return '-'
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return dt_str

@app.route('/')
def index():
    hoje = date.today()
    return render_template('index.html', mes_atual=hoje.month, ano_atual=hoje.year)

@app.route('/api/relatorio')
def api_relatorio():
    mes = request.args.get('mes', type=int) or date.today().month
    ano = request.args.get('ano', type=int) or date.today().year

    dados = obter_dados(mes, ano)
    custos = obter_custos_operacionais()
    resumo_executivo = []
    for item in Resumo_executivo:
            i = dict(item)
            if i["Item"] == "Serviços extraordinários":
                i["Valor (R$)"] = dados['resumo']['total_faturamento']
            elif i["Item"] == "Peças e componentes":
                i["Valor (R$)"] = None  # ainda aguardando API
            resumo_executivo.append(i)

    return jsonify({
        'success': True,
        'resumo_executivo': resumo_executivo,
        'ordens': dados['ordens'],
        'modelos': dados['modelos'],
        'periodo': dados['periodo'],
        'resumo': dados['resumo'],
        'custos_operacionais': custos,   # novo
        'nome_mes': MESES.get(mes, ''),
        'ano': ano,
        'contrato': '001/2025',
        'data_geracao': datetime.now().strftime("%d/%m/%Y %H:%M")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)