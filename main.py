import pandas as pd
import numpy as np
import re
import unicodedata
import sys
import os

# Forçar UTF-8 na consola Windows para suportar caracteres especiais
if sys.stdout.encoding and sys.stdout.encoding.upper() != 'UTF-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import shutil
import argparse
from datetime import datetime

pd.set_option('future.no_silent_downcasting', True)

# ─────────────────────────────────────────────
# CONFIGURAÇÕES DE SEGURANÇA
# ─────────────────────────────────────────────
LIMIAR_VARIACAO_PRECO = 0.30   # 30% — diferença máxima aceite automaticamente
MAX_DIAS_FICHEIRO     = 7      # Ficheiro com mais de N dias gera aviso proeminente
HISTORICO_FILE        = 'HISTORICO_PRECOS.xlsx'
OUTPUT_FILE           = 'Mano-preco-atualizado-final.xlsx'
LOG_FILE              = 'LOG_DECISAO_SAMSUNG.xlsx'
SAMSUNG_FILE          = 'Cotarco-Samsung-preco-atualizado.xlsx'
MANO_FILE             = 'Mano-preco-desatualizado.xlsx'

# ─────────────────────────────────────────────
# ARGUMENTOS DE LINHA DE COMANDO
# ─────────────────────────────────────────────
parser = argparse.ArgumentParser(
    description='Atualizador de Preços e Stock — Mano / Samsung'
)
parser.add_argument(
    '--dry-run',
    action='store_true',
    help='Simula o processamento e mostra o relatório de diferenças SEM gravar ficheiros.'
)
args = parser.parse_args()
DRY_RUN = args.dry_run

print("=" * 60)
if DRY_RUN:
    print("  MODO SIMULAÇÃO (--dry-run) — NENHUM FICHEIRO SERÁ GRAVADO")
else:
    print("  INÍCIO DO PROCESSAMENTO (VERSÃO ROBUSTA)")
print("=" * 60)

# ─────────────────────────────────────────────
# UTILITÁRIOS
# ─────────────────────────────────────────────

def normalize_col(txt):
    """Remove acentos, espaços e coloca em maiúsculas."""
    if pd.isna(txt):
        return ""
    txt = str(txt).strip()
    txt = unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')
    return txt.strip().upper()

def ultra_clean(text):
    """Mantém apenas letras, números e traços (para comparação de referências)."""
    if pd.isna(text):
        return ""
    text = str(text).upper()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'[^A-Z0-9-]', '', text)

def limpar_preco(x):
    """Converte valor de preço para float, tolerando formatos variados."""
    if pd.isna(x):
        return 0.0
    s = str(x).upper()
    s = re.sub(r'[^\d.,]', '', s)   # remove tudo exceto dígitos, ponto e vírgula
    s = s.replace(',', '.')          # normaliza separador decimal
    # Se houver múltiplos pontos (ex: "1.234.567"), remove todos exceto o último
    partes = s.split('.')
    if len(partes) > 2:
        s = ''.join(partes[:-1]) + '.' + partes[-1]
    try:
        return round(float(s), 2)
    except ValueError:
        return 0.0

def auto_detect_header(filepath, max_rows=10):
    """
    Tenta detetar automaticamente a folha e a linha do cabeçalho.
    Retorna o nome/índice da folha e o índice da linha (0-based) com mais colunas preenchidas e não-numéricas.
    """
    best_sheet = 0
    best_row = 0
    best_score = -1

    try:
        xl = pd.ExcelFile(filepath)
        sheets = xl.sheet_names
    except Exception:
        sheets = [0]

    for sheet in sheets:
        for skip in range(max_rows):
            try:
                df_test = pd.read_excel(filepath, sheet_name=sheet, skiprows=skip, nrows=1, header=0)
                score = sum(
                    1 for col in df_test.columns
                    if isinstance(col, str) and len(col.strip()) > 1 and not col.strip().isdigit() and not str(col).startswith('Unnamed:')
                )
                if score > best_score:
                    best_score = score
                    best_row = skip
                    best_sheet = sheet
            except Exception:
                break
    return best_sheet, best_row

def find_column(df_columns_normalized, candidates):
    """
    Recebe lista de nomes de colunas já normalizados e uma lista de candidatos.
    Retorna o nome normalizado que melhor corresponde, ou None.
    Tenta: correspondência exata → contém palavra-chave → começa por.
    """
    for candidate in candidates:
        cand_norm = normalize_col(candidate)
        # 1. Exacta
        if cand_norm in df_columns_normalized:
            return cand_norm
        # 2. A coluna contém o candidato como substring
        for col in df_columns_normalized:
            if cand_norm in col:
                return col
        # 3. O candidato contém a coluna como substring
        for col in df_columns_normalized:
            if col and col in cand_norm:
                return col
    return None

def map_columns(df, col_map):
    """
    Normaliza os nomes das colunas do dataframe e faz o mapeamento para nomes canónicos.
    col_map: dict { nome_canonico: [lista_de_candidatos] }
    Retorna (df_renomeado, dict_mapeamento, lista_nao_encontradas)
    """
    norm_to_original = {normalize_col(c): c for c in df.columns}
    norm_cols = list(norm_to_original.keys())

    rename_map = {}
    nao_encontradas = []

    for nome_canonico, candidatos in col_map.items():
        col_encontrada = find_column(norm_cols, candidatos)
        if col_encontrada:
            original = norm_to_original[col_encontrada]
            rename_map[original] = nome_canonico
        else:
            nao_encontradas.append(nome_canonico)

    df = df.rename(columns=rename_map)
    return df, rename_map, nao_encontradas

# ─────────────────────────────────────────────
# SOLUÇÃO 2 — VERIFICAÇÃO DE IDADE DO FICHEIRO
# ─────────────────────────────────────────────

def verificar_idade_ficheiro(filepath, max_dias):
    """Avisa se o ficheiro de entrada for mais antigo que max_dias."""
    try:
        mtime = os.path.getmtime(filepath)
        data_modificacao = datetime.fromtimestamp(mtime)
        dias_passados = (datetime.now() - data_modificacao).days
        if dias_passados > max_dias:
            print(f"\n{'!' * 60}")
            print(f"  ⚠️  AVISO: '{os.path.basename(filepath)}'")
            print(f"      foi modificado há {dias_passados} dias ({data_modificacao.strftime('%Y-%m-%d %H:%M')}).")
            print(f"      Recomenda-se usar um ficheiro com menos de {max_dias} dias.")
            print(f"  ⚠️  Confirme que está a usar o ficheiro correto e atualizado!")
            print(f"{'!' * 60}\n")
        else:
            print(f"  -> Ficheiro '{os.path.basename(filepath)}' tem {dias_passados} dia(s). ✓")
    except Exception:
        pass

# ─────────────────────────────────────────────
# SOLUÇÃO 1 — PRICE GUARD (VARIAÇÃO EXCESSIVA)
# ─────────────────────────────────────────────

def calcular_variacao(preco_antigo, preco_novo):
    """Calcula a variação percentual entre dois preços."""
    if preco_antigo is None or preco_antigo == 0.0:
        return None
    return abs(preco_novo - preco_antigo) / preco_antigo

def avaliar_price_guard(ref, preco_antigo, preco_novo, limiar):
    """
    Verifica se a variação de preço excede o limiar configurado.
    Retorna (bloqueado: bool, variacao_pct: float|None, mensagem: str)
    """
    variacao = calcular_variacao(preco_antigo, preco_novo)
    if variacao is None:
        return False, None, ""
    pct = variacao * 100
    if variacao > limiar:
        msg = (
            f"  ⛔ BLOQUEADO [{ref}]: "
            f"Preço atual={preco_antigo:.2f}€ | "
            f"Preço novo={preco_novo:.2f}€ | "
            f"Variação={pct:.1f}% > {limiar*100:.0f}%"
        )
        return True, pct, msg
    return False, pct, ""

# ─────────────────────────────────────────────
# SOLUÇÃO 4 — HISTÓRICO CUMULATIVO DE PREÇOS
# ─────────────────────────────────────────────

def registar_historico(registos):
    """
    Adiciona registos ao ficheiro histórico cumulativo HISTORICO_PRECOS.xlsx.
    Cada registo: { Data, Referência, Preço Anterior, Preço Novo, Variação (%), Estado }
    """
    if not registos:
        return
    df_novo = pd.DataFrame(registos)
    if os.path.exists(HISTORICO_FILE):
        try:
            df_hist = pd.read_excel(HISTORICO_FILE)
            df_hist = pd.concat([df_hist, df_novo], ignore_index=True)
        except Exception:
            df_hist = df_novo
    else:
        df_hist = df_novo
    df_hist.to_excel(HISTORICO_FILE, index=False)
    print(f"  -> Histórico atualizado: '{HISTORICO_FILE}' ({len(df_novo)} registo(s) adicionado(s)).")

# ─────────────────────────────────────────────
# SOLUÇÃO 5 — BACKUP AUTOMÁTICO DO FICHEIRO SAMSUNG
# ─────────────────────────────────────────────

def criar_backup(filepath):
    """Cria uma cópia versionada com timestamp do ficheiro de entrada."""
    if not os.path.exists(filepath):
        return
    base, ext = os.path.splitext(filepath)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    backup_path = f"{base}_backup_{timestamp}{ext}"
    try:
        shutil.copy2(filepath, backup_path)
        print(f"  -> Backup criado: '{os.path.basename(backup_path)}' ✓")
    except Exception as e:
        print(f"  -> AVISO: Não foi possível criar backup: {e}")

# ─────────────────────────────────────────────
# PASSO 1 — LER SAMSUNG (FICHEIRO ATUALIZADO)
# ─────────────────────────────────────────────
print(f"\n[Passo 1] A ler '{SAMSUNG_FILE}'...")

# Solução 2: verificar idade do ficheiro de entrada
verificar_idade_ficheiro(SAMSUNG_FILE, MAX_DIAS_FICHEIRO)

# Solução 5: backup automático antes de qualquer alteração (só em execução real)
if not DRY_RUN:
    criar_backup(SAMSUNG_FILE)

try:
    sheet, skip = auto_detect_header(SAMSUNG_FILE)
    if skip > 0:
        print(f"  -> Cabeçalho detetado na folha '{sheet}', linha {skip + 1} (skiprows={skip})")
    else:
        print(f"  -> A usar folha '{sheet}'")
    df_samsung = pd.read_excel(SAMSUNG_FILE, sheet_name=sheet, skiprows=skip)
except FileNotFoundError:
    print(f"ERRO CRÍTICO: Ficheiro '{SAMSUNG_FILE}' não encontrado.")
    print("  Certifique-se de que o ficheiro está na mesma pasta que este script.")
    sys.exit(1)
except Exception as e:
    print(f"ERRO CRÍTICO ao ler '{SAMSUNG_FILE}': {e}")
    sys.exit(1)

print(f"  -> Colunas brutas detetadas ({len(df_samsung.columns)}): {df_samsung.columns.tolist()}")

# Mapeamento tolerante de colunas Samsung
SAMSUNG_COL_MAP = {
    'REFERENCIA': ['REFERENCIA', 'REFERÊNCIA', 'REF', 'REFERENCE', 'CODIGO', 'CÓDIGO', 'COD', 'SKU', 'MODELO'],
    'DESIGNACAO': ['DESIGNACAO', 'DESIGNAÇÃO', 'DESCRICAO', 'DESCRIÇÃO', 'DESCRIPTION', 'NOME', 'NAME', 'PRODUTO', 'TITLE', 'DESC_FAMILIA', 'FAMILIA', 'FAMÍLIA'],
    'STOCK':      ['STOCK', 'ESTOQUE', 'QTY', 'QUANTIDADE', 'QUANTITY', 'QNT'],
    'PRECO':      ['PRECO COM IVA', 'PREÇO COM IVA', 'PRECO', 'PREÇO', 'PRICE', 'PVP', 'VALOR', 'PRECO_FINAL', 'PRECO IVA',
                   'PV1', 'PV2', 'PV5', 'PRECO1', 'PRECO2', 'PRICE1'],
}

df_samsung, mapa_usado, nao_encontradas = map_columns(df_samsung, SAMSUNG_COL_MAP)

if nao_encontradas:
    print(f"\n  AVISO: As seguintes colunas não foram encontradas automaticamente: {nao_encontradas}")
    print(f"  Colunas disponíveis após normalização: {df_samsung.columns.tolist()}")
    print("\n  SUGESTÃO: Verifique os nomes das colunas no ficheiro Excel e adicione-os")
    print("  à lista de candidatos no SAMSUNG_COL_MAP no topo do script.")
    sys.exit(1)

print(f"  -> Mapeamento de colunas aplicado: {mapa_usado}")
print(f"  -> Total de linhas lidas no Samsung: {len(df_samsung)}")

df_samsung['REF_MATCH'] = df_samsung['REFERENCIA'].apply(ultra_clean)
df_samsung['STOCK']  = pd.to_numeric(df_samsung['STOCK'], errors='coerce').fillna(0).astype(int)
df_samsung['PRECO']  = df_samsung['PRECO'].apply(limpar_preco)

antes = len(df_samsung)
df_samsung = df_samsung[df_samsung['REF_MATCH'] != ''].copy()
if len(df_samsung) < antes:
    print(f"  -> {antes - len(df_samsung)} linha(s) ignoradas por referência vazia.")

# ─────────────────────────────────────────────
# PASSO 2 — LER MANO (FICHEIRO A ATUALIZAR)
# ─────────────────────────────────────────────
print(f"\n[Passo 2] A ler '{MANO_FILE}'...")

try:
    sheet_mano, skip_mano = auto_detect_header(MANO_FILE)
    df_mano = pd.read_excel(MANO_FILE, sheet_name=sheet_mano, skiprows=skip_mano)
except FileNotFoundError:
    print(f"ERRO CRÍTICO: Ficheiro '{MANO_FILE}' não encontrado.")
    sys.exit(1)
except Exception as e:
    print(f"ERRO CRÍTICO ao ler '{MANO_FILE}': {e}")
    sys.exit(1)

df_mano.columns = [str(c).strip().lower() for c in df_mano.columns]
print(f"  -> Colunas Mano: {df_mano.columns.tolist()}")
print(f"  -> Total de linhas no Mano: {len(df_mano)}")

ID_CANDIDATES = ['internal_identifier', 'identifier', 'referencia', 'referência', 'ref', 'sku', 'codigo', 'código']
col_id_mano = None
for cand in ID_CANDIDATES:
    matches = [c for c in df_mano.columns if cand in c.lower()]
    if matches:
        col_id_mano = matches[0]
        break

if col_id_mano is None:
    print(f"ERRO CRÍTICO: Coluna de identificador não encontrada no ficheiro Mano.")
    print(f"  Colunas disponíveis: {df_mano.columns.tolist()}")
    print(f"  Adicione o nome correto à lista ID_CANDIDATES no script.")
    sys.exit(1)

print(f"  -> Coluna de identificador Mano: '{col_id_mano}'")
df_mano['ref_match'] = df_mano[col_id_mano].apply(ultra_clean)

# Garantir que colunas booleanas têm dtype compatível para atribuição directa
for col in ['is_active', 'sold_out', 'apply_discounted_price']:
    if col in df_mano.columns:
        df_mano[col] = df_mano[col].astype(object)

# ─────────────────────────────────────────────
# PASSO 3 — CRIAR MAPAS DE REFERÊNCIA
# ─────────────────────────────────────────────
print("\n[Passo 3] A criar mapas de referência...")

mapa_precos = dict(zip(df_samsung['REF_MATCH'], df_samsung['PRECO']))
mapa_stock  = dict(zip(df_samsung['REF_MATCH'], df_samsung['STOCK']))

# Mapa dos preços atuais no Mano (base para o price guard)
col_preco_mano = None
for c in df_mano.columns:
    if 'original_price' in c or 'price' in c:
        col_preco_mano = c
        break

mapa_precos_atuais_mano = {}
if col_preco_mano:
    for _, r in df_mano.iterrows():
        ref = r['ref_match']
        preco_atual = limpar_preco(r.get(col_preco_mano, 0.0))
        if ref:
            mapa_precos_atuais_mano[ref] = preco_atual

referencias_na_mano = set(df_mano['ref_match'].unique())
refs_correspondidas = set()
total_atualizados   = 0

# ─────────────────────────────────────────────
# PASSO 4 — ATUALIZAR PRODUTOS EXISTENTES
#           + SOLUÇÃO 1 (Price Guard)
#           + SOLUÇÃO 3 (Dry-Run Diff)
# ─────────────────────────────────────────────
print("[Passo 4] A atualizar produtos existentes no Mano...")

for col in ['original_price', 'quantity']:
    if col not in df_mano.columns:
        df_mano[col] = np.nan

for col in ['is_active', 'sold_out']:
    if col not in df_mano.columns:
        df_mano[col] = pd.array([None] * len(df_mano), dtype=object)

# Solução 3: cabeçalho do relatório de diff (dry-run)
if DRY_RUN:
    print("\n  -- RELATORIO DE DIFERENCAS (SIMULACAO) --")
    print(f"  {'Referencia':<32} {'Preco Atual':>12} {'Preco Novo':>12} {'Variacao':>10}  Estado")
    print(f"  {'-'*32} {'-'*12} {'-'*12} {'-'*10}  {'-'*32}")

registos_historico  = []
alertas_price_guard = []

for idx, row in df_mano.iterrows():
    ref = row['ref_match']
    if ref not in mapa_stock:
        continue

    refs_correspondidas.add(ref)
    stock_novo  = mapa_stock[ref]
    preco_novo  = mapa_precos[ref]
    preco_atual = mapa_precos_atuais_mano.get(ref, None)

    # Solução 1: Price Guard
    bloqueado, variacao_pct, msg_guard = avaliar_price_guard(
        ref, preco_atual, preco_novo, LIMIAR_VARIACAO_PRECO
    )

    # Solução 3: linha do diff no modo dry-run
    if DRY_RUN:
        preco_ant_str = f"{preco_atual:.2f}EUR" if preco_atual is not None else "N/D"
        variacao_str  = f"{variacao_pct:.1f}%" if variacao_pct is not None else "N/D"
        estado_str    = "[BLOQUEADO] variacao excessiva" if bloqueado else "[OK]"
        print(f"  {ref:<32} {preco_ant_str:>12} {preco_novo:>10.2f}EUR {variacao_str:>10}  {estado_str}")

    if bloqueado:
        alertas_price_guard.append(msg_guard)
        # Regista no histórico como BLOQUEADO (não aplica a alteração)
        registos_historico.append({
            'Data':           datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Referência':     ref,
            'Preço Anterior': preco_atual,
            'Preço Novo':     preco_novo,
            'Variação (%)':   round(variacao_pct, 2) if variacao_pct is not None else None,
            'Estado':         'BLOQUEADO_VARIACAO_EXCESSIVA',
        })
        continue  # Não aplica a atualização

    # Aplica a atualização (apenas em execução real)
    if not DRY_RUN:
        df_mano.at[idx, 'original_price'] = preco_novo
        df_mano.at[idx, 'quantity']       = stock_novo
        if stock_novo >= 3:
            df_mano.at[idx, 'is_active'] = True
            df_mano.at[idx, 'sold_out']  = False
        else:
            df_mano.at[idx, 'is_active'] = False
            df_mano.at[idx, 'sold_out']  = True

    total_atualizados += 1

    # Solução 4: adiciona ao histórico cumulativo
    registos_historico.append({
        'Data':           datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Referência':     ref,
        'Preço Anterior': preco_atual,
        'Preço Novo':     preco_novo,
        'Variação (%)':   round(variacao_pct, 2) if variacao_pct is not None else None,
        'Estado':         'ATUALIZADO',
    })

if DRY_RUN:
    print(f"  {'-'*90}")

# Mostrar todos os alertas de price guard em bloco
if alertas_price_guard:
    print(f"\n[!!!] ALERTAS PRICE GUARD -- {len(alertas_price_guard)} produto(s) BLOQUEADO(s) [!!!]")
    for alerta in alertas_price_guard:
        print(alerta)
    print()

print(f"  -> {total_atualizados} produto(s) {'seriam' if DRY_RUN else ''} atualizados.")
print(f"  -> {len(alertas_price_guard)} produto(s) bloqueados por variacao de preco >{LIMIAR_VARIACAO_PRECO*100:.0f}%.")

# ─────────────────────────────────────────────
# PASSO 5 — ADICIONAR NOVOS PRODUTOS
# ─────────────────────────────────────────────
print("[Passo 5] A analisar e adicionar novos produtos...")

log_decisao = []
novas_linhas = []

for _, row in df_samsung.iterrows():
    ref_orig  = row['REFERENCIA']
    ref_limpa = row['REF_MATCH']
    stock     = row['STOCK']
    preco     = row['PRECO']
    design    = row.get('DESIGNACAO', '')

    if ref_limpa in referencias_na_mano:
        status = "IGNORADO: Já existe no ficheiro Mano (atualizado no Passo 4)"
    elif stock < 3:
        status = f"IGNORADO: Stock insuficiente ({stock} < 3)"
    elif ref_limpa == "":
        status = "IGNORADO: Referência vazia ou inválida"
    elif preco == 0.0:
        status = "IGNORADO: Preço igual a zero"
    else:
        status = "ADICIONADO: Produto novo com stock suficiente"
        if not DRY_RUN:
            nova = {col: np.nan for col in df_mano.columns}
            nova[col_id_mano]              = ref_orig
            nova['title_pt']               = design if 'title_pt' in df_mano.columns else np.nan
            nova['original_price']         = preco
            nova['quantity']               = stock
            nova['is_active']              = True
            nova['sold_out']               = False
            nova['apply_discounted_price'] = False
            novas_linhas.append(nova)

    log_decisao.append({
        'Referência Original':      ref_orig,
        'Referência Limpa (Match)': ref_limpa,
        'Stock Lido':               stock,
        'Preço Lido':               preco,
        'Decisão':                  status,
    })

novos_count = sum(1 for d in log_decisao if d['Decisão'].startswith('ADICIONADO'))
print(f"  -> {novos_count} novo(s) produto(s) {'seriam adicionados' if DRY_RUN else 'a adicionar'}.")

# ─────────────────────────────────────────────
# PASSO 6 — CONSOLIDAR E GRAVAR FICHEIROS
# ─────────────────────────────────────────────
print("\n[Passo 6] A gravar ficheiros finais...")

if DRY_RUN:
    print("\n  ⚠️  MODO SIMULAÇÃO ATIVO — nenhum ficheiro foi gravado.")
    print("  Para aplicar as alterações, execute sem a flag --dry-run:")
    print("      python main.py")
else:
    if novas_linhas:
        df_novas = pd.DataFrame(novas_linhas)
        df_novas = df_novas[[c for c in df_novas.columns if c in df_mano.columns]]
        df_mano  = pd.concat([df_mano, df_novas], ignore_index=True)

    df_mano = df_mano.drop(columns=['ref_match'], errors='ignore')

    for col in ['is_active', 'sold_out', 'apply_discounted_price']:
        if col in df_mano.columns:
            df_mano[col] = df_mano[col].fillna(False).infer_objects(copy=False).astype(bool)

    df_mano.to_excel(OUTPUT_FILE, index=False)
    pd.DataFrame(log_decisao).to_excel(LOG_FILE, index=False)

    # Solução 4: gravar histórico cumulativo de preços
    registar_historico(registos_historico)

    print(f"  -> Ficheiro final gravado:   '{OUTPUT_FILE}'")
    print(f"  -> Log de decisões gravado:  '{LOG_FILE}'")

# ─────────────────────────────────────────────
# RELATÓRIO FINAL
# ─────────────────────────────────────────────
ignorados_stock  = sum(1 for d in log_decisao if 'Stock insuficiente' in d['Decisão'])
ignorados_existe = sum(1 for d in log_decisao if 'Já existe'          in d['Decisão'])
ignorados_preco  = sum(1 for d in log_decisao if 'Preço igual a zero'  in d['Decisão'])

print("\n" + "=" * 60)
print("  RELATÓRIO FINAL" + (" (SIMULAÇÃO)" if DRY_RUN else ""))
print("=" * 60)
print(f"  Produtos Samsung lidos:            {len(df_samsung)}")
print(f"  Produtos Mano lidos:               {len(df_mano) - len(novas_linhas)}")
print(f"  Produtos atualizados:              {total_atualizados}")
print(f"  Novos produtos adicionados:        {novos_count}")
print(f"  Ignorados (já existia):            {ignorados_existe}")
print(f"  Ignorados (stock < 3):             {ignorados_stock}")
print(f"  Ignorados (preco = 0):             {ignorados_preco}")
print(f"  [!] Bloqueados (variacao >{LIMIAR_VARIACAO_PRECO*100:.0f}%):     {len(alertas_price_guard)}")
if not DRY_RUN:
    print(f"\n  Ficheiro final:    '{OUTPUT_FILE}'")
    print(f"  Log de decisões:   '{LOG_FILE}'")
    print(f"  Histórico preços:  '{HISTORICO_FILE}'")
print("=" * 60)
if DRY_RUN:
    print("\n  ▶  Para aplicar as alterações: python main.py")
    print("  ▶  Para simular novamente:     python main.py --dry-run")