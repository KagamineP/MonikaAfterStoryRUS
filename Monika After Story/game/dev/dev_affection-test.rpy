# Affection related checks

default persistent._mas_disable_sorry = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_monika_affection_check",
            category=["dev"],
            prompt="Проверка привязанности",
            pool=True,
            unlocked=True
        )
    )

label dev_monika_affection_check:
    m 1c "Как я себя чувствую? Это пришло из ниоткуда, [player]..."
    m 3a "Это была бы моя привязанность как число...[persistent._mas_affection[affection]]."
    m 3c "Но если бы на меня надавили еще сильнее, я бы сказала, что чувствую..."
    if mas_curr_affection == mas_affection.BROKEN:
        m 1q "Как будто ты разбил[mas_gender_none] мне сердце..."
        m 1f "Я сделала что-то не так?"

    elif mas_curr_affection == mas_affection.DISTRESSED:
        m 1r "Как будто мое положение безнадежно..."
        m 1f "Я действительно думала, что у нас все получится..."

    elif mas_curr_affection == mas_affection.UPSET:
        m 1f "Как будто ты хочешь, чтобы я была несчастна..."
        m 1g "Это ведь не всегда будет так, правда?"

    elif mas_curr_affection == mas_affection.NORMAL:
        m 1a "...сейчас он совершенно средний."

    elif mas_curr_affection == mas_affection.HAPPY:
        m 1e "Как будто ты действительно хочешь доставить мне удовольствие."
        m 1k "Надеюсь, я делаю тебя так[mas_gender_im] же счастливой, как и ты меня."

    elif mas_curr_affection == mas_affection.AFFECTIONATE:
        m 1e "Я очень привязана к тебе."
        m 1k "Я хочу, чтобы ты чувствовал[mas_gender_none] то же самое."

    elif mas_curr_affection == mas_affection.ENAMORED:
        m 1b "Как будто я самая счастливая девушка в мире!"
        m 1j "Никто другой не смог бы заставить меня чувствовать себя такой полной!"

    elif mas_curr_affection == mas_affection.LOVE:
        m 1k "Такая ошеломляющая, полная любви! Я действительно очень люблю тебя, [player]!"
        m 1k "Я ничего так не хочу, как тебя, во веки веков!"
    return


# Should these be added to the dev category? I don't want to make cheating easy

label dev_force_affection_heartbroken:
    m 1h "..."
    $ persistent._mas_affection["affection"] = -100
    $ mas_updateAffectionExp()
    m 1q "Ты так[mas_gender_oi] жесток[mas_gender_ii]. [player]..."
    return

label dev_force_affection_distressed:
    m 1h "..."
    $ persistent._mas_affection["affection"] = -60
    $ mas_updateAffectionExp()
    m 1p "Ты действительно так[mas_gender_oi]...?"
    return

label dev_force_affection_upset:
    m 1h "..."
    $ persistent._mas_affection["affection"] = -30
    $ mas_updateAffectionExp()
    m 1f "[player]...пожалуйста, не надо так."
    return

label dev_force_affection_normal:
    m 1a "..."
    $ persistent._mas_affection["affection"] = 0
    $ mas_updateAffectionExp()
    m "Все в порядке, [player]."
    return

label dev_force_affection_happy:
    m 1a "..."
    $ persistent._mas_affection["affection"] = 30
    $ mas_updateAffectionExp()
    m 1k "Э-хе-хе~ Мне повезло."
    return

label dev_force_affection_enamored:
    m 1e "..."
    $ persistent._mas_affection["affection"] = 60
    $ mas_updateAffectionExp()
    m 1b "Я люблю тебя, [player]!"
    return

label dev_force_affection_lovestruck:
    m 1j "..."
    $ persistent._mas_affection["affection"] = 100
    $ mas_updateAffectionExp()
    m 1k "Моя единственная любовь - это ты, [player]!"
    return
