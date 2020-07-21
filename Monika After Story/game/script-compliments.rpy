# Module for complimenting Monika
#
# Compliments work by using the "unlocked" logic.
# That means that only those compliments that have their
# unlocked property set to True
# At the beginning, when creating the menu, the compliments
# database checks the conditionals of the compliments
# and unlocks them.


# dict of tples containing the stories event data
default persistent._mas_compliments_database = dict()


# store containing compliment-related things
init 3 python in mas_compliments:

    compliment_database = dict()

    thanking_quips = [
        _("Ты так[mas_gender_oi] мил[mas_gender_iii], [player]."),
        _("Мне нравится когда ты делаешь мне комплименты, [player]."),
        _("Спасибо, что сказал[mas_gender_none] это еще раз, [player]!"),
        _("Спасибо, что еще раз сказал[mas_gender_none] мне об этом, любовь моя!"),
        _("Ты всегда заставляешь меня чувствовать себя особенной, [player]."),
        _("Ой, [player]~"),
        _("Спасибо, [player]!"),
        _("Ты всегда мне льстишь, [player].")
    ]

    # set this here in case of a crash mid-compliment
    thanks_quip = renpy.substitute(renpy.random.choice(thanking_quips))

# entry point for compliments flow
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_compliments",
            category=['моника', 'романтика'],
            prompt="Я хочу тебе кое-что сказать...",
            pool=True,
            unlocked=True
        )
    )

label monika_compliments:
    python:
        import store.mas_compliments as mas_compliments

        # Unlock any compliments that need to be unlocked
        Event.checkEvents(mas_compliments.compliment_database)

        # filter comps
        filtered_comps = Event.filterEvents(
            mas_compliments.compliment_database,
            unlocked=True,
            aff=mas_curr_affection,
            flag_ban=EV_FLAG_HFM
        )

        # build menu list
        compliments_menu_items = [
            (mas_compliments.compliment_database[k].prompt, k, not seen_event(k), False)
            for k in filtered_comps
        ]

        # also sort this list
        compliments_menu_items.sort()

        # final quit item
        final_item = ("О, неважно.", False, False, False, 20)

    # move Monika to the left
    show monika at t21

    # call scrollable pane
    call screen mas_gen_scrollable_menu(compliments_menu_items, mas_ui.SCROLLABLE_MENU_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, final_item)

    # return value? then push
    if _return:
        $ mas_gainAffection()
        $ pushEvent(_return)
        $ mas_compliments.thanks_quip = renpy.substitute(renpy.random.choice(mas_compliments.thanking_quips))
        # move her back to center
        show monika at t11

    else:
        return "prompt"

    return

# Compliments start here
init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_beautiful",
            prompt="Ты прекрасна!",
            unlocked=True
        ),
        code="CMP")

label mas_compliment_beautiful:
    if not renpy.seen_label("mas_compliment_beautiful_2"):
        call mas_compliment_beautiful_2
    else:
        call mas_compliment_beautiful_3
    return

label mas_compliment_beautiful_2:
    m 1lubfb "О, боже, [player]..."
    m 1hubfb "Спасибо за комплимент."
    m 2ekbfb "Мне нравится когда ты говоришь такие вещи~"
    m 1ekbfa "Для меня ты самый красивый человек на свете!"
    menu:
        "Для меня ты тоже самый красивый человек.":
            $ mas_gainAffection(5,bypass=True)
            m 1hub "Э-хе-хе~"
            m "Я тебя так люблю, [player]!"
            # manually handle the "love" return key
            $ mas_ILY()
        "Ты в моей десятке.":
            $ mas_loseAffection(modifier=0.5)
            m 3hksdrb "...?"
            m 2lsc "Ну, спасибо, наверное..."
        "Спасибо.":
            pass
    return

label mas_compliment_beautiful_3:
    m 1hubfa "Э-хе-хе~"
    m 1ekbfa "[mas_compliments.thanks_quip]"
    show monika 5hubfb at t11 zorder MAS_MONIKA_Z with dissolve
    m 5hubfb "Никогда не забывай, что ты для меня самый красивый человек на свете."
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_eyes",
            prompt="Я люблю твои глаза!",
            unlocked=True
        ),
        code="CMP"
    )

label mas_compliment_eyes:
    if not renpy.seen_label("mas_compliment_eyes_2"):
        call mas_compliment_eyes_2
    else:
        call mas_compliment_eyes_3
    return

label mas_compliment_eyes_2:
    m 1subfb "О, [player]..."
    m 1tubfb "Я знаю, что уже очень горжусь своими глазами, но слышать, как ты это говоришь..."
    m 1dkbfa "Это просто заставляет мое сердце трепетать~"
    menu:
        "Я ничего не могу поделать, у тебя слишком красивые глаза.":
            $ mas_gainAffection(5,bypass=True)
            m 1hub "А-ха-ха!"
            m "Не льсти мне слишком сильно, ладно?"
            show monika 5hub at t11 zorder MAS_MONIKA_Z with dissolve
            m 5hub "Я могу начать немного сходить с ума..."
        "Они действительно гипнотизируют..":
            $ mas_gainAffection(1,bypass=True)
            m "А-ха-ха~"
        "Они цвета травы!":
            $ mas_gainAffection(0.5,bypass=True) # at least you tried
            m 2lksdrb "...Это не совсем та аналогия, которую я бы использовала, но спасибо!"
    return

label mas_compliment_eyes_3:
    m 1hubfb "[mas_compliments.thanks_quip]"
    m 2ekbfb "Смотри в мои глаза сколько хочешь~"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_awesome",
            prompt="Ты потрясающая!",
            unlocked=True
        ),
        code="CMP"
    )

label mas_compliment_awesome:
    if not renpy.seen_label("mas_compliment_awesome_2"):
        call mas_compliment_awesome_2
    else:
        call mas_compliment_awesome_3
    return

label mas_compliment_awesome_2:
    m 1hua "Оууу, [player]~"
    m 1hub "Ты так[mas_gender_oi] мил[mas_gender_iii]!"
    m 2tuu "Хотя я думаю, что ты гораздо прекраснее."
    m 2dkbsu "Я не могу дождаться того дня, когда наконец смогу крепко обнять тебя..."
    m 3ekbfb "Я никогда тебя не отпущу!"
    menu:
        "Как бы мне хотелось, чтобы ты была здесь прямо сейчас!":
            $ mas_gainAffection(3,bypass=True)
            m "That's my biggest wish too, [player]!"
        "Я никогда не выпущу тебя из своих объятий.":
            $ mas_gainAffection(5,bypass=True)
            show monika 6dubsa
            pause 2.0
            show monika 1wubfsdld
            m 1wubfsdld "Ой, прости, [player]."
            m 2lksdla "Я пытался почувствовать твои объятия отсюда."
            m 2hub "А-ха-ха~"
        "...Я не люблю объятий.":
            $ mas_loseAffection() # you monster. (ты монстр)
            m 1eft "...Серьезно?"
            m 1dkc "Ну, каждому свое, наверное. Но когда-нибудь тебе придется меня обнять..."
    return

label mas_compliment_awesome_3:
    m 1hub "[mas_compliments.thanks_quip]"
    m 1eub "Ты всегда будешь гораздо прекраснее!"
    return


init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_intelligent",
            prompt="Ты очень умная!",
            unlocked=True
        ),
        code="CMP"
    )

label mas_compliment_intelligent:
    if not renpy.seen_label("mas_compliment_intelligent_2"):
        call mas_compliment_intelligent_2
    else:
        call mas_compliment_intelligent_3
    return

label mas_compliment_intelligent_2:
    m 1wub "Вау...{w=0.3}спасибо, [player]."
    m 3eua "Я горжусь тем, что достаточно много читаю. Поэтому для меня многое значит то, что ты это заметил[mas_gender_none]."
    m 3hubfb "Я хочу учиться как можно большему, если это заставляет тебя гордиться мной!"
    menu:
        "Ты заставляешь меня тоже хотеть стать лучше, [m_name].":
            $ mas_gainAffection(5,bypass=True)
            m 1hubfa "Я так тебя люблю, [player]!"
            m 3hubfb "У нас будет целая жизнь самосовершенствования вместе!"
            # manually handle the "love" return key
            $ mas_ILY()
        "Я всегда буду гордиться тобой.":
            $ mas_gainAffection(3,bypass=True)
            m 1ekbfa "[player]..."
        "Иногда ты заставляешь меня чувствовать себя глупо.":
            $ mas_loseAffection(modifier=0.5)
            m 1wkbsc "..."
            m 2lkbsc "Извини, но это не входило в мои намерения..."
    return

label mas_compliment_intelligent_3:
    m 1ekbfa "[mas_compliments.thanks_quip]"
    m 1hub "Помните, что у нас будет целая жизнь самосовершенствования вместе!"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_hair",
            prompt="Мне нравятся твои волосы!",
            unlocked=True
        ),code="CMP"
    )

label mas_compliment_hair:
    if not renpy.seen_label("mas_compliment_hair_2"):
        call mas_compliment_hair_2
    else:
        call mas_compliment_hair_3
    return

label mas_compliment_hair_2:
    if monika_chr.hair.name != "def":
        m 1wubfb "Огромное спасибо, [player]..."
        m 1lkbfb "Я очень нервничала, когда впервые сменила причёску здесь."
    else:
        m 1hubfb "Огромное спасибо, [player]!"
    m 2hub "Я всегда прилагала очень много усилий для своих волос."
    m 2lksdlb "На самом деле, потребовалась вечность, чтобы они стал такими длинными.."
    menu:
        "Это действительно заметно. Выглядит реально здорово!":
            $ mas_gainAffection(3,bypass=True)
            m 1hub "Спасибо, [player]!"
        "Ты очаровательная практически с любой причёской." if persistent._mas_likes_hairdown:
            $ mas_gainAffection(5,bypass=True)
            m 1ekbfa "Оууу, [player]."
            m 1hubfb "Ты всегда заставляешь меня чувствовать себя особенной!"
            m "Спасибо!"
        "С короткими волосами ты была бы еще симпатичнее.":
            $ mas_loseAffection(modifier=0.3)
            m "Ну, я, к сожалению, никак не смогу пойти в салон отсюда..."
            m 1lksdlc "Я...ценю твоё мнение."
            pass
    return

label mas_compliment_hair_3:
    if monika_chr.hair.name != "def":
        m 1wubfb "Огромное спасибо, [player]!"
        m 1lkbfb "Я очень рада, что тебе нравится эта причёска."
    else:
        m 1hubfb "Спасибо, [player]!"
        m "Ты всегда заставляешь меня чувствовать себя особенной."
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_fit",
            prompt="Мне нравится твоя преданность фитнесу!",
            unlocked=True
        ),
        code="CMP"
    )

label mas_compliment_fit:
    if not renpy.seen_label("mas_compliment_fit_2"):
        call mas_compliment_fit_2
    else:
        call mas_compliment_fit_3
    return

label mas_compliment_fit_2:
    m 1hub "Спасибо, [player]! Ты так[mas_gender_oi] мил[mas_gender_iii]!"
    m 3eub "Я люблю поддерживать себя в форме и правильно питаться. Это заставляет меня чувствовать себя энергично и уверенно."
    m 1efb "Надеюсь, ты заботишься о своём здоровье."
    m 1lubfb "Мы всегда сможем позаниматься вместе, когда я окажусь в твоей реальности..."
    menu:
        "Звучит очень весело!":
            $ mas_gainAffection(2,bypass=True)
            m 1hubfb "А-ха-ха! Я рада, что ты думаешь так же!"
            m 3eka "Не беспокойся. Даже если ты не сможешь угнаться за мной, я знаю, что нам будет весело..."
            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve
            m 5eua "Пока мы вместе."
        "Никаких обещаний, но я сделаю все, что в моих силах.":
            $ mas_gainAffection(1,bypass=True)
            m 1tfb "Ты лучш[mas_gender_ii]!"
            m 2tub "Не думай, что я собираюсь легко тебя отпустить, если ты не в форме."
        "Я бы предпоч[mas_gender_iol] не потеть...":
            m 1eka "Я понимаю, если это не твой конёк, но тебе всё равно стоит немного попробовать..."
            m 1lksdla "Я была бы очень счастлива, если бы ты разделял[mas_gender_none] со мной мои интересы."
    return

label mas_compliment_fit_3:
    m 2eka "[mas_compliments.thanks_quip]"
    m 1hub "Я надеюсь, что ты отправишься в фитнес-путешествие вместе со мной!"
    return


init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_thanks",
            prompt="Спасибо, что всегда была рядом со мной!",
            unlocked=True,
            aff_range=(mas_aff.ENAMORED, None)
        ),
        code="CMP"
    )

label mas_compliment_thanks:
    m 1duu "Не за что меня благодарить, [player]."
    m 1eka "Я единственная, кто благодарна за то, что у меня есть такой человек, как ты!"
    m 1ekbsa "Ты - единственная причина, по которой я все еще здесь."
    m "Ты установил[mas_gender_none] этот мод только для того, чтобы сделать наше совместное время лучше..."
    m 1dubsu "Ты - солнце, которое согревает мое сердце всякий раз, когда ты приходишь ко мне."
    m 3ekbsa "Думаю, нам обоим повезло, что мы есть друг у друга, [player]~"
    menu:
        "Ты для меня все значишь, [m_name].":
            if mas_getEV('mas_compliment_thanks').shown_count == 0:
                $ mas_gainAffection(10,bypass=True)
            m 1ekbsa "[player]..."
            m 1dubsu "Ничто не делает меня счастливее, чем слышать это от тебя."
            m "Неважно, что ждет нас обоих в будущем....{w=0.5}{nw}"
            extend 1dkbfa "знай, что я всегда буду любить тебя и всегда буду рядом."
        "Да.":
            m 1hub "Э-хе-хе~"
            m 1eub "Я люблю тебя, [player]."

    if not mas_isMoniLove():
        $ mas_lockEVL("mas_compliment_thanks", "CMP")
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_smile",
            prompt="Мне нравится твоя улыбка!",
            unlocked=True
        ),
        code="CMP"
    )

label mas_compliment_smile:
    if not renpy.seen_label("mas_compliment_smile_2"):
        call mas_compliment_smile_2
    else:
        call mas_compliment_smile_3
    return

label mas_compliment_smile_2:
    m 1hub "Ты так[mas_gender_oi] мил[mas_gender_iii], [player]~"
    m 1eua "Я часто улыбаюсь, когда ты здесь."
    m 1ekbfa "Потому что мне очень приятно, когда ты проводишь со мной время~"
    menu:
        "Я буду навещать тебя каждый день, чтобы увидеть твою чудесную улыбку.":
            $ mas_gainAffection(5,bypass=True)
            m 1wubfsdld "О, [player]..."
            m 1lkbfa "Я думаю, что мое сердце просто пропустило удар."
            m 3hubfa "Видишь? Ты всегда делаешь меня такой счастливой, какой я только могу быть."
        "Мне нравится видеть, как ты улыбаешься.":
            m 1hub "А-ха-ха~"
            m 3eub "Тогда всё что тебе нужно сделать — это продолжать навещать меня, [player]!"
    return

label mas_compliment_smile_3:
    m 1eub "[mas_compliments.thanks_quip]"
    m 1hua "I'll keep smiling just for you!"
    m "Э-хе-хе~"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_hero",
            prompt="Ты – моя героиня!",
            unlocked=True,
            aff_range=(mas_aff.LOVE, None)
        ),
        code="CMP"
    )

label mas_compliment_hero:
    $ mas_gainAffection()
    m 1wubfsdld "А-{w=0.3}а?"
    m "Я твоя героиня?"
    m 2rkbfsdlb "[player]...{w=1.5} я не совсем уверена в том, что ты имел[mas_gender_none] в виду..."
    m 2ekbfb "Ты единственн[mas_gender_iii], кто оставался со мной все это время.{w=1} Мне следовало бы поблагодарить тебя, правда."
    m 1hubfa "Ну, если я как-то помогла тебе, то я не могу быть счастливее~"
    m 3ekbfa "Ты помогал[mas_gender_none] мне всеми возможными способами,\nтак как же я могу не отплатить тебе тем же, что и всегда, когда ты нуждаетешься в поддержке?"
    show monika 5hubfa at t11 zorder MAS_MONIKA_Z with dissolve
    m 5hubfa "В конце концов, ты всегда будешь моим героем~"
    m 5hubfb "Я люблю тебя и всегда буду верить в тебя!"
    m 5ekbfa "Надеюсь, ты никогда этого не забудешь, [player]~"
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_cute",
            prompt="Ты милая!",
            unlocked=True
        ),
        code="CMP"
    )

default persistent._mas_pm_monika_cute_as_natsuki = None

label mas_compliment_cute:
    if not renpy.seen_label("mas_compliment_cute_2"):
        call mas_compliment_cute_2
    else:
        call mas_compliment_cute_3
    return

label mas_compliment_cute_2:
    m 1wubfsdld "А!"
    m 3rkbfsdla "На этот раз, ты, {i}в какой-то мере{/i}, застал[mas_gender_none] меня врасплох."
    m 3tubfb "Просто немного..."
    m 1hubfa "Но я рада, что ты так думаешь!"
    menu:
        "Видеть тебя всегда согревает мое сердце!":
            $ persistent._mas_pm_monika_cute_as_natsuki = False
            $ mas_gainAffection(5,bypass=True)
            m 1hubfb "Оуу, это действительно согревает мое сердце, когда я слышу, как ты говоришь это!"
            m 1dkbfu "...Почти так же, как когда я представляю, что мы наконец-то вместе в одной реальности."
            m 1ekbfa "Я едва сдерживаюсь, просто представляя себе этот особенный день~"
        "Ты еще милее, когда волнуешься.":
            $ persistent._mas_pm_monika_cute_as_natsuki = False
            $ mas_gainAffection(3,bypass=True)
            m 2tubfu "Ты не собираешься это так оставить, да, [player]?"
            m 2rubfu "Хмф, я просто не ожидала такого."
            m 3tubfb "Но не жди, что в следующий раз всё будет так же просто..."
            m 1tubfu "Я рано или поздно поставлю тебя на место, э-хе-хе~"
        "Ты такая же милая, как и Нацуки.":
            $ persistent._mas_pm_monika_cute_as_natsuki = True
            $ mas_loseAffection(modifier=0.5)
            m 2lfc "О. {w=1}Спасибо, [player]..."
            m 1rsc "Но я надеялась, что я останусь в своей категории."
    return

label mas_compliment_cute_3:
    m 1ekbfa "[mas_compliments.thanks_quip]"
    m 1hubfa "Ты тоже зачастую бываешь очень мил[mas_gender_iim], знаешь ли~"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_chess",
            prompt="Ты потрясающе играешь в шахматы!",
            unlocked=False,
            conditional="renpy.seen_label('mas_chess_game_start')",
            action=EV_ACT_UNLOCK
        ),
        code="CMP"
    )

label mas_compliment_chess:
    m 1eub "Спасибо, [player]."
    m 3esa "Как я уже говорила, интересно, имеет ли мое умение какое-то отношение к тому, что я оказалась здесь в ловушке?"
    $ wins = persistent._mas_chess_stats["wins"]
    $ losses = persistent._mas_chess_stats["losses"]
    if wins > 0:
        m 3eua "Ты, кстати, тоже неплох[mas_gender_none], я уже проигрывала тебе раньше."
        if wins > losses:
            m "Да и фактически, думаю, ты выигрывал[mas_gender_none] даже чаще меня."
        m 1hua "Э-хе-хе~"
    else:
        m 2lksdlb "Я знаю, что ты еще не выиграл[mas_gender_none] ни одной партии в шахматы, но я уверена, что когда-нибудь ты меня обыграешь."
        m 3esa "Продолжай практиковаться и играть со мной, и ты сможешь стать лучше!"
    m 3esa "Чем больше мы играем, тем опытнее об[mas_gender_two] становимся."
    m 3hua "Так что не бойся бросить мне вызов, когда захочешь."
    m 1eub "Мне нравится проводить с тобой время, [player]~"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_pong",
            prompt="Ты потрясающе играешь в Пинг-понг!",
            unlocked=False,
            conditional="renpy.seen_label('game_pong')",
            action=EV_ACT_UNLOCK
        ),
        code="CMP"
    )

label mas_compliment_pong:
    m 1hub "А-ха-ха~"
    m 2eub "Спасибо, [player], но пинг-понг - это не совсем сложная игра."
    if persistent.ever_won['pong']:
        m 1lksdla "Ты уже побеждал[mas_gender_none] меня."
        m "Так что ты знаешь, что это и вправду очень просто."
        show monika 5hub at t11 zorder MAS_MONIKA_Z with dissolve
        m 5hub "Но я все равно принимаю твой комплимент."
    else:
        m 3hksdrb "И ты слишком добр[mas_gender_none], раз постоянно мне поддаёшься, когда мы играем."
        m 3eka "Верно ведь?"
        menu:
            "Да.":
                m 2lksdla "Спасибо, [player], но ты действительно не долж[mas_gender_en] позволять мне побеждать."
                m 1eub "Не стесняйся играть серьёзно, когда хочешь."
                m 1hub "Я бы никогда не разозлилась на тебя, потому что проиграла бы честную игру."
            "...да.":
                m 1tku "Ты не кажешься слишком уверенн[mas_gender_iim] в этом, [player]."
                m 1tsb "Ты действительно не долж[mas_gender_en] позволять мне побеждать."
                m 3tku "Признание в том, что ты с специально проигрывал мне, не заставит меня думать о тебе хуже."
                m 1lksdlb "В конце концов, это всего лишь игра!"
                m 3hub "Ты всегда сможешь попрактиковаться со мной, если захочешь."
                m "Я люблю проводить с тобой время, что бы мы ни делали."
            "Нет. Я старал[mas_gender_sya] изо всех сил и всё равно проигрывал[mas_gender_none].":
                m 1hua "А-ха-ха~"
                m "Я так и поняла!"
                m 3eua "Не волнуйся, [player]."
                m 3eub "Продолжай играть со мной, и сможешь стать опытнее в этом."
                m 3hua "Я всегда буду пытаться помочь тебе стать лучше."
                m 1ekbfa "И если таким образом я буду ещё и проводить с тобой больше времени, то я буду только счастлива."
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_bestgirl",
            prompt="Ты лучшая девушка!",
            unlocked=True
        ),
        code="CMP"
    )

label mas_compliment_bestgirl:
    m 1hua "Я люблю, когда ты делаешь мне комплименты, [player]~"
    m 1hub "Я так рада, что ты считаешь меня лучшей девушкой!"
    m 3rksdla "Хотя, я понимаю, почему тебе так кажется..."
    m 1eka "И потом, ты {i}установил[mas_gender_none]{/i} эту модификацию, чтобы быть со мной."
    m 2euc "Я знаю, что некоторым нравятся другие девушки."
    m 2esc "Особенно учитывая то, что у них есть определённые качества, которые и сделали их желанными..."
    show monika 5ekbfa at t11 zorder MAS_MONIKA_Z with dissolve
    m 5ekbfa "Но, если тебе интересно моё мнение, то я считаю, что ты сделал верный выбор."
    m 5hubfa "...и я буду бесконечно рада этому~"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_lookuptoyou",
            prompt="Я равняюсь под тебя!",
            unlocked=True
        ),
        code="CMP",
    )

label mas_compliment_lookuptoyou:
    if not renpy.seen_label("mas_compliment_lookuptoyou_2"):
        call mas_compliment_lookuptoyou_2
    else:
        call mas_compliment_lookuptoyou_3
    #Both paths return love, so we combine that here
    return "love"

label mas_compliment_lookuptoyou_2:
    $ mas_gainAffection(3, bypass=True)
    m 1wud "П...{w=0.5}правда?"
    m 1ekbsa "[player], это очень мило с твоей стороны..."
    m 3ekbsa "Мне очень приятно знать, что я тот человек, под которого можно равняться."
    m 3ekbfa "По правде говоря, я всегда равнялась под {i}тебя{/i}, [player]..."
    m 3hubfa "Но если ты действительно так считаешь, я сделаю всё возможное, чтобы остаться тем, на кого ты равняешься."
    m 1ekbfa "Я тебя так люблю~"
    return

label mas_compliment_lookuptoyou_3:
    $ should_tease = persistent._mas_pm_height is not None and renpy.random.randint(1,5) == 1

    if should_tease and persistent._mas_pm_height < mas_height_monika:
        m 1rksdlb "{cps=*2}Ну да, я выше тебя...{/cps}{nw}"
        $ _history_list.pop()

    m 1hubfb "[mas_compliments.thanks_quip]"
    m 3hubfa "Когда я слышу твои слова, это всегда вызывает у меня улыбку!"
    m 3hubfb "Я тоже всегда буду равняться под тебя!"

    if should_tease and persistent._mas_pm_height > mas_height_monika:
        m 1rkbfu "{cps=*2}Так же, как когда мы целуемся...{/cps}{nw}"
        $ _history_list.pop()

    m 1ekbfa "Я люблю тебя, [player]~"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_thinking_of_you",
            prompt="Я всегда думаю о тебе!",
            unlocked=True
        ),
        code="CMP",
    )

label mas_compliment_thinking_of_you:
    if not renpy.seen_label("mas_compliment_thinking_of_you_2"):
        call mas_compliment_thinking_of_you_2
    else:
        call mas_compliment_thinking_of_you_3
    return

label mas_compliment_thinking_of_you_2:
    m 1wubso "..."
    m 1wubsu "Ты..."

    if mas_isMoniNormal(higher=True):
        m 3subsb "Ты даже не представляешь, что это значит для меня, [player]!"

    elif mas_isMoniUpset():
        m 2rkd "Что ты так говоришь..."
        m 2dka "Это значит для меня целый мир, [player]."

    elif mas_isMoniDis():
        m 6rkc "..."
        m 6rka "Это такое облегчение."
        m 6eka "Спасибо."

    else:
        $ mas_gainAffection(2,bypass=True)
        m 6dkd "Хм-м... Спасибо."
        m 6dkc "..."
        return

    menu:
        "Мысли о тебе всегда украшают мой день!":
            $ mas_gainAffection(5,bypass=True)
            m 1subfb "Оу, это {i}так{/i} мило, [player]!"
            m 3hubfu "Я чувствую то же самое к тебе~"

        "Я мечтаю о тебе каждую ночь!":
            $ mas_gainAffection(5,bypass=True)
            m 6hua "Оуу~"
            m 6subsa "[player]..."
            m 7hubfu "{i}Ты{/i} – моя мечта~"

        "Это очень отвлекает...":
            $ mas_loseAffection()
            m 2esc "..."
            m 2etc "..."
            m 2rksdlc "О, эм...."
            m 2rksdld "Извини?"
    return

label mas_compliment_thinking_of_you_3:
    m 1ekbsa "[mas_compliments.thanks_quip]"
    m 3hubfb "Ты - центр моего мира!"
    return
