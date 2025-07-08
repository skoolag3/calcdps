import streamlit as st
from modules.tecnicas import tecnicas
from modules.enchant import enchants
from modules.skill import skillTrees
from modules.dot import dots
from modules.elementos import elementos, bonusElem

def formValor(valor):
    if valor >= 1e12:
        return f"{valor/1e12:.2f}T"
    elif valor >= 1e9:
        return f"{valor/1e9:.2f}B"
    elif valor >= 1e6:
        return f"{valor/1e6:.2f}M"
    elif valor >= 1e3:
        return f"{valor/1e3:.2f}K"
    else:
        return f"{valor:.2f}"

def formatar_tempo(segundos):
    dias = int(segundos // 86400)
    segundos %= 86400
    horas = int(segundos // 3600)
    segundos %= 3600
    minutos = int(segundos // 60)
    segundos %= 60
    return f"{dias}d {horas}h {minutos}m {segundos:.2f}s"

st.title("Calculadora")

with st.expander("Informações Básicas da Unit", expanded=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        baseDmgValor = st.number_input("Dano Base", min_value=0.0, value=0.0)
    with col2:
        sufixo = st.selectbox("Unidade", ["", "K", "M", "B"])
    mult = {"": 1, "K": 1e3, "M": 1e6, "B": 1e9}
    baseDmg = baseDmgValor * mult[sufixo]

    baseSpa = st.number_input("SPA Base (s)", value=1.0, min_value=0.1)
    baseRange = st.number_input("Range Base", value=10.0, min_value=1.0)

    baseCritChance = st.number_input("Crit Chance Base (%)", value=0.0, min_value=0.0) / 100
    baseCritDmg = st.number_input("Crit Damage Base (%)", value=50.0, min_value=0.0) / 100

    tipoAtaque = st.selectbox("Tipo de Ataque", ["AoE (Line)", "AoE (Full)", "AoE (Cone)", "AoE (Circle)"])

    alvosTipo = {
        "AoE (Line)": 4,
        "AoE (Full)": 10,
        "AoE (Cone)": 6,
        "AoE (Circle)": 8
    }
    numAlvos = st.number_input("Quantidade de inimigos atingidos por ataque", min_value=1, value=alvosTipo.get(tipoAtaque, 1))

with st.expander("Técnica", expanded=True):
    st.markdown("### Escolha a Técnica")

    if "tecnica" not in st.session_state:
        st.session_state["tecnica"] = "Nenhuma"

    cols = st.columns(len(tecnicas))
    for i, (nome, data) in enumerate(tecnicas.items()):
        with cols[i]:
            if data.get("img"):
                st.image(data["img"], width=96)
            if st.button(nome, key=f"btn_{nome}"):
                st.session_state["tecnica"] = nome

    tecnica = st.session_state["tecnica"]
    st.markdown(f"**Selecionado:** `{tecnica}`")

with st.expander("Skill Tree"):
    skt = st.selectbox("Skill Tree", list(skillTrees.keys()))

with st.expander("Enchant"):
    enchant = st.selectbox("Enchant", list(enchants.keys()))

with st.expander("Elementos"):
    col1, col2 = st.columns(2)
    with col1:
        unitElem = st.selectbox("Elemento da Unit", elementos)
    with col2:
        iniElem = st.selectbox("Elemento do Inimigo", elementos[:-2])

with st.expander("DOT/Efeitos", expanded=False):
    qtdDots = st.number_input("Quantidade de DOTs", min_value=0, max_value=3, value=1, step=1)
    selectDot = []
    for i in range(qtdDots):
        st.markdown(f"### DOT {i+1}")
        dot = st.selectbox(f"Efeito {i+1}", list(dots.keys()), key=f"dot_{i}")
        if dot != "None":
            dotInfo = dots[dot]
            st.info(f"**{dot}**: {dotInfo['desc']}")
            dmgBaseDot = st.number_input(f"Dano base para {dot}", min_value=0.0, value=0.0, key=f"dmgBaseDot_dot_{i}")
            selectDot.append({
                "nome": dot,
                "dmgBaseDot": dmgBaseDot,
                "mult": dotInfo["mult"],
                "ticks": dotInfo["ticks"],
                "duracao": dotInfo["duracao"]
            })

t = tecnicas[tecnica]
e = enchants[enchant]
s = skillTrees[skt]

critChance = baseCritChance + t["critChance"] + e["critChance"] + s["critChance"]
critDmgTotal = baseCritDmg + t["critDmg"] + e["critDmg"] + s["critDmg"]

rangeFinal = baseRange * t["alcance"] * s["alcance"]
spaFinal = baseSpa * t["spa"] * e["spa"] * s["spa"]

multDano = t["dano"] * e["dano"] * s["dano"]

# DOT

dmgDotTotal = 0
dotDesc = []
for dotBook in selectDot:
    dmgDot = dotBook["dmgBaseDot"] * dotBook["mult"] * dotBook["ticks"] * multDano
    dmgDotTotal += dmgDot
    dpsDot = dmgDot / dotBook["duracao"] if dotBook["duracao"] > 0 else 0
    dotDesc.append(
        f"**{dotBook['nome']}** - Dano total: {formValor(dmgDot)}, DPS: {formValor(dpsDot)}, Duração: {dotBook['duracao']}s, Ticks: {dotBook['ticks']}"
    )


danoTotal = baseDmg * multDano + dmgDotTotal
danoCritico = danoTotal * (1 + critDmgTotal)

bonusElemental = bonusElem(unitElem, iniElem)
danoElemFinal = danoTotal * bonusElemental

DPS_Normal = danoTotal / spaFinal
DPS_Crit = danoCritico / spaFinal
DPS_Medio = DPS_Normal * (1 - critChance) + DPS_Crit * critChance

DanoPorHit = danoTotal * (1 - critChance) + danoCritico * critChance
DanoTotalHitAoE = DanoPorHit * numAlvos

#st.markdown("---")
#with st.expander("Simulador de Combate (Tempo para Matar Inimigo)"):
#    vidaEnemy = st.number_input("Vida do inimigo (ex: 1T = 1e12)", min_value=0.0, value=0.0)
#    timeKill = vidaEnemy / DPS_Medio if DPS_Medio > 0 else 0
#    timeFormat = formatar_tempo(timeKill)
#    st.metric("Tempo estimado para matar:", timeFormat)

aumentoDeCrit = (critDmgTotal - baseCritDmg) * 100

st.markdown("## Resultados")
col1, col2, col3 = st.columns(3)
col1.metric(" Dano Final", formValor(danoTotal))
col2.metric(" Elemental Dano", formValor(danoElemFinal))
col3.metric(" SPA Final", f"{spaFinal:.2f}s")

col4, col5, col6 = st.columns(3)
col4.metric(" Alcance", f"{rangeFinal:.2f}m")
col5.metric(" Crit Chance", f"{critChance * 100:.1f}%")
col6.metric(" Dano Crítico", formValor(danoCritico))

col7, col8, col9 = st.columns(3)
col7.metric(" Aumento Crit Damage (%)", f"{aumentoDeCrit:.1f}%")
col8.metric(" Crit Damage Total (%)", f"{critDmgTotal*100:.1f}%")
col9.metric(" Multiplicador Crítico", f"x{1 + critDmgTotal:.3f}")

if dotDesc:
    st.markdown("### Informações DOT / Efeitos")
    for msg in dotDesc:
        st.markdown(msg)

st.markdown("### Hit Total por ataque em área")
st.markdown(f" Dano médio por inimigo: `{formValor(DanoPorHit)}`")
st.markdown(f" Dano total em {numAlvos} inimigos (com chance distribuída): `{formValor(DanoTotalHitAoE)}`")
st.markdown(f" Tipo de Ataque: `{tipoAtaque}`")

st.markdown("### DPS")
col1, col2, col3 = st.columns(3)
col1.metric(" DPS Médio", formValor(DPS_Medio))
col2.metric(" DPS Normal", formValor(DPS_Normal))
col3.metric(" DPS Crítico", formValor(DPS_Crit))

