"""
Aplicação Flask para relatório de faturamento de manutenção de ônibus
Versão protótipo com dados fictícios
"""

from flask import Flask, render_template, request, make_response
from datetime import datetime, date
import pandas as pd
import io
import tempfile
import os
from dados_ficticios import (
    ORDENS_MARCO_2026, RESUMO_MARCO_2026, 
    ONIBUS, SERVICOS, gerar_ordens_servico, calcular_resumo_faturamento
)

app = Flask(__name__)

# Dicionário para armazenar dados de diferentes meses (simulando banco)
DADOS_MENSAL = {
    (3, 2026): ORDENS_MARCO_2026
}


def obter_dados_mes(mes, ano):
    """
    Obtém dados do mês/ano especificado
    Se não existir, gera dados fictícios para demonstração
    """
    chave = (mes, ano)
    
    if chave not in DADOS_MENSAL:
        # Gerar dados fictícios para o mês solicitado
        ordens = gerar_ordens_servico(mes, ano)
        resumo = calcular_resumo_faturamento(ordens, mes, ano)
        DADOS_MENSAL[chave] = ordens
        return ordens, resumo
    
    ordens = DADOS_MENSAL[chave]
    resumo = calcular_resumo_faturamento(ordens, mes, ano)
    return ordens, resumo

@app.route('/download/pdf')
def download_pdf():
    """Gera e baixa o relatório em PDF"""
    mes = request.args.get('mes', type=int)
    ano = request.args.get('ano', type=int)
    
    if not mes or not ano:
        mes = date.today().month
        ano = date.today().year
    
    # Obter dados
    ordens, resumo = obter_dados_mes(mes, ano)
    
    # Nome do mês
    meses = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    nome_mes = meses.get(mes, 'Mês Inválido')
    
    # Carregar logo
    logo_base64 = carregar_logo_base64()  # Você já deve ter essa função
    
    # Renderizar o HTML para PDF
    html_content = render_template('relatorio_pdf.html',
                                  ordens=ordens,
                                  resumo=resumo,
                                  mes=mes,
                                  ano=ano,
                                  nome_mes=nome_mes,
                                  data_geracao=datetime.now().strftime("%d/%m/%Y %H:%M"),
                                  logo_empresa=logo_base64)
    
    # Gerar PDF
    pdf_file = HTML(string=html_content).write_pdf()
    
    # Criar resposta
    response = make_response(pdf_file)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=faturamento_{ano}_{mes:02d}.pdf'
    
    return response

def carregar_logo_base64():
    """Carrega a logo e converte para base64"""
    import base64
    import os
    
    caminho_logo = os.path.join(os.path.dirname(__file__), 'static', '3.png')
    try:
        if os.path.exists(caminho_logo):
            with open(caminho_logo, "rb") as f:
                imagem_base64 = base64.b64encode(f.read()).decode('utf-8')
                return f"data:image/png;base64,{imagem_base64}"
    except Exception as e:
        print(f"Erro ao carregar logo: {e}")
    return None


@app.route('/')
def index():
    """Página inicial com seleção de mês/ano"""
    return render_template('index.html', 
                          mes_atual=date.today().month,
                          ano_atual=date.today().year)

@app.route('/relatorio')
def relatorio():
    """Página do relatório de faturamento"""
    mes = request.args.get('mes', type=int)
    ano = request.args.get('ano', type=int)
    
    if not mes or not ano:
        mes = date.today().month
        ano = date.today().year
    
    # Obter dados do mês
    ordens, resumo = obter_dados_mes(mes, ano)
    
    # Nomes dos meses
    meses = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    nome_mes = meses.get(mes, 'Mês Inválido')
    
    return render_template('relatorio.html',
                          ordens=ordens,
                          resumo=resumo,
                          mes=mes,
                          ano=ano,
                          nome_mes=nome_mes,
                          data_geracao=datetime.now().strftime("%d/%m/%Y %H:%M"))

@app.route('/download/excel')
def download_excel():
    """Exporta os dados para Excel"""
    mes = request.args.get('mes', type=int)
    ano = request.args.get('ano', type=int)
    
    if not mes or not ano:
        mes = date.today().month
        ano = date.today().year
    
    # Obter dados
    ordens, resumo = obter_dados_mes(mes, ano)
    
    # Criar DataFrame para detalhamento
    dados_detalhados = []
    for ordem in ordens:
        if ordem['status'] == 'FINALIZADO':  # Apenas finalizadas
            dados_detalhados.append({
                'Número OS': ordem['numero_os'],
                'Data Abertura': ordem['data_abertura'],
                'Data Conclusão': ordem['data_conclusao'],
                'Cliente': ordem['cliente_nome'],
                'Veículo': f"{ordem['veiculo_prefixo']} - {ordem['veiculo_placa']}",
                'Modelo': ordem['veiculo_modelo'],
                'Serviços Realizados': ordem['descricao_servicos'],
                'Qtd Serviços': ordem['qtd_servicos'],
                'Valor Total': ordem['valor_total']
            })
    
    df_detalhe = pd.DataFrame(dados_detalhados)
    
    # Criar DataFrame para resumo por cliente
    dados_por_cliente = []
    for cliente, valor in resumo['por_cliente'].items():
        dados_por_cliente.append({
            'Cliente': cliente,
            'Total Faturado': valor
        })
    df_por_cliente = pd.DataFrame(dados_por_cliente)
    
    # Criar DataFrame para resumo por serviço
    dados_por_servico = []
    for servico, valor in resumo['por_servico'].items():
        dados_por_servico.append({
            'Serviço': servico,
            'Total Faturado': valor
        })
    df_por_servico = pd.DataFrame(dados_por_servico).sort_values('Total Faturado', ascending=False)
    
    # Criar arquivo Excel em memória
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Planilha de resumo geral
        resumo_data = {
            'Indicador': ['Mês/Ano', 'Total de OS', 'Total de Serviços', 'Faturamento Total', 'Ticket Médio'],
            'Valor': [f"{mes}/{ano}", resumo['total_os'], resumo['total_servicos'], 
                     f"R$ {resumo['total_faturamento']:,.2f}", f"R$ {resumo['ticket_medio']:,.2f}"]
        }
        pd.DataFrame(resumo_data).to_excel(writer, sheet_name='Resumo_Geral', index=False)
        
        # Planilha de detalhamento
        if not df_detalhe.empty:
            df_detalhe.to_excel(writer, sheet_name='Detalhamento_OS', index=False)
        
        # Planilha de resumo por cliente
        if not df_por_cliente.empty:
            df_por_cliente.to_excel(writer, sheet_name='Resumo_por_Cliente', index=False)
        
        # Planilha de resumo por serviço
        if not df_por_servico.empty:
            df_por_servico.to_excel(writer, sheet_name='Resumo_por_Servico', index=False)
    
    output.seek(0)
    
    nome_arquivo = f"faturamento_{ano}_{mes:02d}.xlsx"
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=nome_arquivo
    )

@app.route('/api/dados')
def api_dados():
    """Endpoint JSON para possíveis integrações futuras"""
    mes = request.args.get('mes', type=int)
    ano = request.args.get('ano', type=int)
    
    if not mes or not ano:
        mes = date.today().month
        ano = date.today().year
    
    ordens, resumo = obter_dados_mes(mes, ano)
    
    return {
        "mes": mes,
        "ano": ano,
        "resumo": resumo,
        "ordens": ordens
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)