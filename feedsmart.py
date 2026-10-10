import json
import os
from datetime import datetime

ARQ_USUARIOS = "usuarios.json"
ARQ_FEEDBACKS = "feedbacks.txt"
LARGURA = 60

# ----------------------------------------------------------------------
# Utilitários de interface
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


def _limpar(texto):
    """Remove quebras de linha e o separador '|' para gravar em TXT."""
    return " ".join(texto.replace("|", "/").split())

# ----------------------------------------------------------------------
# Sistema dos arquivos
# ----------------------------------------------------------------------

# Usuarios Sistema
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
        print(f"[!] '{ARQ_USUARIOS}' está corrompido. Iniciando sem usuários.")
        return []
    except OSError as e:
        print(f"  [ERRO] Não foi possível ler '{ARQ_USUARIOS}': {e}")
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
        print(f"  [ERRO] Falha ao salvar usuários: {e}")
        return False

# Feedbacks Sistema
# ----------------------------------------------------------------------

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
                    print(f"  (!) Linha {n} ignorada em '{ARQ_FEEDBACKS}': {e}")
    except OSError as e:
        (f"  [ERRO] Não foi possível ler '{ARQ_FEEDBACKS}': {e}")
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
        print(f"  [ERRO] Falha ao salvar feedbacks: {e}")
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
# Menu e Opcoes
# ----------------------------------------------------------------------
             
def cadastrar_usuario(usuarios):
    """
    Essa função serve para armazenar os usuarios que se registram no sistema

    Parâmetros: (tuple,string,int,string,string)
    Retorna:   (txt, json)
    """
    titulo("Cadastrar Usuário")
    nome = input("Nome do usuário: ")
    while True:
            try:
                idade = int(input('Idade: '))
            except ValueError:
                print("  (!) Digite um número inteiro válido.")
                continue
            else:
                break
    profissao = input("Profissão atual: ")
    tipo = input("Tipo de conta:")

    usuario = {
            "id": proximo_id(usuarios),
            "nome": nome,
            "idade": idade,
            "profissao": profissao,
            "tipo": tipo,
            }
    usuarios.append(usuario)
    if salvar_usuarios(usuarios):
        print(f"\n - Usuário '{nome}' cadastrado com ID {usuario['id']}.")


def ver_usuarios(usuarios):
    """
    Exibe os usuários cadastrados em formato de tabela.

    Args:
        usuarios (list[dict]): usuários a serem listados.
    """
    titulo("Usuários Cadastrados")
    if not usuarios:
        print("  (!) Nenhum usuário cadastrado ainda.")
        return
    print(f"  {'ID':<4}{'Nome':<22}{'Idade':<7}{'Profissão':<16}{'Tipo'}")
    print("  " + "-" * (LARGURA - 4))
    for u in usuarios:
        print(f"  {u['id']:<4}{u['nome'][:20]:<22}{u['idade']:<7}"
              f"{u['profissao'][:14]:<16}{u['tipo']}")
    print(f"\n  Total: {len(usuarios)} usuário(s)")


def registrar_feedback(usuarios, feedbacks):
    """
    Registra um feedback associado a um usuário existente.

    Args:
        usuarios (list[dict]): usuários cadastrados.
        feedbacks (list[dict]): feedbacks.
    """
    titulo("Registrar Feedback")
    if not usuarios:
        print("  (!) Cadastre ao menos um usuário antes de registrar feedbacks.")
        return

    for u in usuarios:
        print(f"    {u['id']}) {u['nome']} ({u['tipo']})")
    ids_validos = {u["id"] for u in usuarios}
    while True:
        try:
            id_usuario = int(input("\nID do usuário: "))
            if id_usuario in ids_validos:
                break
            print("  [ERRO] ID não encontrado. Escolha um dos IDs listados.")
        except ValueError:
            print("  (!) Digite uma ID válida")
            continue

    produto = input("Nome do Produto: ")
    texto = input("Comentário: ")
    while True:
            try:
                nota = int(input('Nota (0 a 10): '))
                if nota > 10 or nota < 0:
                    linha("-")
                    print("  (!) Digite um número entre 0 a 10")
                    continue
                else:
                    break
            except ValueError:
                linha("-")
                print("  (!) Digite um número inteiro válido.")
                continue
    data = datetime.now().strftime("%d/%m/%Y")

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
        print(f"\n - Feedback #{feedback['id']} registrado.")


def calcular_estatisticas(usuarios, feedbacks):
    """
    Calcula as estatísticas usadas nos relatórios.

    Args:
        usuarios (list[dict]): usuários cadastrados.
        feedbacks (list[dict]): feedbacks registrados.

    Returns:
        dict: média geral, total, médias/contagens por produto
        de usuário, e matriz produto
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

    return {
        "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total_usuarios": len(usuarios),
        "total_feedbacks": total,
        "media_geral": round(media_geral, 2),
        "por_produto": por_produto,
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
    l.append("Relatório FEEDSMART".center(LARGURA))
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
        print("  (!) Ainda não há feedbacks para analisar.")
        return
    print()
    print(montar_relatorio_texto(calcular_estatisticas(usuarios, feedbacks)))


def gerar_insights(usuarios, feedbacks):
    """
    Analisa os feedbacks, gera insights automáticos e os exibe no terminal.
 
    Regras aplicadas:
        - Produto com média abaixo de 6: precisa de melhorias.
        - Produto com média entre 6 e abaixo de 9: aceitável.
        - Produto com média >= 9: destaque de satisfações.
        - Usuário com mais de 5 feedbacks: perfil engajado.
        - Usuário com 5 ou menos feedbacks: perfil menos engajado.

    Args:
        usuarios (list[dict]): usuários cadastrados.
        feedbacks (list[dict]): feedbacks registrados.
    """
    
    insights = []
    titulo("INSIGHTS AUTOMÁTICOS")
    if not feedbacks:
        return insights
 
    notas_produto = {}
    for f in feedbacks:
        notas_produto.setdefault(f["produto"], []).append(f["nota"])
 
    for produto, notas in sorted(notas_produto.items()):
        media = sum(notas) / len(notas)
        if media < 6:
            insights.append((f"(!) O Produto '{produto}' tem média abaixo de 6 ({media:.1f}) — precisa de melhorias."))
        elif media >= 6 and media < 9:
            insights.append((f"(*) O Produto '{produto}' tem média {media:.1f} — aceitável."))
        elif media >= 9:
            insights.append((f"(+) O Produto '{produto}' tem média {media:.1f} — destaque de satisfações."))
 
    nomes = {u["id"]: u["nome"] for u in usuarios}
    contagem = {}
    for f in feedbacks:
        contagem[f["id_usuario"]] = contagem.get(f["id_usuario"], 0) + 1
 
    for id_usuario, qtd in sorted(contagem.items()):
        if qtd > 5:
            nome = nomes.get(id_usuario, f"Usuário #{id_usuario}")
            insights.append((f"(i) Usuário '{nome}' enviou mais de 5 feedbacks ({qtd}) — perfil engajado."))
        else:
            nome = nomes.get(id_usuario, f"Usuário #{id_usuario}")
            insights.append((f"(i) Usuário '{nome}' enviou 5 ou menos feedbacks ({qtd}) — perfil menos engajado."))

    if not insights:
        insights.append(("info",
            "Nenhum ponto de atenção ou destaque identificado com os dados atuais."))

    for  mensagem in insights:
        print(f" {mensagem}")

    
def menu():
    """Imprime as opções do menu principal e carrega os dados de acordo com a opção escolhida."""
    usuarios = carregar_usuarios()
    feedbacks = carregar_feedbacks()
    opcao = 0
    while True:
        titulo("FEEDSMART - GESTÃO DE FEEDBACKS")
        print("1 - Cadastrar usuário\n2 - Ver usuários\n3 - Registrar feedback\n4 - Relatório geral\n5 - Insights automáticos\n0 - Sair")
        linha("-")
        try:
            opcao = int(input("Escolha uma opção: ").strip())
        except ValueError:
            print("  [ERRO] Opção inválida. Digite um número do menu.")
        else:
            match opcao:
                case 1: 
                    cadastrar_usuario(usuarios)
                case 2: 
                    ver_usuarios(usuarios)
                case 3: 
                    registrar_feedback(usuarios, feedbacks)
                case 4: 
                    mostrar_relatorio(usuarios, feedbacks)
                case 5: 
                    gerar_insights(usuarios, feedbacks)
                case 0: 
                    linha("-")
                    print("\nSistema Encerrado. Até mais!\n")
                    break
                case _: 
                    print('  (!) Opção inválida. Digite um número do menu.')
                    continue
            input("\n  Pressione ENTER para voltar ao menu...")
                

if __name__ == "__main__":
    menu()