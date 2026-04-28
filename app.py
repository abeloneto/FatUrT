from flask import Flask, render_template, request, jsonify
from datetime import datetime, date
import requests
import calendar
import pandas as pd
import io
import csv
from flask import Response 


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

valores_onibus = [
    {
        "ONIBUS": "BYD/MPOLO TORINO E A",
        "valor": 7991.00
    },
    {
        "ONIBUS": "BYD/MPOLO ATTIVI E A",
        "valor": 7991.00
    },
    {
        "ONIBUS": "IND/MILLENNIUM EL A",
        "valor": 9317.00
    },
    {
        "ONIBUS": "VOLV/MPOLO ATTIVI EA",
        "valor": 6662.00
    },
    {
        "ONIBUS": "VOLV/MPOLO ATTIVI EB",
        "valor": 7200.00
    },
    {
        "ONIBUS": "IND/MILLENNIUM ES U",
        "valor": 9048.00
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


def obter_dados(mes, ano, periodo='1'):

    data_inicio, data_fim, data_faturamento = calcular_periodo_pecas(periodo, mes, ano)

    # Ajustar o filtro de data para funcionar corretamente
    ordens_raw = buscar_supabase(
        "Ordens_Servico",
        f"&status=eq.FECHADA&data_fechamento=gte.{data_inicio}&data_fechamento=lte.{data_fim}"
                                )
    print(f"DEBUG - Período: {data_inicio} a {data_fim}")
    print(f"DEBUG - Total de OS encontradas: {len(ordens_raw)}")
    if len(ordens_raw) > 0:
        print(f"DEBUG - Primeira OS: {ordens_raw[0].get('numero_sequencial')}, Data: {ordens_raw[0].get('data_fechamento')}")

    encaminhamentos_raw = buscar_supabase("OS_Encaminhamentos")
    frota_raw = buscar_supabase("View_Frota_Completa")
    apoio_raw = buscar_supabase("Apoio_Etapas")
    # ✅ BUSCAR SOLICITAÇÕES DE SERVIÇO
    solicitacoes_raw = buscar_supabase("Solicitacao_Servicos")
    nf_raw = buscar_supabase("OS_NF")
    

    

    # índice de apoio por codigo_etapa
    apoio_por_codigo = {a['codigo_etapa']: a['descricao'] for a in apoio_raw}

    # ✅ CRIAR ÍNDICE DE SOLICITAÇÕES POR numero_ss
    solicitacoes_por_ss = {str(s['numero_ss']): s for s in solicitacoes_raw}

    notas_por_os = {}
    for nf in nf_raw:
        num_os_nota = str(nf.get('os'))

        if num_os_nota not in notas_por_os:
            notas_por_os[num_os_nota] = []
        
        numero_nota = nf.get('nf', '-')  # ajuste o nome da coluna da nota
        if numero_nota != '-':
            notas_por_os[num_os_nota].append(str(numero_nota))
    
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
        notas_desta_os = notas_por_os.get(num_os, [])
        numeros_notas = ", ".join(notas_desta_os) if notas_desta_os else '-'

        # ✅ BUSCAR KM DA SOLICITAÇÃO DE SERVIÇO
        numero_ss = str(os.get('numero_ss', ''))
        solicitacao = solicitacoes_por_ss.get(numero_ss, {})
        km_atual = solicitacao.get('km_atual', '-')

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
                    "quantidade": int(e.get('insumo_quantidade') or 0),
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
            "km_atual": km_atual,  # ✅ AGORA VEM DA SOLICITAÇÃO
            "tarefas": ", ".join(tarefas) if tarefas else '-',
            "descricao": " | ".join(descricoes) if descricoes else os.get('defeito_relatado', '-'),
            "defeito_relatado": os.get('defeito_relatado', '-'),
            "is_dano_severo": os.get('is_dano_severo', False),
            "insumos": insumos,
            "valor_total": valor_total,
            "notas_fiscais": numeros_notas,
        })

    # Filtrar apenas OSs com valor > 0
    ordens_com_valor = [o for o in ordens if o['valor_total'] > 0]

    # Criar modelos apenas com OSs filtradas
    modelos = {}
    for o in ordens_com_valor:
        m = o['modelo']
        p = o['prefixo']
        modelos.setdefault(m, {}).setdefault(p, []).append(o)

    return {
        "ordens": ordens_com_valor,
        "modelos": modelos,
        "periodo": {
            "inicio": data_inicio, 
            "fim": data_fim,
            "mes": MESES.get(mes, ''),
            "ano": ano
        },
        "resumo": {
            "total_faturamento": sum(o['valor_total'] for o in ordens_com_valor),
            "total_os": len(ordens_com_valor),
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
    
@app.route('/api/relatorio/csv')
def api_relatorio_csv():
    mes = request.args.get('mes', type=int) or date.today().month
    ano = request.args.get('ano', type=int) or date.today().year
    periodo = request.args.get('periodo', '1')

    dados = obter_dados(mes, ano, periodo)

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')

    # cabeçalho
    writer.writerow(['Nº OS', 'Nota Fiscal', 'Abertura', 'Fechamento', 'Prefixo', 'Placa',
                     'Modelo', 'Família', 'Tipo de Serviço', 'Descrição Serviço',
                     'Defeito Relatado', 'Dano Severo', 'Item/Peça',
                     'Quantidade', 'Valor Unitário (R$)', 'Valor Total (R$)'])

    # Buscar encaminhamentos
    numeros_os = [str(os['numero_os']) for os in dados['ordens'] if os['valor_total'] > 0]
    
    encaminhamentos_raw = []
    if numeros_os:
        encaminhamentos_raw = buscar_supabase(
            "OS_Encaminhamentos",
            f"&numero_os_direto=in.({','.join(numeros_os)})&insumo_descricao=not.is.null"
        )

    # Agrupar encaminhamentos por OS
    encaminhamentos_por_os = {}
    for e in encaminhamentos_raw:
        num_os = str(e.get('numero_os_direto', ''))
        if num_os not in encaminhamentos_por_os:
            encaminhamentos_por_os[num_os] = []
        
        quantidade = float(e.get('insumo_quantidade') or 0)
        valor_total = float(e.get('insumo_valor_total') or 0)
        valor_unitario = round(valor_total / quantidade , 2) if quantidade > 0 else 0
        
        encaminhamentos_por_os[num_os].append({
            'descricao': e.get('insumo_descricao', '-'),
            'quantidade': quantidade,
            'valor_unitario': valor_unitario,
            'valor_total': valor_total
        })

    # Escrever linhas
    for os in dados['ordens']:
        if os['valor_total'] > 0:
            num_os = str(os['numero_os'])
            encaminhamentos = encaminhamentos_por_os.get(num_os, [])
            
            if encaminhamentos:
                # Se tem encaminhamentos, uma linha por item/peça
                for enc in encaminhamentos:
                    writer.writerow([
                        os['numero_os'],
                        os['notas_fiscais'],
                        os['data_abertura'],
                        os['data_fechamento'],
                        os['prefixo'],
                        os['placa'],
                        os['modelo'],
                        os['familia'],
                        os['tarefas'],
                        os['descricao'],
                        os['defeito_relatado'],
                        'Sim' if os['is_dano_severo'] else 'Não',
                        enc['descricao'],  # Item/Peça
                        str(enc['quantidade']).replace('.', ','),  # Quantidade
                        str(enc['valor_unitario']).replace('.', ','),  # Valor Unitário
                        str(enc['valor_total']).replace('.', ',')  # Valor Total do item
                    ])
            else:
                # Se não tem encaminhamentos, uma linha sem detalhes de peças
                writer.writerow([
                    os['numero_os'],
                    os['notas_fiscais'],
                    os['data_abertura'],
                    os['data_fechamento'],
                    os['prefixo'],
                    os['placa'],
                    os['modelo'],
                    os['familia'],
                    os['tarefas'],
                    os['descricao'],
                    os['defeito_relatado'],
                    'Sim' if os['is_dano_severo'] else 'Não',
                    '-',  # Item/Peça
                    '-',  # Quantidade
                    '-',  # Valor Unitário
                    str(os['valor_total']).replace('.', ',')  # Valor Total
                ])

    nome_arquivo = f"extrato_manutencao_{MESES.get(mes,'').lower()}_{ano}.csv"

    return Response(
        '\ufeff' + output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{nome_arquivo}"'}
    )


@app.route('/')
def index():
    hoje = date.today()
    return render_template('manutencao.html',
                           mes_atual=hoje.month,
                           ano_atual=hoje.year,
                           pagina_ativa='manutencao')


@app.route('/pecas')
def pecas():
    hoje = date.today()
    return render_template('pecas.html',
                           mes_atual=hoje.month,
                           ano_atual=hoje.year,
                           pagina_ativa='pecas')

@app.route('/faturamento-mensal')
def faturamento_mensal():
    hoje = date.today()
    return render_template('faturamento_mensal.html',
                           mes_atual=hoje.month,
                           ano_atual=hoje.year,
                           pagina_ativa='faturamento_mensal')

@app.route('/api/relatorio')
def api_relatorio():
    mes = request.args.get('mes', type=int) or date.today().month
    ano = request.args.get('ano', type=int) or date.today().year
    periodo = request.args.get('periodo', '1')

    dados = obter_dados(mes, ano, periodo)
    custos = obter_custos_operacionais()
    # resumo_executivo = []
    # for item in Resumo_executivo:
    #         i = dict(item)
    #         if i["Item"] == "Serviços extraordinários":
    #             i["Valor (R$)"] = dados['resumo']['total_faturamento']
    #         elif i["Item"] == "Peças e componentes":
    #             i["Valor (R$)"] = dados['resumo']['total_faturamento']  # ainda aguardando API
    #         resumo_executivo.append(i)

    return jsonify({
        'success': True,
        # 'resumo_executivo': resumo_executivo,
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

def calcular_periodo_pecas(periodo, mes, ano):

    if periodo == '1':
        data_inicio = f"{ano}-{mes:02d}-01"
        data_fim    = f"{ano}-{mes:02d}-10"
    elif periodo == '2':
        data_inicio = f"{ano}-{mes:02d}-11"
        data_fim    = f"{ano}-{mes:02d}-20"
    elif periodo == '3':
        data_inicio = f"{ano}-{mes:02d}-21"
        data_fim    = f"{ano}-{mes:02d}-{calendar.monthrange(ano, mes)[1]}"
    
    # ✅ Adicione esse bloco:
    elif periodo == '4':
        data_inicio = f"{ano}-{mes:02d}-01"
        data_fim    = f"{ano}-{mes:02d}-{calendar.monthrange(ano, mes)[1]}"
    
    data_faturamento = data_fim  # ajuste conforme sua lógica
    return data_inicio, data_fim, data_faturamento

@app.route('/api/faturamento-mensal')
def api_faturamento_mensal():
    mes = request.args.get('mes', type=int) or date.today().month
    ano = request.args.get('ano', type=int) or date.today().year
    
    # Buscar todos os veículos da frota
    frota_raw = buscar_supabase("View_Frota_Completa")
    
    # Criar dicionário de valores por modelo (usando nome_bem)
    valores_por_modelo = {v["ONIBUS"].strip(): v["valor"] for v in valores_onibus}
    
    # Processar veículos e associar valores
    veiculos_com_custo = []
    total_veiculos = 0
    
    for veiculo in frota_raw:
        nome_bem = veiculo.get('nome_bem', '')  # Mudou de 'modelo' para 'nome_bem'
        modelo = veiculo.get('modelo', '').strip()  # Mantém modelo para exibição
        prefixo = veiculo.get('prefixo', '')
        placa = veiculo.get('placa', '')
        
        # Buscar valor correspondente ao nome_bem (que deve bater com a coluna ONIBUS)
        valor_mensal = valores_por_modelo.get(modelo, 0)
        
        veiculos_com_custo.append({
                'prefixo': prefixo,
                'placa': placa,
                'modelo': modelo,
                'nome_bem': nome_bem,
                'valor_mensal': valor_mensal
                    # Será 0 se não encontrar na tabela
            })
        total_veiculos += valor_mensal
    
    # Ordenar por prefixo
    veiculos_com_custo.sort(key=lambda x: x['prefixo'])
    
    # Valor fixo do estoque de peças
    estoque_pecas = 8000.00

    # ===== BUSCAR DANOS SEVEROS DO MÊS =====
    # Calcular primeiro e último dia do mês
    primeiro_dia = f"{ano}-{mes:02d}-01"
    if mes == 12:
        ultimo_dia = f"{ano}-12-31"
    else:
        proximo_mes = f"{ano}-{mes+1:02d}-01"
        from datetime import datetime, timedelta
        ultimo_dia_dt = datetime.strptime(proximo_mes, "%Y-%m-%d") - timedelta(days=1)
        ultimo_dia = ultimo_dia_dt.strftime("%Y-%m-%d")

    # Buscar OS com dano severo fechadas no mês
    os_danos_severos = buscar_supabase(
        "Ordens_Servico",
        f"&status=eq.FECHADA&is_dano_severo=eq.true&data_fechamento=gte.{primeiro_dia}&data_fechamento=lte.{ultimo_dia}"
    )

    print(f"🔥 Danos severos encontrados: {len(os_danos_severos)}")

# Buscar encaminhamentos com insumos dessas OS
    danos_severos_lista = []
    total_danos_severos = 0

    if os_danos_severos:
        numeros_os_severos = [str(os['numero_sequencial']) for os in os_danos_severos]
        
        enc_severos = buscar_supabase(
            "OS_Encaminhamentos",
            f"&numero_os_direto=in.({','.join(numeros_os_severos)})&insumo_descricao=not.is.null"
        )
    
    # Agrupar por OS
        for enc in enc_severos:
            num_os = enc.get('numero_os_direto')
            os_dados = next((os for os in os_danos_severos if str(os['numero_sequencial']) == num_os), None)
            
            if not os_dados:
                continue
        
            prefixo = os_dados.get('prefixo_veiculo', 'SEM-PREFIXO')
            dados_frota = frota_dict.get(prefixo, {'modelo': 'N/A'})
            
            valor_item = float(enc.get('insumo_valor_total') or 0)
            total_danos_severos += valor_item
        
            danos_severos_lista.append({
                'prefixo': prefixo,
                'numero_os': num_os,
                'modelo': dados_frota['modelo'],
                'defeito_relatado': os_dados.get('defeito_relatado', '-'),
                'valor': valor_item
        })

    # Ordenar por prefixo
    danos_severos_lista.sort(key=lambda x: x['prefixo'])    
    
    
    return jsonify({
        'success': True,
        'veiculos': veiculos_com_custo,
        'total_veiculos': total_veiculos,
        'estoque_pecas': estoque_pecas,
        'danos_severos': danos_severos_lista,
        'total_danos_severos': total_danos_severos,
        'nome_mes': MESES.get(mes, ''),
        'mes': mes,
        'ano': ano,
        'contrato': '001/2025',
        'data_geracao': datetime.now().strftime("%d/%m/%Y %H:%M")
    })

@app.route('/api/pecas')
def api_pecas():
    try:
        mes = request.args.get('mes', type=int) or date.today().month
        ano = request.args.get('ano', type=int) or date.today().year
        periodo = request.args.get('periodo', '1')

        data_inicio, data_fim, data_faturamento = calcular_periodo_pecas(periodo, mes, ano)

    # Buscar notas fiscais do Supabase (ou usar lista vazia se não existir a tabela)
    # Buscar notas fiscais da tabela OS_NF
        nf_raw = buscar_supabase("OS_NF")
        notas_por_os = {}
        for nf in nf_raw:
            num_os_nota = str(nf.get('os'))
            if num_os_nota not in notas_por_os:
                notas_por_os[num_os_nota] = []
            
            numero_nota = nf.get('nf', '-')
            if numero_nota != '-':
                notas_por_os[num_os_nota].append(str(numero_nota))
    except Exception as e:
        import traceback
        print("ERRO em api_pecas:", traceback.format_exc())  # ✅ mostra o erro completo no terminal
        return jsonify({'success': False, 'erro': str(e)}), 500

    # Buscar OS FECHADAS no período
    ordens_raw = buscar_supabase(
        "Ordens_Servico",
        f"&status=eq.FECHADA&data_fechamento=gte.{data_inicio}&data_fechamento=lte.{data_fim}"
    )
    
    print(f"DEBUG - Período: {data_inicio} a {data_fim}")
    print(f"DEBUG - Total de OS encontradas: {len(ordens_raw)}")

    if not ordens_raw:
        return jsonify({
            'success': True,
            'prefixos': [],
            'periodo': {'inicio': data_inicio, 'fim': data_fim, 'faturamento': data_faturamento},
            'resumo': {'total_itens': 0, 'total_geral': 0},
            'data_geracao': datetime.now().strftime("%d/%m/%Y %H:%M")
        })

    numeros_os = [str(os['numero_sequencial']) for os in ordens_raw]
    
    # Buscar encaminhamentos COM insumo
    encaminhamentos_raw = buscar_supabase(
        "OS_Encaminhamentos",
        f"&numero_os_direto=in.({','.join(numeros_os)})&insumo_descricao=not.is.null"
    )
    
    print(f"📦 Total de encaminhamentos COM INSUMO: {len(encaminhamentos_raw)}")

    # Buscar dados da frota para pegar placa e modelo
    frota_raw = buscar_supabase("View_Frota_Completa")
    frota_dict = {v.get('prefixo'): {'placa': v.get('placa'), 'modelo': v.get('modelo')} 
                for v in frota_raw}

    # Agrupar por prefixo
# Agrupar por prefixo
# Agrupar por prefixo
    prefixos = {}
    total_itens = 0
    total_geral = 0

    for enc in encaminhamentos_raw:
        num_os = enc.get('numero_os_direto')
        
        os_dados = next((os for os in ordens_raw if str(os['numero_sequencial']) == num_os), None)
        if not os_dados:
            continue
            
        prefixo = os_dados.get('prefixo_veiculo', 'SEM-PREFIXO')
        
        if os_dados.get('is_dano_severo', False):
            continue

        nfs_da_os = notas_por_os.get(num_os, [])
        numero_nf = ', '.join(nfs_da_os) if nfs_da_os else '-'
        valor_item = float(enc.get('insumo_valor_total') or 0)

        if prefixo not in prefixos:
            frota_info = frota_dict.get(prefixo, {})
            prefixos[prefixo] = {
                'prefixo': prefixo,
                'placa': frota_info.get('placa', '-'),
                'modelo': frota_info.get('modelo', '-'),
                'itens': [],
                'subtotal': 0
            }

        prefixos[prefixo]['itens'].append({
            'numero_os': num_os,
            'descricao': enc.get('insumo_descricao', '-'),
            'quantidade': enc.get('insumo_quantidade') or 0,
            'valor_total': valor_item,
            'data_fim': formatar_data(os_dados.get('data_fechamento')),
            'numero_nf': numero_nf,
            'defeito_relatado': os_dados.get('defeito_relatado', '-')
        })
            
        prefixos[prefixo]['subtotal'] += valor_item
        total_itens += 1
        total_geral += valor_item

    # ✅ FORA do for - mesma indentação do 'for'
    lista_prefixos = sorted(prefixos.values(), key=lambda x: x['prefixo'])

    return jsonify({
        'success': True,
        'prefixos': lista_prefixos,
        'periodo': {
            'inicio': data_inicio,
            'fim': data_fim,
            'faturamento': data_faturamento
        },
        'resumo': {
            'total_itens': total_itens,
            'total_geral': total_geral
        },
        'data_geracao': datetime.now().strftime("%d/%m/%Y %H:%M")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)