def getUsername(txt):
    txt = txt.strip()
    alias = getAlias(txt)
    
    # This can be used to review the renames
    if False and alias != txt:
        print("['" + alias + "','" + txt + "'],")

    return alias

def getAlias(txt):

    txt = txt.replace("@", "").strip()
    lower = txt.lower()

    if "wijit" in lower or "jason" in lower:
        return "Wijitmaker"

    if "ykkrosh" in lower or "philip" in lower:
        return "Philip"

    if "janwas" in lower or "jw" in lower or "wfg_jan" in lower: #TODO
        return "janwas"

    if "feneu" in lower or "erik" in lower:
        return "feneur"

    if "gee" == lower:
        return "Gee"

    if "acume" in lower:
        return "Acumen"

    if "matt" in lower:
        return "Matt"

    if "matei" in lower:
        return "matei"

    if "prefect" in lower:
        return "prefect"

    if "dax" in lower:
        return "dax"

    if "wildfirebot" in lower:
        return "WildfireBot";

    if "wildfirerobot" in lower:
        return "WildfireRobot";

    if "fire_g|" in lower or "firegiant" in lower or "fire_giant" in lower:
        return "Fire_Giant"

    if "brian" in lower:
        return "brian"

    if "dave" in lower:
        return "dave"

    if "svede" in lower:
        return "svede"

    if "cheez" in lower:
        return "CheeZy"

    if "mythos" in lower:
        return "Mythos_Ruler"

    if "seth" in lower:
        return "seth"

    if "bruno" in lower:
        return "historic_bruno"

    if "sander" in lower:
        return "sanderd17"

    if "josh" in lower:
        return "Josh"

    if "redfox" in lower:
        return "RedFox"

    if "vladislav" in lower:
        return "Vladislav"

    if "causative" in lower:
        return "causative"

    if "bb_" in lower or "bb1" in lower:
        return "bb"

    if "leper" in lower:
        return "leper"

    if "mimo" in lower:
        return "mimo"

    if "itms" in lower:
        return "Itms"

    if "markt" in lower:
        return "MarkT"

    if "fpre" in lower or "ffff" in lower or "fraizy" in lower or lower == "fg" or lower == "fff" or lower == "ff" or txt == "superelexis":
        return "fpre"

    if "fcxsanya" in lower:
        return "fcxSanya"

    if "bushido" in lower or "bushitodo" in lower or "abnegation" in lower:
        return "fatherbushido"

    if "enrique" in lower:
        return "Enrique"

    if "yves" in lower:
        return "Yves"

    if "scythetwirler" in lower or "scytheswirler" in lower or "scythewhirler" in lower:
        return "scythetwirler"

    if "stan" in lower:
        return "Stan"

    if "fabio" in lower:
        return "fabio"

    if "wraitii" in lower:
        return "wraitii"

    if "fexor" in lower:
        return "FeXoR"

    if "smiley" in lower:
        return "smiley"

    if "elexis" in lower:
        return "elexis"

    if "cc__" in lower or "cc_laptop" in lower or lower == "cc_" or "cc_1" == lower:
        return "cc"

    if "angen" in lower and not "dvangennip" in lower:
        return "Angen"

    if "k776" in lower:
        return "k776"

    if "trompeti" in lower or "tromeptin17" in lower:
        return "trompetin17"

    if "dunedan" in lower:
        return "Dunedan"

    if "temple" in lower:
        return "temple"

    if "telaviv" not in lower and "aviv" in lower or "jeru" in lower:
        return "Jeru"

    if "niektb" in lower:
        return "niektb"

    if "imarok" in lower:
        return "Imarok"

    if "gallaecio" in lower:
        return "Gallaecio"

    if "kimball" in lower:
        return "Kimball"

    if "arthur_d" in lower:
        return "Arthur_D"

    if "grugnas" in lower:
        return "Grugnas"

    if "theshadow" in lower:
        return "theShadow"

    if "nani0" in lower:
        return "nani"

    if "kennylong" in lower or "chakakhan" in lower:
        return "KennyLong"

    if "thamlett" in lower:
        return "thamlett"

    if "alpha123" in lower:
        return "alpha123"

    if txt == "GK-Daniel" or txt == "GKDaniel" or txt == "GK_Daniel":
        return "alpha123"

    if "safa" in lower:
        return "Safa_[A_boy]"

    if "eihrul" in lower:
        return "eihrul"

    if "kali" in lower:
        return "_kali"

    if "sighvatr" in lower:
        return "Sighvatr"

    if "igor" in lower:
        return "igor"

    if "agentx" in lower:
        return "agentx"

    if "badmadblacksad" in lower:
        return "Badmadblacksad"

    if "bichtiades" in lower:
        return "Bichtiades"

    if "dalerank" in lower:
        return "Dalerank"

    if "erraunt" in lower:
        return "erraunt"

    if "evans" in lower:
        return "evans"

    if txt == "Gusse":
        return "Gussebb"

    if txt == "HenryJia":
        return "Henry_Jia_T60"

    if txt == "Jagst3r21_":
        return "Jagst3r21"

    if "infyquest" in lower:
        return "infyquest"

    if "mfmachado" in lower:
        return "mfmachado"

    if "nylki" in lower:
        return "nylki"

    if "quantumstate" in lower:
        return "quantumstate"

    if "rjs23" in lower:
        return "rjs23"

    if "santa_" in lower:
        return "santa_"

    if "spahbod" in lower:
        return "Spahbod"

    if "stwf" in lower:
        return "stwf"

    if "trajan34" in lower:
        return "trajan34"

    if "wacko" in lower:
        return "wacko"

    if "xeramon" in lower:
        return "Xeramon"

    if "zaggy" in lower:
        return "Zaggy1024"

    if "amish" in lower:
        return "amish"

    if "alex|d-guy" in lower:
        return "alex|D-Guy"

    if "cygal" in lower:
        return "cygal"

    if txt == "rada"  or txt == "radagast" or txt == "rada_":
        return "radagast"

    if "skhorn" in lower:
        return "skhorn"

    if "keenehteek" in lower:
        return "keenehteek"

    # not sure if this is the same as GK-Daniel
    if txt == "Daniel_":
        return "Daniel_"

    if txt == "prod_":
        return "prod"

    if txt == "ffm_":
        return "ffm"

    #mark____

    return txt.strip()
