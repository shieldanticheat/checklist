
# -*- coding: utf-8 -*-
import json
import os
from datetime import date
from xml.sax.saxutils import escape

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage
)


# =========================================================
# IDENTIDADE VISUAL — HOSPITAL SÃO CAMILO / CURA D'ARS
# =========================================================

VERMELHO = (0.70, 0.05, 0.13, 1)
VERMELHO_ESCURO = (0.48, 0.03, 0.08, 1)
FUNDO = (0.95, 0.96, 0.97, 1)
BRANCO = (1, 1, 1, 1)
TEXTO = (0.15, 0.18, 0.22, 1)
CINZA = (0.38, 0.41, 0.45, 1)
VERDE = (0.10, 0.40, 0.27, 1)


# =========================================================
# ARQUIVOS DO APLICATIVO
# =========================================================

PASTA = os.path.dirname(os.path.abspath(__file__))

ARQUIVO_DADOS = os.path.join(
    PASTA,
    "registros_checklist.json"
)

ARQUIVO_LOGO = os.path.join(
    PASTA,
    "logo_sao_camilo.png"
)


# =========================================================
# COMPONENTES VISUAIS
# =========================================================

class BotaoInstitucional(Button):

    def __init__(self, **kwargs):
        texto = str(kwargs.get("text", "")).upper()

        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_disabled_normal", "")
        kwargs.setdefault("background_color", VERMELHO)
        kwargs.setdefault("color", BRANCO)
        kwargs.setdefault("bold", True)
        kwargs.setdefault("font_size", "14sp")

        if "VOLTAR" in texto or "CANCELAR" in texto:
            kwargs["background_color"] = CINZA

        elif (
            "PDF" in texto
            or "SALVAR" in texto
            or texto == "OK"
        ):
            kwargs["background_color"] = VERMELHO_ESCURO

        elif (
            "CONCLUÍDO" in texto
            or "REALIZADA" in texto
        ):
            kwargs["background_color"] = VERDE

        super().__init__(**kwargs)


class TextoInstitucional(Label):

    def __init__(self, **kwargs):
        kwargs.setdefault("color", TEXTO)
        kwargs.setdefault("font_size", "14sp")
        super().__init__(**kwargs)


# =========================================================
# AMBIENTES DO 5º ANDAR E DO MEZANINO (-1)
# =========================================================

AMBIENTES = [
    "Tecnologia e Informação - TIC",
    "Comercial e Contas Particulares",
    "SCIH",
    "Gestão de Leitos",
    "Qualidade",
    "Gerência de Contas Médicas",
    "Direção Médica",
    "Gestão de Contratos (Serviços Terceiros)",
    "Cadastro",
    "Direção Assistencial",
    "Diretoria Administrativa",
    "Diretoria Operacional",
    "Sala de Reuniões - Ébano",
    "Copa",
    "Banheiro Feminino",

    # Mezanino (-1)
    "Mezanino (-1) - Sala da Gerência da Contabilidade",
    "Mezanino (-1) - Sala do Setor de Compras",
    "Mezanino (-1) - Sala do Setor SIGE",
    "Mezanino (-1) - Sala do Gerente Financeiro",
    "Mezanino (-1) - Salão de Computadores",
    "Mezanino (-1) - Copa",
    "Mezanino (-1) - Toalete Unissex",
    "Mezanino (-1) - Toalete Masculino",
    "Mezanino (-1) - Toalete Feminino",
]


# =========================================================
# BANHEIROS INTERNOS
# =========================================================

TOALETES = {
    "Tecnologia e Informação - TIC":
        "Toalete interno da TIC",

    "Direção Assistencial":
        "Toalete interno da Direção Assistencial",

    "Diretoria Administrativa":
        "Toalete interno da Diretoria Administrativa",

    "Diretoria Operacional":
        "Toalete interno da Diretoria Operacional",

    "Copa":
        "Banheiro Masculino principal (na copa)",
}


TOALETES_MEZANINO = {
    "Mezanino (-1) - Toalete Unissex",
    "Mezanino (-1) - Toalete Masculino",
    "Mezanino (-1) - Toalete Feminino",
}


SITUACOES_AMBIENTE = [
    "Pendente",
    "Concluído",
    "Retornar mais tarde",
    "Acesso indisponível",
]


SITUACOES_TAREFA = [
    "Pendente",
    "Concluído",
    "Não aplicável hoje",
]


# =========================================================
# TAREFAS DE CADA AMBIENTE
# =========================================================

def tarefas_ambiente(ambiente):

    if ambiente == "Copa":
        tarefas = [
            ("Limpar mesas e bancadas", "diaria"),
            ("Limpar pia e torneira", "diaria"),
            ("Recolher o lixo da copa", "diaria"),
            ("Organizar a copa", "diaria"),
            ("Limpar a geladeira", "segunda"),
            ("Aspirar o carpete da copa", "sexta"),
        ]

    elif ambiente == "Mezanino (-1) - Copa":
        tarefas = [
            ("Limpar mesas e bancadas", "diaria"),
            ("Limpar pia e torneira", "diaria"),
            ("Limpar a parte externa da geladeira", "diaria"),
            ("Limpar o interior da geladeira", "segunda"),
            ("Limpar o micro-ondas", "diaria"),
            ("Recolher o lixo da copa", "diaria"),
            ("Organizar a copa", "diaria"),
            ("Passar mop seco no piso", "diaria"),
            ("Passar mop úmido no piso", "diaria"),
        ]

    elif ambiente == "Banheiro Feminino":
        tarefas = [
            ("Lavar o piso", "diaria"),
            ("Higienizar vaso sanitário", "diaria"),
            ("Higienizar pia e torneiras", "diaria"),
            ("Limpar espelho", "diaria"),
            ("Repor materiais, se necessário", "diaria"),
            ("Recolher o lixo", "diaria"),
        ]

    elif ambiente in TOALETES_MEZANINO:
        tarefas = [
            ("Lavar o piso", "diaria"),
            ("Higienizar vaso sanitário", "diaria"),
            ("Higienizar pia e torneiras", "diaria"),
            ("Limpar espelho", "diaria"),
            ("Repor materiais, se necessário", "diaria"),
            ("Recolher o lixo", "diaria"),
        ]

    elif ambiente.startswith("Mezanino (-1) - "):
        tarefas = [
            ("Limpar superfícies acessíveis", "diaria"),
            ("Limpar mesas de trabalho", "diaria"),
            (
                "Limpar externamente os computadores, "
                "quando permitido",
                "diaria"
            ),
            ("Recolher o lixo", "diaria"),
            ("Organizar o ambiente", "diaria"),
            ("Passar mop seco no piso", "diaria"),
            ("Passar mop úmido no piso", "diaria"),
        ]

    else:
        tarefas = [
            ("Limpar superfícies acessíveis", "diaria"),
            ("Recolher o lixo", "diaria"),
            ("Organizar o ambiente", "diaria"),
            ("Aspirar o carpete", "sexta"),
        ]

    if ambiente in TOALETES:
        nome = TOALETES[ambiente]

        tarefas.extend([
            (nome + " - lavar o piso", "diaria"),
            (nome + " - higienizar vaso sanitário", "diaria"),
            (nome + " - higienizar pia e torneiras", "diaria"),
            (nome + " - limpar espelho", "diaria"),
            (nome + " - repor materiais, se necessário", "diaria"),
            (nome + " - recolher o lixo", "diaria"),
        ])

    return tarefas


def valor_inicial(frequencia):
    hoje = date.today()

    if frequencia == "segunda" and hoje.weekday() != 0:
        return "Não aplicável hoje"

    if frequencia == "sexta" and hoje.weekday() != 4:
        return "Não aplicável hoje"

    return "Pendente"


# =========================================================
# SALVAMENTO E CARREGAMENTO DOS REGISTROS
# =========================================================

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return {}

    try:
        with open(
            ARQUIVO_DADOS,
            "r",
            encoding="utf-8-sig"
        ) as arquivo:
            dados = json.load(arquivo)

        return dados if isinstance(dados, dict) else {}

    except (OSError, json.JSONDecodeError):
        return {}


def salvar_json(dados):
    temporario = ARQUIVO_DADOS + ".tmp"

    with open(
        temporario,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=2
        )

    os.replace(temporario, ARQUIVO_DADOS)


# =========================================================
# FONTES DO PDF
# =========================================================

def fontes_pdf():
    normal = r"C:\Windows\Fonts\arial.ttf"
    negrito = r"C:\Windows\Fonts\arialbd.ttf"

    try:
        if os.path.isfile(normal):

            if (
                "ArialLimpeza"
                not in pdfmetrics.getRegisteredFontNames()
            ):
                pdfmetrics.registerFont(
                    TTFont("ArialLimpeza", normal)
                )

            if os.path.isfile(negrito):

                if (
                    "ArialLimpezaBold"
                    not in pdfmetrics.getRegisteredFontNames()
                ):
                    pdfmetrics.registerFont(
                        TTFont("ArialLimpezaBold", negrito)
                    )

                return "ArialLimpeza", "ArialLimpezaBold"

            return "ArialLimpeza", "ArialLimpeza"

    except Exception:
        pass

    return "Helvetica", "Helvetica-Bold"


# =========================================================
# APLICATIVO
# =========================================================

class ChecklistLimpezaApp(App):

    def build(self):
        self.title = "Checklist de Limpeza - São Camilo | Ébano"

        Window.size = (460, 780)
        Window.clearcolor = FUNDO

        self.dados = carregar_dados()
        self.data_hoje = date.today().isoformat()

        self.dados.setdefault(self.data_hoje, {})
        self.dados.setdefault("limpeza_terminal", {})

        registros = self.dados[self.data_hoje]

        for ambiente in AMBIENTES:
            reg = registros.setdefault(
                ambiente,
                {
                    "situacao": "Pendente",
                    "tarefas": {}
                }
            )

            reg.setdefault("situacao", "Pendente")
            reg.setdefault("tarefas", {})

            for tarefa, frequencia in tarefas_ambiente(ambiente):
                reg["tarefas"].setdefault(
                    tarefa,
                    valor_inicial(frequencia)
                )

        salvar_json(self.dados)

        self.raiz = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8)
        )

        with self.raiz.canvas.before:
            Color(*FUNDO)
            self._fundo_raiz = Rectangle(
                pos=self.raiz.pos,
                size=self.raiz.size
            )

        self.raiz.bind(
            pos=lambda obj, valor:
                setattr(self._fundo_raiz, "pos", valor),
            size=lambda obj, valor:
                setattr(self._fundo_raiz, "size", valor)
        )

        self.mostrar_lista()

        return self.raiz

    def aviso(self, titulo, mensagem):
        caixa = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        texto = TextoInstitucional(
            text=mensagem,
            halign="center",
            valign="middle"
        )

        texto.bind(
            size=lambda obj, tamanho:
                setattr(obj, "text_size", tamanho)
        )

        caixa.add_widget(texto)

        botao = BotaoInstitucional(
            text="OK",
            size_hint_y=None,
            height=dp(44)
        )

        popup = Popup(
            title=titulo,
            content=caixa,
            size_hint=(0.88, 0.38)
        )

        botao.bind(on_release=popup.dismiss)
        caixa.add_widget(botao)
        popup.open()

    def salvar(self):
        salvar_json(self.dados)

    # =====================================================
    # LISTA PRINCIPAL — COM LOGO
    # =====================================================

    def mostrar_lista(self, *_):
        self.raiz.clear_widgets()

        # A logo é opcional: o aplicativo funciona sem ela.
        if os.path.isfile(ARQUIVO_LOGO):
            try:
                logo = Image(
                    source=ARQUIVO_LOGO,
                    size_hint=(1, None),
                    height=dp(140),
                    fit_mode="contain"
                )
                self.raiz.add_widget(logo)

            except Exception as erro:
                print("Não foi possível carregar a logo:", erro)

        titulo = TextoInstitucional(
            text=(
                "HOSPITAL SÃO CAMILO — CURA D’ARS\n"
                "CHECKLIST DE LIMPEZA\n"
                "5º ANDAR E MEZANINO (-1)"
            ),
            font_size="17sp",
            bold=True,
            color=VERMELHO,
            size_hint_y=None,
            height=dp(88),
            halign="center",
            valign="middle"
        )

        self.raiz.add_widget(titulo)

        self.raiz.add_widget(TextoInstitucional(
            text="Data: " + date.today().strftime("%d/%m/%Y"),
            size_hint_y=None,
            height=dp(28)
        ))

        scroll = ScrollView()

        lista = BoxLayout(
            orientation="vertical",
            spacing=dp(7),
            size_hint_y=None
        )

        lista.bind(minimum_height=lista.setter("height"))

        registros = self.dados[self.data_hoje]

        for ambiente in AMBIENTES:
            reg = registros[ambiente]
            situacao = reg.get("situacao", "Pendente")

            botao = BotaoInstitucional(
                text=ambiente + "\nSituação: " + situacao,
                size_hint_y=None,
                height=dp(62)
            )

            botao.bind(
                on_release=lambda instancia, nome=ambiente:
                    self.mostrar_ambiente(nome)
            )

            lista.add_widget(botao)

        scroll.add_widget(lista)
        self.raiz.add_widget(scroll)

        terminal = BotaoInstitucional(
            text="REGISTRAR LIMPEZA TERMINAL",
            size_hint_y=None,
            height=dp(48)
        )

        terminal.bind(on_release=self.mostrar_terminal)
        self.raiz.add_widget(terminal)

        pdf = BotaoInstitucional(
            text="GERAR RELATÓRIO PDF DO DIA",
            size_hint_y=None,
            height=dp(52),
            bold=True
        )

        pdf.bind(on_release=self.gerar_pdf)
        self.raiz.add_widget(pdf)

    # =====================================================
    # DETALHES DO AMBIENTE
    # =====================================================

    def mostrar_ambiente(self, ambiente):
        self.raiz.clear_widgets()

        reg = self.dados[self.data_hoje][ambiente]

        self.raiz.add_widget(TextoInstitucional(
            text=ambiente,
            font_size="19sp",
            bold=True,
            size_hint_y=None,
            height=dp(58),
            halign="center",
            valign="middle"
        ))

        self.raiz.add_widget(TextoInstitucional(
            text="Situação do ambiente",
            size_hint_y=None,
            height=dp(28)
        ))

        situacao = Spinner(
            text=reg.get("situacao", "Pendente"),
            values=SITUACOES_AMBIENTE,
            size_hint_y=None,
            height=dp(44)
        )

        situacao.bind(
            text=lambda sp, valor:
                self.alterar_situacao(ambiente, valor)
        )

        self.raiz.add_widget(situacao)

        scroll = ScrollView()

        lista = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None
        )

        lista.bind(minimum_height=lista.setter("height"))

        lista.add_widget(TextoInstitucional(
            text="Tarefas diárias e semanais",
            bold=True,
            size_hint_y=None,
            height=dp(32)
        ))

        for tarefa, frequencia in tarefas_ambiente(ambiente):
            linha = BoxLayout(
                orientation="vertical",
                spacing=dp(2),
                size_hint_y=None,
                height=dp(76)
            )

            label = TextoInstitucional(
                text=tarefa,
                size_hint_y=None,
                height=dp(34),
                halign="left",
                valign="middle"
            )

            label.bind(
                size=lambda obj, tamanho:
                    setattr(obj, "text_size", tamanho)
            )

            linha.add_widget(label)

            atual = reg["tarefas"].get(
                tarefa,
                valor_inicial(frequencia)
            )

            spinner = Spinner(
                text=atual,
                values=SITUACOES_TAREFA,
                size_hint_y=None,
                height=dp(40)
            )

            spinner.bind(
                text=lambda sp, valor, a=ambiente, t=tarefa:
                    self.alterar_tarefa(a, t, valor)
            )

            linha.add_widget(spinner)
            lista.add_widget(linha)

        scroll.add_widget(lista)
        self.raiz.add_widget(scroll)

        botoes = BoxLayout(
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8)
        )

        voltar = BotaoInstitucional(text="VOLTAR")
        voltar.bind(on_release=self.mostrar_lista)
        botoes.add_widget(voltar)

        confirmar = BotaoInstitucional(text="SALVAR")
        confirmar.bind(
            on_release=lambda *_: self.confirmar_salvo()
        )
        botoes.add_widget(confirmar)

        self.raiz.add_widget(botoes)

    def alterar_situacao(self, ambiente, valor):
        self.dados[self.data_hoje][ambiente]["situacao"] = valor
        self.salvar()

    def alterar_tarefa(self, ambiente, tarefa, valor):
        self.dados[self.data_hoje][ambiente]["tarefas"][tarefa] = valor
        self.salvar()

    def confirmar_salvo(self):
        self.salvar()

        self.aviso(
            "Salvo",
            "Os registros foram salvos neste computador."
        )

    # =====================================================
    # LIMPEZA TERMINAL MENSAL
    # =====================================================

    def mostrar_terminal(self, *_):
        self.raiz.clear_widgets()

        self.raiz.add_widget(TextoInstitucional(
            text="LIMPEZA TERMINAL",
            font_size="20sp",
            bold=True,
            size_hint_y=None,
            height=dp(55)
        ))

        self.raiz.add_widget(TextoInstitucional(
            text="Referência: mensal. Registre somente quando realizar.",
            size_hint_y=None,
            height=dp(55),
            halign="center",
            valign="middle"
        ))

        mes = date.today().strftime("%Y-%m")

        terminais = self.dados.setdefault(
            "limpeza_terminal", {}
        )

        registro_mes = terminais.setdefault(mes, {})

        scroll = ScrollView()

        lista = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None
        )

        lista.bind(minimum_height=lista.setter("height"))

        for ambiente in AMBIENTES:
            item = registro_mes.setdefault(
                ambiente,
                {
                    "data_realizacao": "",
                    "situacao": "Ainda não realizada",
                    "tarefas": {
                        "Lavar paredes": "Pendente",
                        "Limpar teto conforme protocolo": "Pendente",
                        "Higienização terminal conforme protocolo": "Pendente",
                    }
                }
            )

            item.setdefault("data_realizacao", "")
            item.setdefault("situacao", "Ainda não realizada")
            item.setdefault("tarefas", {})

            item["tarefas"].setdefault(
                "Lavar paredes", "Pendente"
            )
            item["tarefas"].setdefault(
                "Limpar teto conforme protocolo", "Pendente"
            )
            item["tarefas"].setdefault(
                "Higienização terminal conforme protocolo",
                "Pendente"
            )

            botao = BotaoInstitucional(
                text=ambiente + "\n" +
                    item.get("situacao", "Ainda não realizada"),
                size_hint_y=None,
                height=dp(58)
            )

            botao.bind(
                on_release=lambda inst, nome=ambiente:
                    self.editar_terminal(nome)
            )

            lista.add_widget(botao)

        scroll.add_widget(lista)
        self.raiz.add_widget(scroll)

        voltar = BotaoInstitucional(
            text="VOLTAR À LISTA",
            size_hint_y=None,
            height=dp(48)
        )

        voltar.bind(on_release=self.mostrar_lista)
        self.raiz.add_widget(voltar)

        self.salvar()

    def editar_terminal(self, ambiente):
        mes = date.today().strftime("%Y-%m")

        item = self.dados["limpeza_terminal"][mes][ambiente]

        caixa = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        scroll = ScrollView()

        conteudo = BoxLayout(
            orientation="vertical",
            padding=dp(4),
            spacing=dp(8),
            size_hint_y=None
        )

        conteudo.bind(minimum_height=conteudo.setter("height"))

        conteudo.add_widget(TextoInstitucional(
            text=ambiente,
            size_hint_y=None,
            height=dp(36)
        ))

        situacao = Spinner(
            text=item.get("situacao", "Ainda não realizada"),
            values=[
                "Ainda não realizada",
                "Realizada",
                "Parcial",
                "Não foi possível realizar"
            ],
            size_hint_y=None,
            height=dp(42)
        )

        conteudo.add_widget(TextoInstitucional(
            text="Situação",
            size_hint_y=None,
            height=dp(25)
        ))

        conteudo.add_widget(situacao)

        hoje = date.today().strftime("%d/%m/%Y")
        data_atual = item.get("data_realizacao") or hoje

        data_input = Spinner(
            text=data_atual,
            values=[hoje],
            size_hint_y=None,
            height=dp(42)
        )

        conteudo.add_widget(TextoInstitucional(
            text="Data da execução",
            size_hint_y=None,
            height=dp(25)
        ))

        conteudo.add_widget(data_input)

        seletores = {}

        for tarefa, estado in item["tarefas"].items():
            conteudo.add_widget(TextoInstitucional(
                text=tarefa,
                size_hint_y=None,
                height=dp(32)
            ))

            sp = Spinner(
                text=estado,
                values=[
                    "Pendente",
                    "Concluído",
                    "Não aplicável"
                ],
                size_hint_y=None,
                height=dp(40)
            )

            conteudo.add_widget(sp)
            seletores[tarefa] = sp

        scroll.add_widget(conteudo)
        caixa.add_widget(scroll)

        botoes = BoxLayout(
            size_hint_y=None,
            height=dp(44),
            spacing=dp(8)
        )

        popup = Popup(
            title="Registro de limpeza terminal",
            content=caixa,
            size_hint=(0.94, 0.9)
        )

        def guardar(*_):
            item["situacao"] = situacao.text

            if situacao.text in ("Realizada", "Parcial"):
                item["data_realizacao"] = data_input.text
            else:
                item["data_realizacao"] = ""

            for tarefa, sp in seletores.items():
                item["tarefas"][tarefa] = sp.text

            self.salvar()
            popup.dismiss()
            self.mostrar_terminal()

        b_salvar = BotaoInstitucional(text="SALVAR")
        b_salvar.bind(on_release=guardar)

        b_cancelar = BotaoInstitucional(text="CANCELAR")
        b_cancelar.bind(on_release=popup.dismiss)

        botoes.add_widget(b_salvar)
        botoes.add_widget(b_cancelar)

        caixa.add_widget(botoes)
        popup.open()

    # =====================================================
    # GERAÇÃO DO RELATÓRIO PDF — COM LOGO
    # =====================================================

    def gerar_pdf(self, *_):
        try:
            self.salvar()

            caminho = os.path.join(
                PASTA,
                "Relatorio_Limpeza_" +
                date.today().strftime("%Y-%m-%d") + ".pdf"
            )

            fonte, fonte_bold = fontes_pdf()
            estilos = getSampleStyleSheet()

            estilos.add(ParagraphStyle(
                name="TituloLimpeza",
                parent=estilos["Title"],
                fontName=fonte_bold,
                fontSize=16,
                leading=20,
                alignment=TA_CENTER,
                spaceAfter=8
            ))

            estilos.add(ParagraphStyle(
                name="CabecalhoLimpeza",
                parent=estilos["Heading2"],
                fontName=fonte_bold,
                fontSize=11,
                leading=14,
                spaceBefore=9,
                spaceAfter=4
            ))

            estilos.add(ParagraphStyle(
                name="TextoLimpeza",
                parent=estilos["BodyText"],
                fontName=fonte,
                fontSize=8.5,
                leading=11
            ))

            doc = SimpleDocTemplate(
                caminho,
                pagesize=A4,
                rightMargin=1.4 * cm,
                leftMargin=1.4 * cm,
                topMargin=1.3 * cm,
                bottomMargin=1.3 * cm
            )

            # Cabeçalho: usa a logo se ela estiver disponível.
            elementos = []

            if os.path.isfile(ARQUIVO_LOGO):
                try:
                    logo_pdf = RLImage(
                        ARQUIVO_LOGO,
                        width=3.5 * cm,
                        height=1.5 * cm,
                        kind="proportional"
                    )

                    cabecalho = Table(
                        [[
                            logo_pdf,
                            Paragraph(
                                "HOSPITAL SÃO CAMILO — CURA D’ARS<br/>"
                                "RELATÓRIO DIÁRIO DE LIMPEZA",
                                estilos["TituloLimpeza"]
                            )
                        ]],
                        colWidths=[4.0 * cm, 12.3 * cm]
                    )

                    cabecalho.setStyle(TableStyle([
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (0, 0), (0, 0), "LEFT"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]))

                    elementos.append(cabecalho)

                except Exception as erro_logo:
                    print(
                        "Não foi possível inserir a logo no PDF:",
                        erro_logo
                    )

            # Se não houver logo, mantém o cabeçalho textual.
            if not elementos:
                elementos.append(
                    Paragraph(
                        "HOSPITAL SÃO CAMILO — CURA D’ARS<br/>"
                        "RELATÓRIO DIÁRIO DE LIMPEZA",
                        estilos["TituloLimpeza"]
                    )
                )

            elementos.extend([
                Paragraph(
                    "5º andar - Ébano e Mezanino (-1) | Data: " +
                    date.today().strftime("%d/%m/%Y"),
                    estilos["TextoLimpeza"]
                ),
                Spacer(1, 8)
            ])

            registros = self.dados.get(
                self.data_hoje, {}
            )

            for ambiente in AMBIENTES:
                reg = registros.get(
                    ambiente,
                    {
                        "situacao": "Pendente",
                        "tarefas": {}
                    }
                )

                elementos.append(Paragraph(
                    escape(ambiente),
                    estilos["CabecalhoLimpeza"]
                ))

                elementos.append(Paragraph(
                    "<b>Situação do ambiente:</b> " +
                    escape(reg.get("situacao", "Pendente")),
                    estilos["TextoLimpeza"]
                ))

                linhas = [["Tarefa", "Situação"]]

                for tarefa, frequencia in tarefas_ambiente(ambiente):
                    estado = reg.get("tarefas", {}).get(
                        tarefa,
                        valor_inicial(frequencia)
                    )

                    linhas.append([
                        Paragraph(
                            escape(tarefa),
                            estilos["TextoLimpeza"]
                        ),
                        Paragraph(
                            escape(estado),
                            estilos["TextoLimpeza"]
                        )
                    ])

                tabela = Table(
                    linhas,
                    colWidths=[12.2 * cm, 4.1 * cm],
                    repeatRows=1
                )

                tabela.setStyle(TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0), (-1, 0),
                        colors.HexColor("#B30D21")
                    ),
                    (
                        "FONTNAME",
                        (0, 0), (-1, 0),
                        fonte_bold
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0), (-1, 0),
                        colors.white
                    ),
                    (
                        "GRID",
                        (0, 0), (-1, -1),
                        0.4, colors.grey
                    ),
                    (
                        "VALIGN",
                        (0, 0), (-1, -1),
                        "TOP"
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0), (-1, -1), 4
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0), (-1, -1), 4
                    ),
                    (
                        "TOPPADDING",
                        (0, 0), (-1, -1), 3
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0), (-1, -1), 3
                    ),
                ]))

                elementos.extend([
                    tabela,
                    Spacer(1, 4)
                ])

            # Registros mensais da limpeza terminal
            elementos.append(Spacer(1, 12))

            elementos.append(Paragraph(
                "LIMPEZA TERMINAL - REGISTROS DO MÊS",
                estilos["CabecalhoLimpeza"]
            ))

            mes = date.today().strftime("%Y-%m")

            terminal_mes = self.dados.get(
                "limpeza_terminal", {}
            ).get(mes, {})

            linhas_terminal = [[
                "Ambiente",
                "Situação",
                "Data realizada"
            ]]

            for ambiente in AMBIENTES:
                item = terminal_mes.get(ambiente, {})

                linhas_terminal.append([
                    Paragraph(
                        escape(ambiente),
                        estilos["TextoLimpeza"]
                    ),
                    Paragraph(
                        escape(
                            item.get(
                                "situacao",
                                "Ainda não realizada"
                            )
                        ),
                        estilos["TextoLimpeza"]
                    ),
                    Paragraph(
                        escape(
                            item.get("data_realizacao", "") or "-"
                        ),
                        estilos["TextoLimpeza"]
                    )
                ])

            tabela_terminal = Table(
                linhas_terminal,
                colWidths=[
                    8.3 * cm,
                    5.0 * cm,
                    3.0 * cm
                ],
                repeatRows=1
            )

            tabela_terminal.setStyle(TableStyle([
                (
                    "BACKGROUND",
                    (0, 0), (-1, 0),
                    colors.HexColor("#B30D21")
                ),
                (
                    "FONTNAME",
                    (0, 0), (-1, 0),
                    fonte_bold
                ),
                (
                    "TEXTCOLOR",
                    (0, 0), (-1, 0),
                    colors.white
                ),
                (
                    "GRID",
                    (0, 0), (-1, -1),
                    0.4, colors.grey
                ),
                (
                    "VALIGN",
                    (0, 0), (-1, -1),
                    "TOP"
                ),
                (
                    "FONTSIZE",
                    (0, 0), (-1, -1), 8
                ),
            ]))

            elementos.extend([
                tabela_terminal,
                Spacer(1, 16),
                Paragraph(
                    "Responsável pela limpeza: ______________________________",
                    estilos["TextoLimpeza"]
                ),
                Spacer(1, 10),
                Paragraph(
                    "Assinatura / ciência da gerência: _________________________",
                    estilos["TextoLimpeza"]
                ),
            ])

            doc.build(elementos)

            self.aviso(
                "PDF criado",
                "Relatório salvo em:\n" + caminho
            )

        except Exception as erro:
            self.aviso(
                "Erro ao criar PDF",
                str(erro)
            )


if __name__ == "__main__":
    ChecklistLimpezaApp().run()
