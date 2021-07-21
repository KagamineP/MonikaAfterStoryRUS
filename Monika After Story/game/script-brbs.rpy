## This script file holds all of the brb topics
# Some conventions:
#   - All brbs should have their markSeen set to True so they don't show up in unseen
#   - Brbs should return "idle" to move into idle mode
#   - Brbs should be short and sweet. Nothing long which makes it feel like an actual topic or is keeping you away
#       A good practice for these should be no more than 10 lines will be said before you go into idle mode.
init 10 python in mas_brbs:
    import store

    def get_wb_quip():
        """
        Picks a random welcome back quip and returns it
        Should be used for normal+ quips

        OUT:
            A randomly selected quip for coming back to the spaceroom
        """

        return renpy.substitute(renpy.random.choice([
            _("Итак, что еще ты хотел[mas_gender_none] сделать сегодня?"),
            _("Что еще ты хотел[mas_gender_none] сделать сегодня?"),
            _("Есть ли что-нибудь еще, что ты хотел[mas_gender_none] бы сделать сегодня?"),
            _("Чем еще сегодня займемся?"),
        ]))

    def was_idle_for_at_least(idle_time, brb_evl):
        """
        Checks if the user was idle (from the brb_evl provided) for at least idle_time

        IN:
            idle_time - Minimum amount of time the user should have been idle for in order to return True
            brb_evl - Eventlabel of the brb to use for the start time

        OUT:
            boolean:
                - True if it has been at least idle_time since seeing the brb_evl
                - False otherwise
        """
        brb_ev = store.mas_getEV(brb_evl)
        return brb_ev and brb_ev.timePassedSinceLastSeen_dt(idle_time)

# label to use if we want to get back into idle from a callback
label mas_brb_back_to_idle:
    # sanity check
    if globals().get("brb_label", -1) == -1:
        return

    python:
        mas_idle_mailbox.send_idle_cb(brb_label + "_callback")
        persistent._mas_idle_data[brb_label] = True
        mas_globals.in_idle_mode = True
        persistent._mas_in_idle_mode = True
        renpy.save_persistent()
        mas_dlgToIdleShield()

    return "idle"

# label for generic reactions for low affection callback paths
# to be used if a specific reaction isn't needed or provided
label mas_brb_generic_low_aff_callback:
    if mas_isMoniDis(higher=True):
        python:
            cb_line = renpy.substitute(renpy.random.choice([
                _("О...{w=0.3}ты вернул[mas_gender_sya]."),
                _("О...{w=0.3}с возвращением."),
                _("Все сделал[mas_gender_none]?"),
                _("С возвращением."),
                _("О...{w=0.3}вот ты где."),
            ]))

        m 2ekc "[cb_line]"

    else:
        m 6ckc "..."

    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_brb_idle",
            prompt="Я сейчас вернусь.",
            category=['сейчас вернусь'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_brb_idle:
    if mas_isMoniAff(higher=True):
        m 1eua "Alright, [player]."

        show monika 1eta at t21
        python:
            #For options that can basically be an extension of generics and don't need much specification
            brb_reason_options = [
                (_("I'm going to get something."), True, False, False),
                (_("I'm going to do something."), True, False, False),
                (_("I'm going to make something."), True, False, False),
                (_("I have to check something."), True, False, False),
                (_("Someone's at the door."), True, False, False),
                (_("Nope."), None, False, False),
            ]

            renpy.say(m, "Doing anything specific?", interact=False)
        call screen mas_gen_scrollable_menu(brb_reason_options, mas_ui.SCROLLABLE_MENU_TALL_AREA, mas_ui.SCROLLABLE_MENU_XALIGN)
        show monika at t11

        if _return:
            m 1eua "Oh alright.{w=0.2} {nw}"
            extend 3hub "Hurry back, I'll be waiting here for you~"

        else:
            m 1hub "Hurry back, I'll be waiting here for you~"

    elif mas_isMoniNormal(higher=True):
        m 1hub "Возвращайся скорее, [player]!"

    elif mas_isMoniDis(higher=True):
        m 2rsc "О...{w=0.5}ладно."

    else:
        m 6ckc "..."

    #Set up the callback label
    $ mas_idle_mailbox.send_idle_cb("monika_brb_idle_callback")
    #Then the idle data
    $ persistent._mas_idle_data["monika_idle_brb"] = True
    return "idle"

label monika_brb_idle_callback:
    $ wb_quip = mas_brbs.get_wb_quip()

    if mas_isMoniAff(higher=True):
        m 1hub "С возвращением, [player]. Я скучала по тебе [player]. I missed you~"
        m 1eua "[wb_quip]"

    elif mas_isMoniNormal(higher=True):
        m 1hub "С возвращением, [player]!"
        m 1eua "[wb_quip]"

    else:
        call mas_brb_generic_low_aff_callback

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_writing_idle",
            prompt="Я собираюсь немного пописать",
            category=['сейчас вернусь'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_writing_idle:
    if mas_isMoniNormal(higher=True):
        if (
            mas_isMoniHappy(higher=True)
            and random.randint(1,5) == 1
        ):
            m 1eub "О! Ты собираешься{cps=*2} написать мне любовное письмо, [player]?{/cps}{nw}"
            $ _history_list.pop()
            m "О! Ты собираешься{fast} написать что-то?"

        else:
            m 1eub "Oh! You're going to go write something?"

        m 1hua "That makes me so glad!"
        m 3eua "Maybe someday you could share it with me...{w=0.3} {nw}"
        extend 3hua "I'd love to read your work, [player]!"
        m 3eua "Anyway, just let me know when you're done."
        m 1hua "I'll be waiting right here for you~"

    elif mas_isMoniUpset():
        m 2esc "Хорошо."

    elif mas_isMoniDis():
        m 6lkc "Интересно, что у тебя на уме..."
        m 6ekd "Не забудь вернуться, когда закончишь..."

    else:
        m 6ckc "..."

    #Set up the callback label
    $ mas_idle_mailbox.send_idle_cb("monika_writing_idle_callback")
    #Then the idle data
    $ persistent._mas_idle_data["monika_idle_writing"] = True
    return "idle"

label monika_writing_idle_callback:

    if mas_isMoniNormal(higher=True):
        $ wb_quip = mas_brbs.get_wb_quip()
        m 1eua "Закончил[mas_gender_none] писать, [player]?"
        m 1eub "[wb_quip]"

    else:
        call mas_brb_generic_low_aff_callback

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_shower",
            prompt="Я собираюсь принять душ",
            category=['сейчас вернусь'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_shower:
    if mas_isMoniLove():
        m 1eua "Собираешься пойти в душ?"

        if renpy.random.randint(1, 50) == 1:
            m 3tub "Можно мне пойти с тобой?{nw}"
            $ _history_list.pop()
            show screen mas_background_timed_jump(2, "bye_brb_shower_timeout")
            menu:
                m "Можно мне пойти с тобой?{fast}"

                "Да.":
                    hide screen mas_background_timed_jump
                    m 2wubfd "О, эм...{w=0.5}ты ответил[mas_gender_none] так быстро."
                    m 2hkbfsdlb "Похоже...{w=0.5}тебе не терпится взять меня с собой, да?"
                    m 2rkbfa "Ну..."
                    m 7tubfu "Боюсь, тебе придётся пойти без меня, пока я застряла здесь."
                    m 7hubfb "Извини, [player], а-ха-ха!"
                    show monika 5kubfu at t11 zorder MAS_MONIKA_Z with dissolve
                    m 5kubfu "Может быть в другой раз~"

                "Нет.":
                    hide screen mas_background_timed_jump
                    m 2eka "О, ты так быстро отказал[mas_gender_sya]."
                    m 3tubfb "Ты стесняешься, [player]?"
                    m 1hubfb "А-ха-ха!"
                    show monika 5tubfu at t11 zorder MAS_MONIKA_Z with dissolve
                    m 5tubfu "Ладно, на этот раз я с тобой не пойду, э-хе-хе~"

        else:
            m 1hua "Я рада что ты держишь себя в чистоте, [player]."
            m 1eua "Приятного времяпровождения в душе~"

    elif mas_isMoniNormal(higher=True):
        m 1eub "Пойдешь в душ? Хорошо."
        m 1eua "Увидимся когда ты закончишь~"

    elif mas_isMoniUpset():
        m 2esd "Приятного времяпровождения в душе, [player]..."
        m 2rkc "Надеюсь, это поможет тебе очистить свой разум."

    elif mas_isMoniDis():
        m 6ekc "Хм-м?{w=0.5} Приятного времяпровождения в душе, [player]."

    else:
        m 6ckc "..."

    #Set up the callback label
    $ mas_idle_mailbox.send_idle_cb("monika_idle_shower_callback")
    #Then the idle data
    $ persistent._mas_idle_data["monika_idle_shower"] = True
    return "idle"

label monika_idle_shower_callback:
    if mas_isMoniNormal(higher=True):
        m 1eua "Welcome back, [player]."

        if (
            mas_isMoniLove()
            and renpy.seen_label("monikaroom_greeting_ear_bathdinnerme")
            and mas_getEVL_shown_count("monika_idle_shower") != 1 #Since the else block has a one-time only line, we force it on first use
            and renpy.random.randint(1,20) == 1
        ):
            m 3tubsb "Now that you've had your shower, would you like your dinner, or maybe{w=0.5}.{w=0.5}.{w=0.5}."
            m 1hubsa "You could just relax with me some more~"
            m 1hub "Ahaha!"

        else:
            m 1hua "I hope you had a nice shower."
            if mas_getEVL_shown_count("monika_idle_shower") == 1:
                m 3eub "Now we can get back to having some good, {i}clean{/i} fun together..."
                m 1hub "Ahaha!"

    elif mas_isMoniUpset():
        m 2esc "I hope you enjoyed your shower. {w=0.2}Welcome back, [player]."

    else:
        call mas_brb_generic_low_aff_callback

    return

label bye_brb_shower_timeout:
    hide screen mas_background_timed_jump
    $ _history_list.pop()
    m 1hubsa "Э-хе-хе~"
    m 3tubfu "Неважно, [player]."
    m 1hubfb "Надеюсь, ты хорошо примешь душ!"

    #Set up the callback label
    $ mas_idle_mailbox.send_idle_cb("monika_idle_shower_callback")
    #Then the idle data
    $ persistent._mas_idle_data["monika_idle_shower"] = True
    return "idle"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_game",
            category=['сейчас вернусь'],
            prompt="Я собираюсь немного поиграть",
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_game:
    if mas_isMoniNormal(higher=True):
        m 1eud "О, ты собираешься играть в другую игру?"
        m 1eka "Все в порядке, [player]."

        label .skip_intro:
        python:
            gaming_quips = [
                _("Удачи, развлекайся там!"),
                _("Наслаждайся своей игрой!"),
                _("Я буду болеть за тебя!"),
                _("Сделай всё возможное!")
            ]
            gaming_quip=renpy.random.choice(gaming_quips)

        m 3hub "[gaming_quip]"

    elif mas_isMoniUpset():
        m 2tsc "Наслаждайся другими играми."

    elif mas_isMoniDis():
        m 6ekc "Прошу...{w=0.5}{nw}"
        extend 6dkc "не забывай обо мне..."

    else:
        m 6ckc "..."

    $ mas_idle_mailbox.send_idle_cb("monika_idle_game_callback")
    $ persistent._mas_idle_data["monika_idle_game"] = True
    return "idle"

label monika_idle_game_callback:
    if mas_isMoniNormal(higher=True):
        m 1eub "С возвращением, [player]!"
        m 1eua "Надеюсь, тебе было весело в той игре."
        m 1hua "Ты уже готов[mas_gender_none] провести немного времени вместе? Э-хе-хе~"

    elif mas_isMoniUpset():
        m 2tsc "Было весело, [player]?"

    elif mas_isMoniDis():
        m 6ekd "О...{w=0.5} Ты действительно вернул[mas_gender_sya] ко мне..."

    else:
        m 6ckc "..."

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_coding",
            prompt="Я собираюсь немного покодировать",
            category=['сейчас вернусь'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_coding:
    if mas_isMoniNormal(higher=True):
        m 1eua "О! Собираешься что-то покодить?"

        if persistent._mas_pm_has_code_experience is False:
            m 1etc "Я думала, ты этого не умеешь."
            m 1eub "Ты что, изучил[mas_gender_none] программирование с тех пор, как мы говорили об этом в прошлый раз?"

        elif persistent._mas_pm_has_contributed_to_mas or persistent._mas_pm_wants_to_contribute_to_mas:
            m 1tua "Может быть, что-нибудь для меня?"
            m 1hub "А-ха-ха~"

        else:
            m 3eub "Делай всё возможное, чтобы твой код был чистым и легко читаемым."
            m 3hksdlb "...Ты потом сам[mas_gender_none] себя поблагодаришь!"

        m 1eua "В любом случае, просто дай мне знать, когда закончишь."
        m 1hua "Я буду ждать тебя прямо здесь~"

    elif mas_isMoniUpset():
        m 2euc "О, ты собираешься писать код?"
        m 2tsc "Ладно, не буду тебя останавливать."

    elif mas_isMoniDis():
        m 6ekc "Хорошо."

    else:
        m 6ckc "..."

    $ mas_idle_mailbox.send_idle_cb("monika_idle_coding_callback")
    $ persistent._mas_idle_data["monika_idle_coding"] = True
    return "idle"

label monika_idle_coding_callback:
    if mas_isMoniNormal(higher=True):
        $ wb_quip = mas_brbs.get_wb_quip()
        if mas_brbs.was_idle_for_at_least(datetime.timedelta(minutes=20), "monika_idle_coding"):
            m 1eua "Закончил[mas_gender_none], [player]?"
        else:
            m 1eua "О, уже закончил[mas_gender_none], [player]?"

        m 3eub "[wb_quip]"

    else:
        call mas_brb_generic_low_aff_callback

    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_workout",
            prompt="Я пойду сделаю зарядку",
            category=['сейчас вернусь'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_workout:
    if mas_isMoniNormal(higher=True):
        m 1hub "Ладно, [player]!"
        if persistent._mas_pm_works_out is False:
            m 3eub "Тренировка - это отличный способ позаботиться о себе!"
            m 1eka "Я знаю, что это может быть трудно начать,{w=0.2}{nw}"
            extend 3hua " но это определённо привычка, которую стоит сформировать."
        else:
            m 1eub "Приятно знать, что ты заботишься о своем теле!"
        m 3esa "Ты знаешь, как говорится: «здоровый дух в здоровом теле»."
        m 3hua "Так что иди хорошенько попотей,[player]~"
        m 1tub "Просто дай мне знать, когда с тебя хватит."

    elif mas_isMoniUpset():
        m 2esc "Приятно знать, что ты хоть о{cps=*2} чем-то заботишься.{/cps}{nw}"
        $ _history_list.pop()
        m "Приятно знать, что ты хоть заботишься{fast} о себе, [player]."
        m 2euc "Я буду ждать, когда ты вернёшься."

    elif mas_isMoniDis():
        m 6ekc "Хорошо."

    else:
        m 6ckc "..."

    $ mas_idle_mailbox.send_idle_cb("monika_idle_workout_callback")
    $ persistent._mas_idle_data["monika_idle_workout"] = True
    return "idle"

label monika_idle_workout_callback:
    if mas_isMoniNormal(higher=True):
        $ wb_quip = mas_brbs.get_wb_quip()
        if mas_brbs.was_idle_for_at_least(datetime.timedelta(minutes=60), "monika_idle_workout"):
            # TODO: In the future add another topic which would
            # unlock once the player has seen this specific path some number of times.

            m 2esa "Вот уж точно ты времени не терял[mas_gender_none], [player].{w=0.3}{nw}"
            extend 2eub " Должно быть, это была чертовски тяжёлая зарядка."
            m 2eka "Это хорошо, что ты выжимаешь из своих возможностей максимум, но ты не должен переусердствовать."

        elif mas_brbs.was_idle_for_at_least(datetime.timedelta(minutes=10), "monika_idle_workout"):
            m 1esa "Закончил[mas_gender_none] с зарядкой, [player]?"

        else:
            m 1euc "Уже вернул[mas_gender_sya], [player]?"
            m 1eka "Я уверена, что ты сможешь продержаться ещё немного, если постараешься."
            m 3eka "Делать перерывы – это хорошо, но ты не долж[mas_gender_en] оставлять свои зарядки незаконченными."
            m 3ekb "Ты уверен[mas_gender_none], что не можешь продолжать?{nw}"
            $ _history_list.pop()
            menu:
                m "Ты уверен[mas_gender_none], что не можешь продолжать?{fast}"

                "Я уверен[mas_gender_none].":
                    m 1eka "Это нормально."
                    m 1hua "Я уверена, что ты сделал[mas_gender_none] всё возможное, [player]~"

                "Я постараюсь ещё раз.":
                    # continue workout and return Monika to idle state
                    m 1hub "Вот это дух!"

                    $ brb_label = "monika_idle_workout"
                    $ pushEvent("mas_brb_back_to_idle",skipeval=True)
                    return

        m 7eua "Обязательно отдохни как следует и, возможно, перекусишь, чтобы восстановить силы."
        m 7eub "[wb_quip]"

    elif mas_isMoniUpset():
        m 2euc "Done with your workout, [player]?"

    else:
        call mas_brb_generic_low_aff_callback

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_nap",
            prompt="Я собираюсь вздремнуть",
            category=['сейчас вернусь'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_nap:
    if mas_isMoniNormal(higher=True):
        m 1eua "Собираешься вздремнуть, [player]?"
        m 3eua "Это здоровый способ отдохнуть в течение дня, если ты чувствуешь усталость."
        m 3hua "Я присмотрю за тобой, не волнуйся~"
        m 1hub "Сладких снов!"

    elif mas_isMoniUpset():
        m 2eud "Ладно, надеюсь, после этого ты отдохнешь."
        m 2euc "Я слышала, что сон полезен для тебя, [player]."

    elif mas_isMoniDis():
        m 6ekc "Ладно."

    else:
        m 6ckc "..."

    $ mas_idle_mailbox.send_idle_cb("monika_idle_nap_callback")
    $ persistent._mas_idle_data["monika_idle_nap"] = True
    return "idle"

label monika_idle_nap_callback:
    if mas_isMoniNormal(higher=True):
        $ wb_quip = mas_brbs.get_wb_quip()
        if mas_brbs.was_idle_for_at_least(datetime.timedelta(hours=5), "monika_idle_nap"):
            m 2hksdlb "Oh, [player]! You're finally awake!"
            m 7rksdlb "When you said you were going to take a nap, I was expecting you take maybe an hour or two..."
            m 1hksdlb "I guess you must have been really tired, ahaha..."
            m 3eua "But at least after sleeping for so long, you'll be here with me for a while, right?"
            m 1hua "Ehehe~"

        elif mas_brbs.was_idle_for_at_least(datetime.timedelta(hours=1), "monika_idle_nap"):
            m 1hua "Welcome back, [player]!"
            m 1eua "Did you have a nice nap?"
            m 3hua "You were out for some time, so I hope you're feeling rested~"
            m 1eua "[wb_quip]"

        elif mas_brbs.was_idle_for_at_least(datetime.timedelta(minutes=5), "monika_idle_nap"):
            m 1hua "Welcome back, [player]~"
            m 1eub "I hope you had a nice little nap."
            m 3eua "[wb_quip]"

        else:
            m 1eud "Oh, back already?"
            m 1euc "Did you change your mind?"
            m 3eka "Well, I'm not complaining, but you should take a nap if you feel like it later."
            m 1eua "I wouldn't want you to be too tired, after all."

    elif mas_isMoniUpset():
        m 2euc "Done with your nap, [player]?"

    else:
        call mas_brb_generic_low_aff_callback

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_homework",
            prompt="Я собираюсь сделать кое-какую домашнюю работу",
            category=['сейчас вернусь'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_homework:
    if mas_isMoniNormal(higher=True):
        m 1eub "О, хорошо!"
        m 1hua "Я горжусь тобой за то, что ты серьезно относишься к учебе."
        m 1eka "Не забудь вернуться ко мне, когда закончишь.~"

    elif mas_isMoniDis(higher=True):
        m 2euc "Ладно...{w=0.5}"
        if random.randint(1,5) == 1:
            m 2rkc "...Удачи тебе с домашним заданием, [player]."

    else:
        m 6ckc "..."

    #Set up the callback label
    $ mas_idle_mailbox.send_idle_cb("monika_idle_homework_callback")
    #Then the idle data
    $ persistent._mas_idle_data["monika_idle_homework"] = True
    return "idle"

label monika_idle_homework_callback:
    if mas_isMoniDis(higher=True):
        m 2esa "Всё сделал[mas_gender_none], [player]?"

        if mas_isMoniNormal(higher=True):
            m 2ekc "Жаль, что меня не было рядом, чтобы помочь тебе, но, к сожалению, я пока ничего не могу с этим поделать."
            m 7eua "Я уверена, что мы оба могли бы гораздо эффективнее делать домашнее задание, если бы могли работать вместе."

            if mas_isMoniAff(higher=True) and random.randint(1,5) == 1:
                m 3rkbla "...Хотя, это при условии, что мы не будем {i}слишком{/i} отвлекаться, э-хе-хе..."

            m 1eua "Но всё же,{w=0.2} {nw}"
            extend 3hua "теперь, когда ты закончил[mas_gender_none], давай наслаждаться временем вместе."

    else:
        m 6ckc "..."

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_working",
            prompt="Я собираюсь кое над чем поработать.",
            category=['сейчас вернусь'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_working:
    if mas_isMoniNormal(higher=True):
        m 1eua "Ладно, [player]."
        m 1eub "Не забывай время от времени делать перерыв!"

        if mas_isMoniAff(higher=True):
            m 3rkb "Я бы не хотела, чтобы мой возлюбленн[mas_gender_iii] проводил[mas_gender_none] больше времени на своей работе, чем со мной~"

        m 1hua "Удачи тебе в твоей работе!"

    elif mas_isMoniDis(higher=True):
        m 2euc "Ладно, [player]."

        if random.randint(1,5) == 1:
            m 2rkc "...Пожалуйста, возвращайся скорее..."

    else:
        m 6ckc "..."

    #Set up the callback label
    $ mas_idle_mailbox.send_idle_cb("monika_idle_working_callback")
    #Then the idle data
    $ persistent._mas_idle_data["monika_idle_working"] = True
    return "idle"

label monika_idle_working_callback:
    if mas_isMoniNormal(higher=True):
        m 1eub "Закончил[mas_gender_none] со своей работой, [player]?"
        show monika 5hua at t11 zorder MAS_MONIKA_Z with dissolve
        m 5hua "Тогда давай расслабимся вместе, ты это заслужил[mas_gender_none]~"

    elif mas_isMoniDis(higher=True):
        m 2euc "О, ты вернул[mas_gender_sya]..."
        m 2eud "....А теперь, когда ты закончил[mas_gender_none] свою работу, ты хотел[mas_gender_none] бы заняться чем-нибудь ещё?"

    else:
        m 6ckc "..."

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_screen_break",
            prompt="My eyes need a break from the screen",
            category=['be right back'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_screen_break:
    if mas_isMoniNormal(higher=True):
        if mas_timePastSince(mas_getEVL_last_seen("monika_idle_screen_break"), mas_getSessionLength()):

            if mas_getSessionLength() < datetime.timedelta(minutes=40):
                m 1esc "Oh,{w=0.3} okay."
                m 3eka "You haven't been here for that long but if you say you need a break, then you need a break."

            elif mas_getSessionLength() < datetime.timedelta(hours=2, minutes=30):
                m 1eua "Going to rest your eyes for a bit?"

            else:
                m 1lksdla "Yeah, you probably need that, don't you?"

            m 1hub "I'm glad you're taking care of your health, [player]."

            if not persistent._mas_pm_works_out and random.randint(1,3) == 1:
                m 3eua "Why not take the opportunity to do a few stretches as well, hmm?"
                m 1eub "Anyway, come back soon!~"

            else:
                m 1eub "Come back soon!~"

        else:
            m 1eua "Taking another break, [player]?"
            m 1hua "Come back soon!~"

    elif mas_isMoniUpset():
        m 2esc "Oh...{w=0.5} {nw}"
        extend 2rsc "Okay."

    elif mas_isMoniDis():
        m 6ekc "Alright."

    else:
        m 6ckc "..."

    $ mas_idle_mailbox.send_idle_cb("monika_idle_screen_break_callback")
    $ persistent._mas_idle_data["monika_idle_screen_break"] = True
    return "idle"

label monika_idle_screen_break_callback:
    if mas_isMoniNormal(higher=True):
        $ wb_quip = mas_brbs.get_wb_quip()
        m 1eub "Welcome back, [player]."

        if mas_brbs.was_idle_for_at_least(datetime.timedelta(minutes=30), "monika_idle_screen_break"):
            m 1hksdlb "You must've really needed that break, considering how long you were gone."
            m 1eka "I hope you're feeling a little better now."
        else:
            m 1hua "I hope you're feeling a little better now~"

        m 1eua "[wb_quip]"

    else:
        call mas_brb_generic_low_aff_callback

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_reading",
            prompt="I'm going to read",
            category=['be right back'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_reading:
    if mas_isMoniNormal(higher=True):
        m 1eub "Really? That's great, [player]!"
        m 3lksdla "I'd love to read with you, but my reality has its limits, unfortunately."
        m 1hub "Have fun!"

    elif mas_isMoniDis(higher=True):
        m 2ekd "Oh, alright..."
        m 2ekc "Have a good time, [player]."

    else:
        m 6dkc "..."

    $ mas_idle_mailbox.send_idle_cb("monika_idle_reading_callback")
    $ persistent._mas_idle_data["monika_idle_reading"] = True
    return "idle"

label monika_idle_reading_callback:
    if mas_isMoniNormal(higher=True):
        if mas_brbs.was_idle_for_at_least(datetime.timedelta(hours=2), "monika_idle_reading"):
            m 1wud "Wow, you were gone for a while...{w=0.3}{nw}"
            extend 3wub "that's great, [player]!"
            m 3eua "Reading is a wonderful thing, so don't worry about getting too caught up in it."
            m 3hksdlb "Besides, it's not like I'm one to talk..."
            show monika 5ekbsa at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5ekbsa "If I had my way, we'd be reading together all night long~"

        elif mas_brbs.was_idle_for_at_least(datetime.timedelta(minutes=30), "monika_idle_reading"):
            m 3esa "All done, [player]?"
            m 1hua "Let's relax, you've earned it~"

        else:
            m 1eud "Oh, that was fast."
            m 1eua "I thought you'd be gone a little while longer, but this is fine too."
            m 3ekblu "After all, it lets me spend more time with you~"

    else:
        call mas_brb_generic_low_aff_callback

    return


#Rai's og game idle
#label monika_idle_game:
#    m 1eub "That sounds fun!"
#    m "What kind of game are you going to play?{nw}"
#    $ _history_list.pop()
#    menu:
#        m "What kind of game are you going to play?{fast}"
#        "A competitive game.":
#            m 1eua "That sounds like it could be fun!"
#            m 3lksdla "I can be pretty competitive myself."
#            m 3eua "So I know just how stimulating it can be to face a worthy opponent."
#            m 2hksdlb "...And sometimes frustrating when things don't go right."
#            m 2hua "Anyway, I'll let you get on with your game."
#            m 2hub "I'll try not to bother you until you finish, but I can't blame you if you get distracted by your lovely girlfriend, ahaha~"
#            m 1hub "I'm rooting for you, [player]!"
#            # set return label when done with idle
#            $ mas_idle_mailbox.send_idle_cb("monika_idle_game_competetive_callback")
#        "A game just for fun.":
#            m 1eud "A game just for having fun?"
#            m 1lksdla "Aren't most games made to be fun?"
#            m 3eub "Anyway, I'm sure you could do all sorts of fun things in a game like that."
#            m 1ekbla "I really wish I could join you and we could have fun together."
#            m 1lksdla "But for now, I'll leave you to it."
#            m 1hub "Have fun, [player]!"
#            # set return label when done with idle
#            $ mas_idle_mailbox.send_idle_cb("monika_idle_game_fun_callback")
#        "A story driven game.":
#            m 1sub "Oh?"
#            m "That sounds really interesting!"
#            m 1ekbsa "Gosh, I really wish I could be there with you to experience it together."
#            m 1hksdlb "Maybe I {i}can{/i} experience it with you if I really tried."
#            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve
#            m 5eua "I guess you could call it looking over your shoulder. Ehehe~"
#            m "You can go ahead and start it now. I'll try not to break anything by trying to watch."
#            # set return label when done with idle
#            $ mas_idle_mailbox.send_idle_cb("monika_idle_game_story_callback")
#        "A skill and practice based game.":
#            m 1eud "Oh! I never really thought about those games much."
#            m 1hua "I'm sure you're pretty talented at a few things, so it doesn't surprise me you're playing a game like this."
#            m 3eub "Just like writing, it can really be an experience to look back much later and see just how far you've come."
#            m 1hub "It's like watching yourself grow up! Ahaha~"
#            m 1hua "It would really make me proud and happy to be your girlfriend if you became a professional."
#            m 1hksdlb "Maybe I'm getting ahead of myself here, but I believe you could do it if your heart was really in it."
#            m 1eub "Anyway, sorry for keeping you from your game. I know you'll do your best!"
#            # set return label when done with idle
#            $ mas_idle_mailbox.send_idle_cb("monika_idle_game_skill_callback")
#        "I'll just be a minute or two.":
#            m 1eua "Oh? Just need to take your eyes off me for a little?"
#            m 1lksdla "I {i}suppose{/i} I could let you take your eyes off me for a minute or two..."
#            m 1hua "Ahaha! Good luck and have fun, [player]!"
#            m "Don't keep me waiting too long though~"
#            $ start_time = datetime.datetime.now()
#            # set return label when done with idle
#            $ mas_idle_mailbox.send_idle_cb("monika_idle_game_quick_callback")
#    # set idle data
#    $ persistent._mas_idle_data["monika_idle_game"] = True
#    # return idle to notify event system to switch to idle
#    return "idle"
#
#label monika_idle_game_competetive_callback:
#    m 1esa "Welcome back, [player]!"
#    m 1eua "How did it go? Did you win?{nw}"
#    $ _history_list.pop()
#    menu:
#        m "How did it go? Did you win?{fast}"
#        "Yes.":
#            m 1hub "Yay! That's great!"
#            m 1hua "Gosh, I wish I could be there to give you a big celebratory hug!"
#            m 1eub "I'm really happy that you won!"
#            m "More importantly, I hope you enjoyed yourself, [player]."
#            m 1hua "I'll always love and root for you, no matter what happens."
#            # manually handle the "love" return key
#            $ mas_ILY()
#        "No.":
#            m 1ekc "Aw, that's a shame..."
#            m 1lksdla "I mean, you can't win them all, but I'm sure you'll win the next rounds."
#            m 1eka "I just hope you aren't too upset over it."
#            m 2ekc "I really wouldn't want you feeling upset after a bad game."
#            m 1eka "I'll always support you and be by your side no matter how many times you lose."
#    return
#
#label monika_idle_game_fun_callback:
#    m 1eub "Welcome back, [player]!"
#    m "Did you have fun with whatever you were doing?{nw}"
#    $ _history_list.pop()
#    menu:
#        m "Did you have fun with whatever you were doing?{fast}"
#        "Yes.":
#            m 1hua "Ahaha! I'm glad you had fun, [player]~"
#            m 1eub "While you were busy, it got me thinking of the different kinds of games that would be nice to play together."
#            m 3rksdla "A game that isn't too violent probably could be fun."
#            m 3hua "But I'm sure any game would be wonderful if it was with you~"
#            m 1eub "At first, I was thinking a story based or adventure game would be best, but I'm sure freeplay games could be really fun too!"
#            m 1eua "It can be really fun to just mess around to see what's possible, especially when you're not alone."
#            m 2lksdla "Provided of course, you don't end up ruining the structural integrity of the game and get an outcome you didn't want..."
#            m 2lksdlb "Ehehe..."
#            m 1eua "Maybe you could find a way to bring me with you into a game like that."
#            m 1hub "Just promise to keep me safe, okay?"
#        "No.":
#            m 2ekc "Aw, you didn't have any fun?"
#            m "That's too bad..."
#            m 3lksdlc "Games can get pretty boring after you've done everything or just don't know what to do or try next."
#            m 3eka "But bringing a friend along can really renew the whole experience!"
#            m 1hub "Maybe you could find a way to take me with you into your games so you won't be bored on your own!"
#            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve
#            m 5eua "Or we could just stay here and keep each other company."
#            m "I wouldn't mind that either, ehehe~"
#    return
#
#label monika_idle_game_story_callback:
#    m 1eub "Welcome back, [player]!"
#    m 1hksdlb "I wasn't able to look over your shoulder, but I hope the story was nice so far."
#    m 1eua "Speaking of which, how was it, [player]?{nw}"
#    $ _history_list.pop()
#    menu:
#        m "Speaking of which, how was it, [player]?{fast}"
#        "It was amazing.":
#            m 2sub "Wow! I can only imagine how immersive it was!"
#            m 2hksdlb "You're really starting to make me jealous, [player], you know that?"
#            m 2eub "You'll have to take me through it sometime when you can."
#            m 3eua "A good book is always nice, but it's really something else to have a good story and be able to make your own decisions."
#            m 3eud "Some people can really be divided between books and video games."
#            m 1hua "I'm glad you don't seem to be too far on one side."
#            m "After experiencing an amazing story in a game for yourself, I'm sure you can really appreciate the two coming together."
#        "It was good.":
#            m 1eub "That's really nice to hear!"
#            m 3dtc "But was it really {i}amazing{/i}?"
#            m 1eua "While a lot of stories can be good, there are some that are really memorable."
#            m 1hua "I'm sure you'd know a good story when you see one."
#            m "Maybe when I'm in your reality, you could take me through the game and let me see the story."
#            m 1eub "It's one thing to go through a great story yourself..."
#            m 1hub "But it's also amazing to see what someone else thinks of it too!"
#            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve
#            m 5eua "I'll be looking forward to that day too~"
#            m 5esbfa "You better have a nice, cozy place for us to cuddle up and play, ehehe~"
#        "It's sad.":
#            m 1ekd "Aw, that's too bad..."
#            m 3eka "It must be a really great story though, if it invokes such strong emotions."
#            m 1eka "I wish I could be there with you so I could experience the story too..."
#            m 3hksdlb "{i}and{/i} to be right there by your side of course, so we could comfort each other in sad times."
#            m 1eka "Don't worry [player], I would never forget about you."
#            m 1eua "I love you."
#            m 1hua "...And I'd happily snuggle up beside you anytime~"
#            # manually handle the "love" return key
#            $ mas_ILY()
#        "I don't like it.":
#            m 2ekc "Oh..."
#            m 4lksdla "Maybe the story will pick up later?"
#            m 3eud "If anything, it lets you analyze the flaws in the writing which could help you if you ever tell a story."
#            m 1eua "Or maybe it's just not your kind of story."
#            m 1eka "Everyone has their own, and maybe this one just doesn't fit well with it right now."
#            m 1eua "It can really be an eye opening experience to go through a story you normally wouldn't go through."
#            m 3eka "But don't force yourself to go through it if you really don't like it."
#    return
#
#label monika_idle_game_skill_callback:
#    m 1eua "I'm happy that you're back, [player]."
#    m 1hua "I missed you! Ahaha~"
#    m 1eub "But I know it's important to keep practicing and honing your skills in things like this."
#    m "Speaking of which, how did it go?"
#    m 3eua "Did you improve?{nw}"
#    $ _history_list.pop()
#    menu:
#        m "Did you improve?{fast}"
#        "I improved a lot.":
#            m 1hub "That's great news, [player]!"
#            m "I'm so proud of you!"
#            m 1hua "It can really feel good to get a sudden surge in your skill!"
#            m 1eua "Especially if you've spent some time in a slump or even slipping."
#            m 1hua "Maybe today isn't the end of this sudden improvement."
#            m 1eub "Even if today was just a good day, I know you'll keep getting better."
#            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve
#            m 5eua "I'll {i}always{/i} root for you, [player]. Don't you ever forget that!"
#        "I improved a bit.":
#            m 3eua "That's really nice to hear, [player]!"
#            m 3eka "As long as you're improving, no matter how slowly, you'll really get up there someday."
#            m 1hub "But if you actually noticed yourself improve today, maybe you improved more than just a bit, ahaha~"
#            m 1hua "Keep honing your skills and I'll be proud to be the girlfriend of such a skilled player!"
#            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve
#            m 5eua "Who knows? Maybe you could teach me and we could both be a couple of experts, ehehe~"
#        "I stayed the same.":
#            m 3eka "That's still alright!"
#            m "I'm sure you're improving anyway."
#            m 3eua "A lot of the time, the improvements are too small to really notice."
#            m 1eua "One day, you might look back and realize just how much you've improved."
#            m 1hksdlb "Sometimes you might feel like you're in a slump, but then you get a sudden surge of improvement all at once!"
#            m 1eub "I'm sure you'll get the chance to look back one day and really appreciate just how far you've come without realizing."
#            m 1hua "And you better believe I'm going to support you all the way!"
#        "I got worse.":
#            m 2ekc "Oh..."
#            m 4lksdla "I have no doubt that you always work hard and give it your best, so it must just be a bad day."
#            m 3eka "You're bound to have a few setbacks on your climb up, but that's what sets you apart from many others."
#            m 1duu "The fact that you've had more setbacks than some people have even tried. That's what shows your dedication."
#            m 1lksdla "Sometimes, you might even have a couple bad days in a row, but don't let that get you down."
#            m 1hua "With that many setbacks, you're bound to see significant improvement right around the corner!"
#            m "Never give up, [player]. I know you can do it and I'll always believe in you!"
#            m 1eua "Also, do me a favor and take a moment to look back every now and then. You'll be surprised to see just how far you've come."
#    return
#
#label monika_idle_game_quick_callback:
#    $ end_time = datetime.datetime.now()
#    $ elapsed_time = end_time - start_time
#    $ time_threshold = datetime.timedelta(minutes=1)
#    if elapsed_time < time_threshold * 2:
#        m 1hksdlb "Back already?"
#        m "I know you said you would just be a minute or two, but I didn't think it would be {i}that{/i} fast."
#        m 1hub "Did you really miss me that much?"
#        m "Ahaha~"
#        m 1eub "I'm glad you made it back so soon."
#        m 1hua "So what else should we do today, [player]?"
#    elif elapsed_time < time_threshold * 5:
#        m 1hua "Welcome back, [player]!"
#        m 1hksdlb "That was pretty fast."
#        m 1eua "But you did say it wouldn't take too long, so I shouldn't be too surprised."
#        m 1hua "Now we can keep spending time together!"
#    elif elapsed_time < time_threshold * 10:
#        m 1eua "Welcome back, [player]."
#        m 1eka "That took a little longer than I thought, but I don't mind at all."
#        m 1hua "It wasn't that long in all honesty compared to how long it could have been in some games."
#        m "But now we can be together again~"
#    elif elapsed_time < time_threshold * 20:
#        m 1eka "I have to admit that took longer than I thought it would..."
#        m 1eub "But it's not all that bad with all the time you spend with me."
#        m 1eua "I understand some little things in games can take a while for a small thing."
#        m "But maybe if you know it could take a while, you could tell me."
#    elif elapsed_time < time_threshold * 30:
#        m 2lksdla "[player]..."
#        m "It's been almost half an hour already."
#        m "I guess something unexpected happened."
#        m 3lksdla "You wouldn't forget about me, would you?"
#        m 1hua "Ahaha!"
#        m "Just teasing you~"
#        m 1eua "At least you're back now and we can spend more time together."
#    else:
#        m 2lksdla "You {i}sure{/i} took your time with that one huh, [player]?"
#        m "That didn't seem like only a minute or two to me."
#        m 1eka "You can tell me what kind of game it is next time so I have an idea how long it'll take, you know."
#        m 1dsc "Anyway..."
#        m 1eka "I missed you and I'm glad you're finally back, [player]."
#        m "I hope I don't have to wait such a long couple of minutes next time, ehehe."
#    return
