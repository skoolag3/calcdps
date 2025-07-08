elementos = ["Fire", "Water", "Nature", "Light", "Dark", "Neutral", "Omni", "Perfect Seal"]

def bonusElem(unitElem, iniElem):
    vantagem = {
        "Fire": "Nature",
        "Water": "Fire",
        "Nature": "Water",
        "Dark": "Light",
        "Light": "Dark"
    }
    if unitElem == "Omni":
        return 1.5
    if unitElem == "Perfect Seal":
        return 3.0
    if unitElem == "Neutral":
        return 1.0
    if unitElem in vantagem:
        if vantagem[unitElem] == iniElem:
            return 3.0
        elif vantagem.get(iniElem) == unitElem:
            return 0.33
    return 1.0
