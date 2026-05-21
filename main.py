import pandas as pd
import numpy as np
import re
import unicodedata
import sys

pd.set_option('future.no_silent_downcasting', True)

print("=" * 60)
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
    """Mantém apenas letras e números (para comparação de referências)."""
    if pd.isna(text):
        return ""
    text = str(text).upper()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'[^A-Z0-9]', '', text)

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
        return float(s)
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
    # Guardar mapa de nome_normalizado -> nome_original
    norm_to_original = {normalize_col(c): c for c in df.columns}
    norm_cols = list(norm_to_original.keys())

    rename_map = {}    # nome_original -> nome_canonico
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
# PASSO 1 — LER SAMSUNG (FICHEIRO ATUALIZADO)
# ─────────────────────────────────────────────
SAMSUNG_FILE = 'Cotarco-Samsung-preco-atualizado.xlsx'
MANO_FILE    = 'Mano-preco-desatualizado.xlsx'

print(f"\n[Passo 1] A ler '{SAMSUNG_FILE}'...")

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

# Diagnóstico inicial
print(f"  -> Colunas brutas detetadas ({len(df_samsung.columns)}): {df_samsung.columns.tolist()}")

# Mapeamento tolerante de colunas Samsung
SAMSUNG_COL_MAP = {
    'REFERENCIA': ['REFERENCIA', 'REFERÊNCIA', 'REF', 'REFERENCE', 'CODIGO', 'CÓDIGO', 'COD', 'SKU', 'MODELO'],
    'DESIGNACAO': ['DESIGNACAO', 'DESIGNAÇÃO', 'DESCRICAO', 'DESCRIÇÃO', 'DESCRIPTION', 'NOME', 'NAME', 'PRODUTO', 'TITLE'],
    'STOCK':      ['STOCK', 'ESTOQUE', 'QTY', 'QUANTIDADE', 'QUANTITY', 'QNT'],
    'PRECO':      ['PRECO COM IVA', 'PREÇO COM IVA', 'PRECO', 'PREÇO', 'PRICE', 'PVP', 'VALOR', 'PRECO_FINAL', 'PRECO IVA'],
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

# Limpar e converter dados Samsung
df_samsung['REF_MATCH'] = df_samsung['REFERENCIA'].apply(ultra_clean)
df_samsung['STOCK']  = pd.to_numeric(df_samsung['STOCK'], errors='coerce').fillna(0).astype(int)
df_samsung['PRECO']  = df_samsung['PRECO'].apply(limpar_preco)

# Remover linhas sem referência
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

# Encontrar coluna de identificador no Mano de forma tolerante
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

# ─────────────────────────────────────────────
# PASSO 3 — CRIAR MAPAS DE REFERÊNCIA
# ─────────────────────────────────────────────
print("\n[Passo 3] A criar mapas de referência...")

mapa_precos = dict(zip(df_samsung['REF_MATCH'], df_samsung['PRECO']))
mapa_stock  = dict(zip(df_samsung['REF_MATCH'], df_samsung['STOCK']))

referencias_na_mano       = set(df_mano['ref_match'].unique())
refs_correspondidas        = set()

total_atualizados = 0

# ─────────────────────────────────────────────
# PASSO 4 — ATUALIZAR PRODUTOS EXISTENTES
# ─────────────────────────────────────────────
print("[Passo 4] A atualizar produtos existentes no Mano...")

for col in ['original_price', 'quantity', 'is_active', 'sold_out']:
    if col not in df_mano.columns:
        df_mano[col] = np.nan

for idx, row in df_mano.iterrows():
    ref = row['ref_match']
    if ref in mapa_stock:
        refs_correspondidas.add(ref)
        stock_atual = mapa_stock[ref]
        df_mano.at[idx, 'original_price'] = mapa_precos[ref]
        df_mano.at[idx, 'quantity']       = stock_atual
        if stock_atual >= 3:
            df_mano.at[idx, 'is_active'] = True
            df_mano.at[idx, 'sold_out']  = False
        else:
            df_mano.at[idx, 'is_active'] = False
            df_mano.at[idx, 'sold_out']  = True
        total_atualizados += 1

print(f"  -> {total_atualizados} produto(s) atualizados.")

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
        nova = {col: np.nan for col in df_mano.columns}
        nova[col_id_mano]            = ref_orig
        nova['title_pt']             = design if 'title_pt' in df_mano.columns else np.nan
        nova['original_price']       = preco
        nova['quantity']             = stock
        nova['is_active']            = True
        nova['sold_out']             = False
        nova['apply_discounted_price'] = False
        novas_linhas.append(nova)

    log_decisao.append({
        'Referência Original':      ref_orig,
        'Referência Limpa (Match)': ref_limpa,
        'Stock Lido':               stock,
        'Preço Lido':               preco,
        'Decisão':                  status,
    })

print(f"  -> {len(novas_linhas)} novo(s) produto(s) a adicionar.")

# ─────────────────────────────────────────────
# PASSO 6 — CONSOLIDAR E GRAVAR FICHEIROS
# ─────────────────────────────────────────────
print("\n[Passo 6] A gravar ficheiros finais...")

if novas_linhas:
    df_novas = pd.DataFrame(novas_linhas)
    # Garantir que só colunas existentes no Mano são adicionadas
    df_novas = df_novas[[c for c in df_novas.columns if c in df_mano.columns]]
    df_mano  = pd.concat([df_mano, df_novas], ignore_index=True)

# Remover coluna auxiliar
df_mano = df_mano.drop(columns=['ref_match'], errors='ignore')

# Normalizar booleanos
for col in ['is_active', 'sold_out', 'apply_discounted_price']:
    if col in df_mano.columns:
        df_mano[col] = df_mano[col].fillna(False).infer_objects(copy=False).astype(bool)

# Gravar
OUTPUT_FILE = 'Mano-preco-atualizado-final.xlsx'
LOG_FILE    = 'LOG_DECISAO_SAMSUNG.xlsx'

df_mano.to_excel(OUTPUT_FILE, index=False)
pd.DataFrame(log_decisao).to_excel(LOG_FILE, index=False)

# ─────────────────────────────────────────────
# RELATÓRIO FINAL
# ─────────────────────────────────────────────
ignorados_stock  = sum(1 for d in log_decisao if 'Stock insuficiente' in d['Decisão'])
ignorados_existe = sum(1 for d in log_decisao if 'Já existe'          in d['Decisão'])
ignorados_preco  = sum(1 for d in log_decisao if 'Preço igual a zero'  in d['Decisão'])

print("\n" + "=" * 60)
print("  RELATÓRIO FINAL")
print("=" * 60)
print(f"  Produtos Samsung lidos:        {len(df_samsung)}")
print(f"  Produtos Mano lidos:           {len(df_mano) - len(novas_linhas)}")
print(f"  Produtos atualizados:          {total_atualizados}")
print(f"  Novos produtos adicionados:    {len(novas_linhas)}")
print(f"  Ignorados (já existia):        {ignorados_existe}")
print(f"  Ignorados (stock < 3):         {ignorados_stock}")
print(f"  Ignorados (preço = 0):         {ignorados_preco}")
print(f"\n  Ficheiro final:  '{OUTPUT_FILE}'")
print(f"  Log de decisões: '{LOG_FILE}'")
print("=" * 60)