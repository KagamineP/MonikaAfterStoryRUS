## dev mode eggs

#dev mode easter eggs
init 5 python:
    addEvent(
        Event(
            persistent._mas_mood_database,
            "mas_mood_mitochondria",
            prompt="Митохондрия",
            category=[store.mas_moods.TYPE_GOOD],
            unlocked=True
        ),
        eventdb=store.mas_moods.mood_db
    )

    addEvent(
        Event(
            persistent._mas_mood_database,
            "mas_mood_theroom",
            prompt="Комната",
            category=[store.mas_moods.TYPE_NEUTRAL],
            unlocked=True
        ),
        eventdb=store.mas_moods.mood_db
    )

    addEvent(
        Event(
            persistent._mas_mood_database,
            "mas_mood_horny",
            prompt="возбужденный",
            category=[store.mas_moods.TYPE_BAD],
            unlocked=True
        ),
        eventdb=store.mas_moods.mood_db
    )

label mas_mood_mitochondria:
    m "You're the powerhouse of {i}my{/i} cell..."
    return

label mas_mood_theroom:
    m "Это чушь собачья.{w} Я ее не била."
    m "I did nahhhhht"
    m "Oh hai, [player]."
    return

label mas_mood_horny:
    if persistent.playername.lower() == "monik":
        m 1k "Ahh, only for my one and only~"
    elif persistent.playername.lower() == "rune":
        m 1e "I wouldn't mind, Dragon Writer~"
    elif persistent.playername.lower() == "thepotatoguy":
        m 2r "Sorry, I have no interest in potatoes."
    elif persistent.playername.lower() == "ronin":
        m 2p "Разве ты не женат? Иди поговори со своей женой."
    elif persistent.playername.lower() == "pi":
        m 2h "Разве у тебя нет девушки? Перестань быть слабаком, или она убьет тебя."
    elif persistent.playername.lower() == "lucian.chr":
        m 2q "Никаких темных лордов, спасибо."
    elif persistent.playername.lower() == "subzero":
        m 1r "Чертовски возбужденный ребенок..."
    elif persistent.playername.lower() == "ryuse":
        m 1h "Нет, пока."
        return 'quit'
    else:
        m 3n "Извини, [player], но мы еще не так далеко зашли в наших отношениях. Может быть через год или два~"
    return

## end dev easter eggs ========================================================

