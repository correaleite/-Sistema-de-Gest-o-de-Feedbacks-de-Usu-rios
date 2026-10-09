"""
FeedSmart - Sistema de Gestão de Feedbacks de Usuários (P5)

Funcionalidades:
    - Cadastro e listagem de usuários (persistidos em JSON)
    - Registro de feedbacks associados a usuários (persistidos em TXT)
    - Relatórios: médias, contagens, categorias (promotor/neutro/detrator)
    - Exportação de relatórios em TXT e JSON
    - Tratamento de erros e validação de entradas
"""

import json
import os
from datetime import datetime

# ----------------------------------------------------------------------
# Constantes e configuração
# ----------------------------------------------------------------------
ARQ_USUARIOS = "usuarios.json"
ARQ_FEEDBACKS = "feedbacks.txt"
ARQ_RELATORIO_TXT = "relatorio.txt"
ARQ_RELATORIO_JSON = "relatorio.json"

# Tupla: valores fixos que não mudam durante a execução
TIPOS_USUARIO = ("Cliente", "Beta Tester", "Colaborador")
CATEGORIAS = ("Detrator", "Neutro", "Promotor")  # índices da matriz

LARGURA = 60


# ----------------------------------------------------------------------
# Utilitários de interface (UX textual)
# ----------------------------------------------------------------------
def linha(char="="):
    """Imprime uma linha separadora com a largura padrão do terminal."""
    print(char * LARGURA)


def titulo(texto):
    """Imprime um título centralizado entre linhas separadoras."""
    print()
    linha()
    print(texto.center(LARGURA))
    linha()


def sucesso(msg):
    """Exibe uma mensagem de sucesso."""
    print(f"  [OK] {msg}")


def erro(msg):
    """Exibe uma mensagem de erro."""
    print(f"  [ERRO] {msg}")


def aviso(msg):
    """Exibe uma mensagem de aviso."""
    print(f"  [!] {msg}")


def pausar():
    """Aguarda o usuário pressionar ENTER antes de continuar."""
    input("\n  Pressione ENTER para voltar ao menu...")


# ----------------------------------------------------------------------
# Leitura e validação de entradas
# ----------------------------------------------------------------------
def ler_texto(prompt, minimo=2, maximo=200):
    """
    Lê um texto não vazio do terminal.

    Args:
        prompt (str): mensagem exibida ao usuário.
        minimo (int): quantidade mínima de caracteres.
        maximo (int): quantidade máxima de caracteres.

    Returns:
        str: texto validado, sem espaços nas pontas.
    """
    while True:
        valor = input(prompt).strip()
        if len(valor) < minimo:
            erro(f"Digite pelo menos {minimo} caracteres.")
        elif len(valor) > maximo:
            erro(f"Máximo de {maximo} caracteres.")
        else:
            return valor


def ler_inteiro(prompt, minimo, maximo):
    """
    Lê um número inteiro dentro de um intervalo.

    Args:
        prompt (str): mensagem exibida ao usuário.
        minimo (int): menor valor aceito.
        maximo (int): maior valor aceito.

    Returns:
        int: valor validado.
    """
    while True:
        try:
            valor = int(input(prompt).strip())
        except ValueError:
            erro("Digite um número inteiro válido.")
            continue
        if minimo <= valor <= maximo:
            return valor
        erro(f"O valor deve estar entre {minimo} e {maximo}.")


def ler_data(prompt):
    """
    Lê uma data no formato dd/mm/aaaa. ENTER usa a data de hoje.

    Args:
        prompt (str): mensagem exibida ao usuário.

    Returns:
        str: data no formato dd/mm/aaaa, nunca no futuro.
    """
    while True:
        entrada = input(prompt).strip()
        if not entrada:
            return datetime.now().strftime("%d/%m/%Y")
        try:
            data = datetime.strptime(entrada, "%d/%m/%Y")
        except ValueError:
            erro("Formato inválido. Use dd/mm/aaaa (ex.: 25/12/2025).")
            continue
        if data > datetime.now():
            erro("A data não pode estar no futuro.")
            continue
        return data.strftime("%d/%m/%Y")


def escolher_tipo_usuario():
    """
    Mostra os tipos de usuário disponíveis e lê a escolha.

    Returns:
        str: tipo de usuário escolhido.
    """
    print("  Tipos de usuário:")
    for i, tipo in enumerate(TIPOS_USUARIO, start=1):
        print(f"    {i}) {tipo}")
    opcao = ler_inteiro("  Escolha o tipo: ", 1, len(TIPOS_USUARIO))
    return TIPOS_USUARIO[opcao - 1]


# ----------------------------------------------------------------------
# Persistência (JSON para usuários, TXT para feedbacks)
# ----------------------------------------------------------------------
def carregar_usuarios():
    """
    Carrega a lista de usuários do arquivo JSON.

    Returns:
        list[dict]: usuários cadastrados (lista vazia se não houver arquivo
        ou se o arquivo estiver corrompido).
    """
    if not os.path.exists(ARQ_USUARIOS):
        return []
    try:
        with open(ARQ_USUARIOS, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if not isinstance(dados, list):
            raise ValueError("Formato inesperado")
        return dados
    except (json.JSONDecodeError, ValueError):
        aviso(f"'{ARQ_USUARIOS}' está corrompido. Iniciando sem usuários.")
        return []
    except OSError as e:
        erro(f"Não foi possível ler '{ARQ_USUARIOS}': {e}")
        return []


def salvar_usuarios(usuarios):
    """
    Salva a lista de usuários em JSON.

    Args:
        usuarios (list[dict]): usuários a serem gravados.

    Returns:
        bool: True se salvou com sucesso, False caso contrário.
    """
    try:
        with open(ARQ_USUARIOS, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, ensure_ascii=False, indent=4)
        return True
    except OSError as e:
        erro(f"Falha ao salvar usuários: {e}")
        return False


def _limpar(texto):
    """Remove quebras de linha e o separador '|' para gravar em TXT."""
    return " ".join(texto.replace("|", "/").split())


def carregar_feedbacks():
    """
    Carrega feedbacks do arquivo TXT.

    Formato de cada linha: id|id_usuario|produto|nota|data|texto

    Returns:
        list[dict]: feedbacks válidos. Linhas malformadas são ignoradas.
    """
    feedbacks = []
    if not os.path.exists(ARQ_FEEDBACKS):
        return feedbacks
    try:
        with open(ARQ_FEEDBACKS, "r", encoding="utf-8") as f:
            for n, linha_txt in enumerate(f, start=1):
                linha_txt = linha_txt.strip()
                if not linha_txt:
                    continue
                partes = linha_txt.split("|", 5)
                try:
                    if len(partes) != 6:
                        raise ValueError("campos insuficientes")
                    nota = int(partes[3])
                    if not 0 <= nota <= 10:
                        raise ValueError("nota fora do intervalo")
                    feedbacks.append({
                        "id": int(partes[0]),
                        "id_usuario": int(partes[1]),
                        "produto": partes[2],
                        "nota": nota,
                        "data": partes[4],
                        "texto": partes[5],
                    })
                except ValueError as e:
                    aviso(f"Linha {n} ignorada em '{ARQ_FEEDBACKS}': {e}")
    except OSError as e:
        erro(f"Não foi possível ler '{ARQ_FEEDBACKS}': {e}")
    return feedbacks


def salvar_feedbacks(feedbacks):
    """
    Grava todos os feedbacks no arquivo TXT.

    Args:
        feedbacks (list[dict]): feedbacks a serem gravados.

    Returns:
        bool: True se salvou com sucesso, False caso contrário.
    """
    try:
        with open(ARQ_FEEDBACKS, "w", encoding="utf-8") as f:
            for fb in feedbacks:
                f.write(
                    f"{fb['id']}|{fb['id_usuario']}|{_limpar(fb['produto'])}|"
                    f"{fb['nota']}|{fb['data']}|{_limpar(fb['texto'])}\n"
                )
        return True
    except OSError as e:
        erro(f"Falha ao salvar feedbacks: {e}")
        return False


def proximo_id(registros):
    """
    Calcula o próximo ID sequencial para uma lista de dicionários.

    Args:
        registros (list[dict]): registros que possuem a chave 'id'.

    Returns:
        int: maior ID existente + 1 (ou 1 se a lista estiver vazia).
    """
    return max((r["id"] for r in registros), default=0) + 1


# ----------------------------------------------------------------------
# RF01 - Usuários
# ----------------------------------------------------------------------
def cadastrar_usuario(usuarios):
    """
    Cadastra um novo usuário solicitando nome, idade, profissão e tipo.

    Args:
        usuarios (list[dict]): lista de usuários (modificada in-place).
    """
    titulo("CADASTRO DE USUÁRIO")
    nome = ler_texto("  Nome: ", minimo=3, maximo=80)
    idade = ler_inteiro("  Idade (1-120): ", 1, 120)
    profissao = ler_texto("  Profissão: ", minimo=2, maximo=60)
    tipo = escolher_tipo_usuario()

    usuario = {
        "id": proximo_id(usuarios),
        "nome": nome,
        "idade": idade,
        "profissao": profissao,
        "tipo": tipo,
    }
    usuarios.append(usuario)
    if salvar_usuarios(usuarios):
        sucesso(f"Usuário '{nome}' cadastrado com ID {usuario['id']}.")


def listar_usuarios(usuarios):
    """
    Exibe os usuários cadastrados em formato de tabela.

    Args:
        usuarios (list[dict]): usuários a serem listados.
    """
    titulo("USUÁRIOS CADASTRADOS")
    if not usuarios:
        aviso("Nenhum usuário cadastrado ainda.")
        return
    print(f"  {'ID':<4}{'Nome':<22}{'Idade':<7}{'Profissão':<16}{'Tipo'}")
    print("  " + "-" * (LARGURA - 4))
    for u in usuarios:
        print(f"  {u['id']:<4}{u['nome'][:20]:<22}{u['idade']:<7}"
              f"{u['profissao'][:14]:<16}{u['tipo']}")
    print(f"\n  Total: {len(usuarios)} usuário(s)")


def buscar_usuario(usuarios, id_usuario):
    """
    Busca um usuário pelo ID.

    Args:
        usuarios (list[dict]): lista de usuários.
        id_usuario (int): ID procurado.

    Returns:
        dict | None: o usuário encontrado ou None.
    """
    for u in usuarios:
        if u["id"] == id_usuario:
            return u
    return None


# ----------------------------------------------------------------------
# RF02 - Feedbacks
# ----------------------------------------------------------------------
def registrar_feedback(usuarios, feedbacks):
    """
    Registra um feedback associado a um usuário existente.

    Args:
        usuarios (list[dict]): usuários cadastrados.
        feedbacks (list[dict]): feedbacks (modificada in-place).
    """
    titulo("REGISTRAR FEEDBACK")
    if not usuarios:
        aviso("Cadastre ao menos um usuário antes de registrar feedbacks.")
        return

    for u in usuarios:
        print(f"    {u['id']}) {u['nome']} ({u['tipo']})")
    ids_validos = {u["id"] for u in usuarios}
    while True:
        id_usuario = ler_inteiro("\n  ID do usuário: ", 1, 10**9)
        if id_usuario in ids_validos:
            break
        erro("ID não encontrado. Escolha um dos IDs listados.")

    produto = ler_texto("  Produto: ", minimo=2, maximo=60)
    texto = ler_texto("  Comentário: ", minimo=3, maximo=300)
    nota = ler_inteiro("  Nota (0 a 10): ", 0, 10)
    data = ler_data("  Data (dd/mm/aaaa, ENTER = hoje): ")

    feedback = {
        "id": proximo_id(feedbacks),
        "id_usuario": id_usuario,
        "produto": produto,
        "nota": nota,
        "data": data,
        "texto": texto,
    }
    feedbacks.append(feedback)
    if salvar_feedbacks(feedbacks):
        sucesso(f"Feedback #{feedback['id']} registrado.")


def classificar_nota(nota):
    """
    Classifica uma nota em categoria (estilo NPS).

    Args:
        nota (int): nota de 0 a 10.

    Returns:
        int: 0 = Detrator (0-6), 1 = Neutro (7-8), 2 = Promotor (9-10).
    """
    if nota <= 6:
        return 0
    if nota <= 8:
        return 1
    return 2


# ----------------------------------------------------------------------
# RF03 - Relatórios
# ----------------------------------------------------------------------
def calcular_estatisticas(usuarios, feedbacks):
    """
    Calcula as estatísticas usadas nos relatórios.

    Args:
        usuarios (list[dict]): usuários cadastrados.
        feedbacks (list[dict]): feedbacks registrados.

    Returns:
        dict: média geral, total, médias/contagens por produto e por tipo
        de usuário, e matriz produto x categoria.
    """
    total = len(feedbacks)
    media_geral = sum(f["nota"] for f in feedbacks) / total if total else 0.0

    notas_produto = {}
    for f in feedbacks:
        notas_produto.setdefault(f["produto"], []).append(f["nota"])

    produtos = sorted(notas_produto)
    por_produto = {
        p: {
            "quantidade": len(notas_produto[p]),
            "media": round(sum(notas_produto[p]) / len(notas_produto[p]), 2),
        }
        for p in produtos
    }

    # Matriz: linhas = produtos, colunas = categorias (Detrator/Neutro/Promotor)
    matriz = [[0] * len(CATEGORIAS) for _ in produtos]
    for f in feedbacks:
        matriz[produtos.index(f["produto"])][classificar_nota(f["nota"])] += 1

    tipo_por_id = {u["id"]: u["tipo"] for u in usuarios}
    notas_tipo = {}
    for f in feedbacks:
        tipo = tipo_por_id.get(f["id_usuario"], "Desconhecido")
        notas_tipo.setdefault(tipo, []).append(f["nota"])
    por_tipo = {
        t: {"quantidade": len(n), "media": round(sum(n) / len(n), 2)}
        for t, n in sorted(notas_tipo.items())
    }

    return {
        "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total_usuarios": len(usuarios),
        "total_feedbacks": total,
        "media_geral": round(media_geral, 2),
        "por_produto": por_produto,
        "por_tipo_usuario": por_tipo,
        "categorias": list(CATEGORIAS),
        "produtos_matriz": produtos,
        "matriz_produto_categoria": matriz,
    }


def montar_relatorio_texto(est):
    """
    Converte as estatísticas em um relatório formatado em texto.

    Args:
        est (dict): resultado de calcular_estatisticas().

    Returns:
        str: relatório pronto para exibir ou gravar em TXT.
    """
    l = []
    l.append("=" * LARGURA)
    l.append("RELATÓRIO FEEDSMART".center(LARGURA))
    l.append(f"Gerado em {est['gerado_em']}".center(LARGURA))
    l.append("=" * LARGURA)
    l.append(f"Usuários cadastrados : {est['total_usuarios']}")
    l.append(f"Feedbacks recebidos  : {est['total_feedbacks']}")
    l.append(f"Média geral das notas: {est['media_geral']:.2f}")

    l.append("\nPor produto:")
    if est["por_produto"]:
        for p, d in est["por_produto"].items():
            barra = "#" * round(d["media"])
            l.append(f"  {p[:20]:<20} média {d['media']:>5.2f} "
                     f"({d['quantidade']} fb) {barra}")
    else:
        l.append("  (sem dados)")

    l.append("\nPor tipo de usuário:")
    if est["por_tipo_usuario"]:
        for t, d in est["por_tipo_usuario"].items():
            l.append(f"  {t:<20} média {d['media']:>5.2f} ({d['quantidade']} fb)")
    else:
        l.append("  (sem dados)")

    l.append("\nCategorias por produto (Detrator 0-6 | Neutro 7-8 | Promotor 9-10):")
    if est["produtos_matriz"]:
        l.append(f"  {'Produto':<20}" + "".join(f"{c:>10}" for c in est["categorias"]))
        for p, linha_m in zip(est["produtos_matriz"], est["matriz_produto_categoria"]):
            l.append(f"  {p[:20]:<20}" + "".join(f"{v:>10}" for v in linha_m))
    else:
        l.append("  (sem dados)")
    return "\n".join(l)


def mostrar_relatorio(usuarios, feedbacks):
    """
    Exibe o relatório geral no terminal.

    Args:
        usuarios (list[dict]): usuários cadastrados.
        feedbacks (list[dict]): feedbacks registrados.
    """
    if not feedbacks:
        titulo("RELATÓRIO GERAL")
        aviso("Ainda não há feedbacks para analisar.")
        return
    print()
    print(montar_relatorio_texto(calcular_estatisticas(usuarios, feedbacks)))


def listar_feedbacks_por_produto(usuarios, feedbacks):
    """
    Lista os feedbacks de um produto escolhido pelo usuário.

    Args:
        usuarios (list[dict]): usuários cadastrados.
        feedbacks (list[dict]): feedbacks registrados.
    """
    titulo("FEEDBACKS POR PRODUTO")
    if not feedbacks:
        aviso("Ainda não há feedbacks registrados.")
        return

    produtos = sorted({f["produto"] for f in feedbacks})
    for i, p in enumerate(produtos, start=1):
        print(f"    {i}) {p}")
    escolha = ler_inteiro("\n  Escolha o produto: ", 1, len(produtos))
    produto = produtos[escolha - 1]

    nomes = {u["id"]: u["nome"] for u in usuarios}
    selecionados = [f for f in feedbacks if f["produto"] == produto]
    print(f"\n  Produto: {produto} ({len(selecionados)} feedback(s))")
    print("  " + "-" * (LARGURA - 4))
    for f in selecionados:
        autor = nomes.get(f["id_usuario"], "Usuário removido")
        print(f"  #{f['id']} | {f['data']} | nota {f['nota']:>2} | {autor}")
        print(f"      \"{f['texto']}\"")
    media = sum(f["nota"] for f in selecionados) / len(selecionados)
    print(f"\n  Média do produto: {media:.2f}")


def exportar_relatorio(usuarios, feedbacks):
    """
    Exporta o relatório para TXT e JSON.

    Args:
        usuarios (list[dict]): usuários cadastrados.
        feedbacks (list[dict]): feedbacks registrados.
    """
    titulo("EXPORTAR RELATÓRIO")
    if not feedbacks:
        aviso("Sem feedbacks para exportar.")
        return
    est = calcular_estatisticas(usuarios, feedbacks)
    try:
        with open(ARQ_RELATORIO_TXT, "w", encoding="utf-8") as f:
            f.write(montar_relatorio_texto(est) + "\n")
        with open(ARQ_RELATORIO_JSON, "w", encoding="utf-8") as f:
            json.dump(est, f, ensure_ascii=False, indent=4)
        sucesso(f"Arquivos gerados: {ARQ_RELATORIO_TXT} e {ARQ_RELATORIO_JSON}")
    except OSError as e:
        erro(f"Falha ao exportar relatório: {e}")


# ----------------------------------------------------------------------
# RF06 - Menu principal
# ----------------------------------------------------------------------
def exibir_menu():
    """Imprime as opções do menu principal."""
    titulo("FEEDSMART - GESTÃO DE FEEDBACKS")
    print("  1) Cadastrar usuário")
    print("  2) Listar usuários")
    print("  3) Registrar feedback")
    print("  4) Relatório geral (médias, contagens, categorias)")
    print("  5) Feedbacks por produto")
    print("  6) Exportar relatório (TXT + JSON)")
    print("  0) Sair")
    linha("-")


def main():
    """Ponto de entrada: carrega os dados e executa o laço do menu."""
    usuarios = carregar_usuarios()
    feedbacks = carregar_feedbacks()

    # Descarta feedbacks cujo usuário não existe mais (integridade referencial)
    ids = {u["id"] for u in usuarios}
    orfaos = [f for f in feedbacks if f["id_usuario"] not in ids]
    if orfaos:
        aviso(f"{len(orfaos)} feedback(s) sem usuário correspondente foram mantidos "
              "como 'Usuário removido'.")

    while True:
        exibir_menu()
        try:
            opcao = input("  Opção: ").strip()
            if opcao == "1":
                cadastrar_usuario(usuarios)
            elif opcao == "2":
                listar_usuarios(usuarios)
            elif opcao == "3":
                registrar_feedback(usuarios, feedbacks)
            elif opcao == "4":
                mostrar_relatorio(usuarios, feedbacks)
            elif opcao == "5":
                listar_feedbacks_por_produto(usuarios, feedbacks)
            elif opcao == "6":
                exportar_relatorio(usuarios, feedbacks)
            elif opcao == "0":
                print("\n  Dados salvos. Até logo!\n")
                break
            else:
                erro("Opção inválida. Digite um número do menu.")
                continue
            pausar()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Encerrando o sistema. Até logo!\n")
            break
        except Exception as e:  # rede de segurança: nunca quebrar o sistema
            erro(f"Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    main()
