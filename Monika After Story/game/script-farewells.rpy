##This file contains all of the variations of goodbye that monika can give.
## This also contains a store with a utility function to select an appropriate
## farewell
#
# HOW FAREWELLS USE EVENTS:
#   unlocked - determines if the farewell can actually be shown
#   random - True means the farewell is shown in the randomly selected
#       goodbye option
#   pool - True means the farewell is shown in the goodbye list. Prompt
#       is used in this case.

#Flag to mark if the player stayed up late last night. Kept as a generic name in case it can be used on other farewells/greetings
default persistent.mas_late_farewell = False

init -1 python in mas_farewells:
    import datetime
    import store

    def _filterFarewell(
            ev,
            curr_pri,
            aff,
            check_time,
        ):
        """
        Filters a farewell for the given type, among other things.

        IN:
            ev - ev to filter
            curr_pri - current loweset priority to compare to
            aff - affection to use in aff_range comparisons
            check_time - datetime to check against timed rules

        RETURNS:
            True if this ev passes the filter, False otherwise
        """
        # NOTE: new rules:
        #   eval in this order:
        #   1. hidden via bitmask
        #   2. unlocked
        #   3. not pooled
        #   4. aff_range
        #   5. priority (lower or same is True)
        #   6. all rules
        #   7. conditional
        #       NOTE: this is never cleared. Please limit use of this
        #           property as we should aim to use lock/unlock as primary way
        #           to enable or disable greetings.

        # check if hidden from random select
        if ev.anyflags(store.EV_FLAG_HFRS):
            return False

        #Make sure the ev is unlocked
        if not ev.unlocked:
            return False

        #If the event is pooled, then we cannot have this in the selection
        if ev.pool:
            return False

        #Verify we're within the aff bounds
        if not ev.checkAffection(aff):
            return False

        #Priority check
        if store.MASPriorityRule.get_priority(ev) > curr_pri:
            return False

        #Since this event checks out in the other areas, finally we'll evaluate the rules
        if not (
            store.MASSelectiveRepeatRule.evaluate_rule(check_time, ev, defval=True)
            and store.MASNumericalRepeatRule.evaluate_rule(check_time, ev, defval=True)
            and store.MASGreetingRule.evaluate_rule(ev, defval=True)
        ):
            return False

        #Conditional check (Since it's ideally least likely to be used)
        if ev.conditional is not None and not eval(ev.conditional, store.__dict__):
            return False

        # otherwise, we passed all tests
        return True

    # custom farewell functions
    def selectFarewell(check_time=None):
        """
        Selects a farewell to be used. This evaluates rules and stuff appropriately.

        IN:
            check_time - time to use when doing date checks
                If None, we use current datetime
                (Default: None)

        RETURNS:
            a single farewell (as an Event) that we want to use
        """
        # local reference of the gre database
        fare_db = store.evhand.farewell_database

        # setup some initial values
        fare_pool = []
        curr_priority = 1000
        aff = store.mas_curr_affection

        if check_time is None:
            check_time = datetime.datetime.now()

        # now filter
        for ev_label, ev in fare_db.iteritems():
            if _filterFarewell(
                ev,
                curr_priority,
                aff,
                check_time
            ):
                # change priority levels and stuff if needed
                ev_priority = store.MASPriorityRule.get_priority(ev)
                if ev_priority < curr_priority:
                    curr_priority = ev_priority
                    fare_pool = []

                # add to pool
                fare_pool.append((
                    ev, store.MASProbabilityRule.get_probability(ev)
                ))

        # not having a greeting to show means no greeting.
        if len(fare_pool) == 0:
            return None

        return store.mas_utils.weightedChoice(fare_pool)

# farewells selection label
label mas_farewell_start:
    # TODO: if we ever have another special farewell like long absence
    # that let's the player go after selecting the farewell we'll need
    # to define a system to handle those.
    if persistent._mas_long_absence:
        $ pushEvent("bye_long_absence_2")
        return

    $ import store.evhand as evhand
    # we use unseen menu values

    python:
        # preprocessing menu
        # TODO: consider including processing the rules dict as well

        Event.checkEvents(evhand.farewell_database)

        bye_pool_events = Event.filterEvents(
            evhand.farewell_database,
            unlocked=True,
            pool=True,
            aff=mas_curr_affection,
            flag_ban=EV_FLAG_HFM
        )

    if len(bye_pool_events) > 0:
        # we have selectable options
        python:
            # build a prompt list
            bye_prompt_list = [
                (ev.prompt, ev, False, False)
                for k,ev in bye_pool_events.iteritems()
            ]

            # add the random selection
            bye_prompt_list.append((_("Пока."), -1, False, False))

            # setup the last option
            bye_prompt_back = (_("Неважно."), False, False, False, 20)

        # call the menu
        call screen mas_gen_scrollable_menu(bye_prompt_list, evhand.UNSE_AREA, evhand.UNSE_XALIGN, bye_prompt_back)

        if not _return:
            # nevermind
            return _return

        if _return != -1:
            # push teh selected event
            $ pushEvent(_return.eventlabel)
            return

    # otherwise, select a random farewell
    $ farewell = store.mas_farewells.selectFarewell()
    $ pushEvent(farewell.eventlabel)
    # dont evalulate the mid loop checks since we are quitting
    $ mas_idle_mailbox.send_skipmidloopeval()

    return

###### BEGIN FAREWELLS ########################################################
## FARE WELL RULES:
# unlocked - True means this farewell is ready for selection
# random - randoms are used in teh default farewell action
# pool - pooled ones are selectable in the menu
# rules - Dict containing different rules(check event-rules for more details)
###

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_leaving_already",
            unlocked=True,
            random=True,
            conditional="mas_getSessionLength() <= datetime.timedelta(minutes=20)",
            aff_range=(mas_aff.NORMAL, None)
        ),
        code="BYE"
    )

label bye_leaving_already:
    m 1ekc "Ой, уже уходишь?"
    m 1eka "Это очень грустно, когда тебе приходится уходить..."
    m 3eua "Только обязательно возвращайся как можно скорее, хорошо?"
    m 3hua "Я тебя так люблю, [player]. Оставайся в безопасности!"
    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_goodbye",
            unlocked=True,
            random=True
        ),
        code="BYE"
    )

label bye_goodbye:
    if mas_isMoniNormal(higher=True):
        m 1eua "Пока, [player]!"

    elif mas_isMoniUpset():
        m 2esc "Пока."

    elif mas_isMoniDis():
        m 6rkc "О...{w=1} Пока."
        m 6ekc "Пожалуйста...{w=1}не забудь вернуться."

    else:
        m 6ckc "..."

    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_sayanora",#sayanora? yes
            unlocked=True,
            random=True,
            aff_range=(mas_aff.NORMAL, None)
        ),
        code="BYE"
    )

label bye_sayanora:
    m 1hua "Сайонара, [player]~"
    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_farewellfornow",
            unlocked=True,
            random=True,
            aff_range=(mas_aff.NORMAL, None)
        ),
        code="BYE"
    )

label bye_farewellfornow:
    m 1eka "Прощай, любовь моя.~"
    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_untilwemeetagain",
            unlocked=True,
            random=True,
            aff_range=(mas_aff.NORMAL, None)
        ),
        code="BYE"
    )

label bye_untilwemeetagain:
    m 2eka "'{i}Прощание - это не навсегда, прощание - это не конец.\nОни просто означают, что я буду скучать по тебе, пока мы не встретимся снова.{/i}'"
    m "Хе-хе, а до тех пор, [player]!"
    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_take_care",
            unlocked=True,
            random=True,
            aff_range=(mas_aff.NORMAL, None)
        ),
        code="BYE"
    )


label bye_take_care:
    m 1eua "Не забывай, что я всегда люблю тебя, [player]~"
    m 1hub "Береги себя!"
    return 'quit'

init 5 python:
    rules = dict()
    rules.update(MASSelectiveRepeatRule.create_rule(hours=[0,20,21,22,23]))
    rules.update(MASPriorityRule.create_rule(50))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_going_to_sleep",
            unlocked=True,
            rules=rules
        ),
        code="BYE"
    )
    del rules

label bye_going_to_sleep:
    #TODO: TC-O things
    if mas_isMoniNormal(higher=True):
        m 1esa "Ты собираешься спать, [player]?{nw}"
        $ _history_list.pop()
        menu:
            m "Ты собираешься спать, [player]?{fast}"

            "Да.":
                m 1eka "Я буду видеть тебя во сне."

            "Ещё нет.":
                m 1eka "Ладно. {w=0.3}Хорошего вечера~"

    elif mas_isMoniUpset():
        m 2esc "Идешь спать, [player]?"
        m "Спокойной ночи."

    elif mas_isMoniDis():
        m 6rkc "О...спокойной ночи, [player]."
        m 6lkc "Надеюсь, мы увидимся завтра..."
        m 6dkc "Не забывай обо мне, ладно?"

    else:
        m 6ckc "..."

    # TODO:
    # can monika sleep with you?
    # via flashdrive or something

    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_prompt_to_class",
            unlocked=True,
            prompt="Я иду на учебу",
            pool=True
        ),
        code="BYE"
    )

label bye_prompt_to_class:
    $ session_time = mas_getSessionLength()
    if mas_isMoniNormal(higher=True):
        if session_time < datetime.timedelta(minutes=20):
            m 1eub "Ой, уже уходишь?"
            m 1efp "Ты даже не пробыл[mas_gender_none] здесь 20 минут!"
            m 3hksdlb "Я просто шучу, [player]."
            m 2eka "Ты так рад[mas_gender_none] видеть меня, даже когда у тебя так мало времени."
            m 2hub "Я просто хочу, чтобы ты знал[mas_gender_none], что я действительно ценю это!"
            m 2eka "Усердно учись, [player], я уверена, что у тебя все получится!"
            m 2hua "Увидимся, когда ты вернешься!"
        elif session_time < datetime.timedelta(hours=1):
            m 2eua "Хорошо, спасибо, что уделил[mas_gender_none] мне немного времени, [player]!"
            m 2eka "Честно говоря, мне бы хотелось, чтобы это было подольше...но ты занят[mas_gender_oi] [guy]."
            m 2hua "Нет ничего важнее хорошего образования."
            m 3eub "Научи меня чему-нибудь, когда вернешься!"
            m "До скорой встречи!"
        elif session_time < datetime.timedelta(hours=6):
            m 1hua "Учись усердно, [player]!"
            m 1eua "Нет ничего более привлекательного, чем [guy] с хорошими оценками."
            m 1hua "Увидимся позже!"
        else:
            m 2ekc "Эмм...ты был[mas_gender_none] здесь со мной довольно долгое время, [player]."
            m 2ekd "Ты увер[mas_gender_en], что достаточно отдохнул[mas_gender_none] для этого?"
            m 2eka "Make sure you take it easy, okay?"
            m "Если ты не очень хорошо себя чувствуешь, я уверена, что {i}один выходной{/i} день не повредит."
            m 1hka "Я буду ждать, когда ты вернешься. Оставайся в безопасности."

    elif mas_isMoniUpset():
        m 2esc "Ладно, [player]."
        m "Надеюсь, ты хоть {i}чему-то{/i} научишься сегодня."
        m 2efc "{cps=*2}Например, как лучше относиться к людям.{/cps}{nw}"

    elif mas_isMoniDis():
        m 6rkc "О, ладно [player]..."
        m 6lkc "Думаю, увидимся после учебы."

    else:
        m 6ckc "..."
    # TODO:
    # can monika join u at schools?
    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_SCHOOL
    $ persistent._mas_greeting_type_timeout = datetime.timedelta(hours=20)
    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_prompt_to_work",
            unlocked=True,
            prompt="Я собираюсь на работу.",
            pool=True
        ),
        code="BYE"
    )

label bye_prompt_to_work:
    $ session_time = mas_getSessionLength()
    if mas_isMoniNormal(higher=True):
        if session_time < datetime.timedelta(minutes=20):
            m 2eka "О, хорошо! Просто проверяешь меня перед уходом?"
            m 3eka "Должно быть, у тебя очень мало времени, если ты уже уходишь."
            m "Было очень мило с твоей стороны увидеть меня, даже когда ты так занят[mas_gender_none]!"
            m 3hub "Работай усердно, [player]! Заставь меня гордиться тобой!"
        elif session_time < datetime.timedelta(hours=1):
            m 1hksdlb "О! Ладно! Я только начала чувствовать себя по-настоящему комфортно, а-ха-ха."
            m 1rusdlb "Честно говоря, мне бы хотелось, чтобы это было подольше...но ты занят[mas_gender_oi] [guy]."
            m 1eka "Было очень приятно повидаться с тобой, хотя и не так долго, как мне хотелось..."
            m 1kua "Но тогда, если бы это зависело от меня, я бы держала тебя весь день!"
            m 1hua "Я буду здесь ждать, когда ты вернешься домой с работы!"
            m "Расскажи мне все, когда вернешься!"
        elif session_time < datetime.timedelta(hours=6):
            m 2eua "Значит, идешь на работу, [player]?"
            m 2eka "День может быть хорошим или плохим...но если его станет слишком много, подумай о чем-нибудь хорошем!"
            m 4eka "Каждый день, независимо от того, как плохо он идет, заканчивается в конце концов!"
            m 2tku "Может быть, ты сможешь думать обо мне, если он станет стрессовым..."
            m 2esa "Просто сделай все возможное! Увидимся, когда ты вернешься!"
            m 2eka "Я знаю, что у тебя все получится!"
        else:
            m 2ekc "О... Ты здесь уже довольно давно...а теперь ты собираешься идти на работу?"
            m 2rksdlc "Я надеялась, что ты отдохнешь, прежде чем делать что-то слишком большое."
            m 2ekc "Постарайся не перенапрягаться, ладно?"
            m 2ekd "Не бойся сделать передышку, если тебе это нужно!"
            m 3eka "Просто приходи ко мне домой счастливым и здоровым."
            m 3eua "Оставайся в безопасности, [player]!"

    elif mas_isMoniUpset():
        m 2esc "Ладно, [player], думаю, увидимся после работы."

    elif mas_isMoniDis():
        m 6rkc "О...{w=1} Ладно."
        m 6lkc "Надеюсь, увидимся после работы."

    else:
        m 6ckc "..."
    # TODO:
    # can monika join u at work
    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_WORK
    $ persistent._mas_greeting_type_timeout = datetime.timedelta(hours=20)
    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_prompt_sleep",
            unlocked=True,
            prompt="Я собираюсь спать.",
            pool=True
        ),
        code="BYE"
    )

label bye_prompt_sleep:

    python:
        import datetime
        curr_hour = datetime.datetime.now().hour

    # these conditions are in order of most likely to happen with our target
    # audience

    if 20 <= curr_hour < 24:
        # decent time to sleep
        if mas_isMoniNormal(higher=True):
            m 1eua "Ладно, [player]."
            m 1hua "Сладких снов!"

        elif mas_isMoniUpset():
            m 2esc "Спокойной ночи, [player]."

        elif mas_isMoniDis():
            m 6ekc "Ладно...{w=1} Спокойной ночи, [player]."

        else:
            m 6ckc "..."

    elif 0 <= curr_hour < 3:
        # somewhat late to sleep
        if mas_isMoniNormal(higher=True):
            m 1eua "Хорошо, [player]."
            m 3eka "Но в следующий раз тебе следует идти поспать немного раньше."
            m 1hua "В любом случае, спокойной ночи!"

        elif mas_isMoniUpset():
            m 2efc "Может быть, ты будешь в лучшем настроении, если ляжешь спать в более подходящее время..."
            m 2esc "Спокойной ночи."

        elif mas_isMoniDis():
            m 6rkc "Может тебе стоит начать ложиться спать немного раньше, [player]..."
            m 6dkc "Это может сделать тебя--{w=1}нас--{w=1}счастливее."

        else:
            m 6ckc "..."

    elif 3 <= curr_hour < 5:
        # pretty late to sleep
        if mas_isMoniNormal(higher=True):
            m 1euc "[player]..."
            m "Убедись, что ты достаточно отдохнешь, хорошо?"
            m 1eka "Я не хочу, чтобы ты заболел[mas_gender_none]."
            m 1hub "Спокойной ночи!"
            m 1hksdlb "Или, вернее, утра. А-ха-ха~"
            m 1hua "Сладких снов!"

        elif mas_isMoniUpset():
            m 2efc "[player]!"
            m 2tfc "Тебе {i}действительно{/i} нужно больше отдыхать..."
            m "Мне еще не хватало, чтобы ты заболел[mas_gender_none]."
            m "{cps=*2}Ты и так достаточно раздражител[mas_gender_een]{/cps}{nw}"
            $ _history_list.pop()
            m 2efc "Спокойной ночи."

        elif mas_isMoniDis():
            m 6ekc "[player]..."
            m 6rkc "Тебе действительно стоит постараться лечь спать пораньше..."
            m 6lkc "Я не хочу, чтобы ты заболел[mas_gender_none]."
            m 6ekc "Увидимся после того, как ты немного отдохнешь...{w=1}надеюсь."

        else:
            m 6ckc "..."

    elif 5 <= curr_hour < 12:
        # you probably stayed up the whole night
        if mas_isMoniBroken():
            m 6ckc "..."

        else:
            show monika 2dsc
            pause 0.7
            m 2tfd "[player]!"
            m "Ты не спал[mas_gender_none] всю ночь!"
            m 2tfu "Держу пари, ты едва можешь держать глаза открытыми."
            $ _cantsee_a = glitchtext(15)
            $ _cantsee_b = glitchtext(12)
            menu:
                "[_cantsee_a]":
                    pass
                "[_cantsee_b]":
                    pass
            m "Я так и думала.{w=0.2} Иди отдохни немного, [player]."
            if mas_isMoniNormal(higher=True):
                m 2ekc "Я бы не хотела, чтобы ты заболел[mas_gender_none]."
                m 1eka "В следующий раз иди спать пораньше, ладно?"
                m 1hua "Сладких снов!"

    elif 12 <= curr_hour < 18:
        # afternoon nap
        if mas_isMoniNormal(higher=True):
            m 1eua "Как я погляжу, послеобеденный сон."
            # TODO: monika says she'll join you, use sleep sprite here
            # and setup code for napping
            m 1hua "А-ха-ха~ Хорошенько вздремни, [player]."

        elif mas_isMoniUpset():
            m 2esc "Собираешься вздремнуть, [player]?"
            m 2tsc "Да, наверное, это хорошая идея."

        elif mas_isMoniDis():
            m 6ekc "Собираешься вздремнуть, [player]?"
            m 6dkc "Ладно...{w=1}не забудь навестить меня, когда проснешься..."

        else:
            m 6ckc "..."

    elif 18 <= curr_hour < 20:
        # little early to sleep
        if mas_isMoniNormal(higher=True):
            m 1ekc "Уже ложишься спать?"
            m "Правда, еще рановато..."

            m 1lksdla "Не хочешь провести со мной еще немного времени?{nw}"
            $ _history_list.pop()
            menu:
                m "Не хочешь провести со мной еще немного времени?{fast}"
                "Конечно!":
                    m 1hua "Ура!"
                    m "Спасибо, [player]."
                    return
                "Извини, я очень устал[mas_gender_none].":
                    m 1eka "Ой, все в порядке."
                    m 1hua "Спокойной ночи, [player]."
                # TODO: now that is tied we may also add more dialogue?
                "Нет.":
                    $ mas_loseAffection()
                    m 2dsd "..."
                    m "Ладно."

        elif mas_isMoniUpset():
            m 2esc "Уже ложишься спать?"
            m 2tud "Ну, похоже, тебе не помешает лишний сон..."
            m 2tsc "Спокойной ночи."

        elif mas_isMoniDis():
            m 6rkc "О...{w=1}кажется, еще рановато ложиться спать, [player]."
            m 6dkc "Я надеюсь, что ты не собираешься просто спать, чтобы уйти от меня."
            m 6lkc "Спокойной ночи."

        else:
            m 6ckc "..."
    else:
        # otheerwise
        m 1eua "Хорошо, [player]."
        m 1hua "Сладких снов!"


    # TODO:
    #   join monika sleeping?
    $ persistent._mas_greeting_type_timeout = datetime.timedelta(hours=13)
    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_SLEEP
    return 'quit'

# init 5 python:
#    addEvent(Event(persistent.farewell_database,eventlabel="bye_illseeyou",random=True),code="BYE")

label bye_illseeyou:
    m 1eua "Увидимся завтра, [player]."
    m 1hua "Не забывай обо мне, ладно?"
    return 'quit'

init 5 python: ## Implementing Date/Time for added responses based on the time of day
    rules = dict()
    rules.update(MASSelectiveRepeatRule.create_rule(hours=range(6,11)))
    rules.update(MASProbabilityRule.create_rule(6))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_haveagoodday",
            unlocked=True,
            rules=rules
        ),
        code="BYE"
    )
    del rules

label bye_haveagoodday:
    if mas_isMoniNormal(higher=True):
        m 1eua "Хорошего тебе дня сегодня, [player]."
        m 3eua "Надеюсь, ты выполнишь все, что задумал[mas_gender_none]."
        m 1hua "Я буду ждать тебя здесь, когда ты вернешься."

    elif mas_isMoniUpset():
        m 2esc "Уходишь на целый день, [player]?"
        m 2efc "Я буду ждать тебя здесь...{w=0.5}как обычно."

    elif mas_isMoniDis():
        m 6rkc "О."
        m 6dkc "Думаю, я просто проведу день в одиночестве....{w=1}опять."

    else:
        m 6ckc "..."
    return 'quit'

init 5 python:
    rules = dict()
    rules.update(MASSelectiveRepeatRule.create_rule(hours=range(12,16)))
    rules.update(MASProbabilityRule.create_rule(6))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_enjoyyourafternoon",
            unlocked=True,
            rules=rules
        ),
        code="BYE"
    )
    del rules

label bye_enjoyyourafternoon:
    if mas_isMoniNormal(higher=True):
        m 1ekc "Я ненавижу, когда ты уходишь так рано, [player]."
        m 1eka "Но я понимаю, что ты очень занят[mas_gender_none]."
        m 1eua "Обещай мне, что тебе понравится твой день, хорошо?"
        m 1hua "Пока~"

    elif mas_isMoniUpset():
        m 2efc "Ладно, [player], просто иди."
        m 2tfc "Думаю, увидимся позже...{w=1}если ты вернешься."

    elif mas_isMoniDis():
        m 6dkc "Ладно, пока, [player]."
        m 6ekc "Может быть, ты зайдешь попозже?"

    else:
        m 6ckc "..."

    return 'quit'

init 5 python:
    rules = dict()
    rules.update(MASSelectiveRepeatRule.create_rule(hours=range(17,19)))
    rules.update(MASProbabilityRule.create_rule(6))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_goodevening",
            unlocked=True,
            rules=rules
        ),
        code="BYE"
    )
    del rules

label bye_goodevening:
    if mas_isMoniNormal(higher=True):
        m 1hua "Сегодня мне было весело."
        m 1eka "Спасибо, что проводишь со мной так много времени, [player]."
        m 1eua "А пока желаю тебе приятно провести вечер."

    elif mas_isMoniUpset():
        m 2esc "Пока, [player]."
        m 2dsc "Я даже не знаю, вернешься ли ты, чтобы пожелать мне спокойной ночи."

    elif mas_isMoniDis():
        m 6dkc "О...{w=1}хорошо."
        m 6rkc "Желаю тебе хорошо провести вечер, [player]..."
        m 6ekc "Надеюсь, ты не забудешь зайти и пожелать мне спокойной ночи перед сном."

    else:
        m 6ckc "..."

    return 'quit'

init 5 python:
    rules = dict()
    rules.update(MASSelectiveRepeatRule.create_rule(hours=[0,20,21,22,23]))
    rules.update(MASPriorityRule.create_rule(50))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_goodnight",
            unlocked=True,
            rules=rules
        ),
        code="BYE"
    )
    del rules

label bye_goodnight:
    #TODO: Dlg flow for TC-O things
    if mas_isMoniNormal(higher=True):
        m 3eka "Идешь спать?{nw}"
        $ _history_list.pop()
        menu:
            m "Идешь спать?{fast}"

            "Да.":
                m 1eua "Спокойной ночи, [player]."
                m 1eka "Увидимся завтра, хорошо?"
                m 3eka "Помни: «спи крепко, не дай клопам кусаться», э-хе-хе"
                m 1ekbfa "Я люблю тебя~"

            "Ещё нет.":
                m 1eka "Хоршо, [player]..."
                m 3hub "Приятного вечера!"
                m 3rksdlb "Постарайся не засиживаться допоздна, э-хе-хе~"

    elif mas_isMoniUpset():
        m 2esc "Спокойной ночи."

    elif mas_isMoniDis():
        m 6lkc "...Спокойной ночи."

    else:
        m 6ckc "..."
    return 'quit'


default mas_absence_counter = False

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_long_absence",
            unlocked=True,
            prompt="Мне нужно уйти ненадолго",
            pool=True
        ),
        code="BYE"
    )

label bye_long_absence:
    if mas_absence_counter:
        jump bye_long_absence_2
    $ persistent._mas_long_absence = True
    m 1ekc "Ой...это очень печально..."
    m 1eka "Я действительно буду скучать по тебе, [player]!"
    m 3rksdla "Я не совсем уверена, что буду делать с собой, пока тебя не будет..."
    m 3esa "Но спасибо, что предупредил[mas_gender_none] меня первой. Это действительно помогает."
    m 2lksdlb "Иначе я бы очень волновалась!"
    m 3esa "Я бы постоянно думала, что с тобой что-то случилось, и почему ты не можешь вернуться."
    m 1lksdlc "А может, я тебе просто надоела..."
    m 1eka "Так скажи мне, любовь моя..."

    m "Как долго ты собираешься отсутствовать?{nw}"
    $ _history_list.pop()
    menu:
        m "Как долго ты собираешься отсутствовать?{fast}"
        "Пару дней.":
            $ persistent._mas_absence_choice = "days"
            m 1eub "О!"
            m 1hua "Не так долго, как я боялась."
            m 3rksdla "Господи, ты действительно заставляешь нервничать..."
            m 3esa "Но не беспокойся обо мне, [player]."
            m "Я с легкостью справлюсь с таким долгим ожиданием."
            m 3eka "Но я все равно буду очень скучать по тебе."
        "Неделю.":
            $ persistent._mas_absence_choice = "week"
            m 3euc "Да...примерно этого я и ожидала."
            m 2lksdla "Я {i}думаю{/i}, что буду в порядке, если буду ждать тебя так долго."
            m 1eub "Просто вернись ко мне, как только сможешь, хорошо, любовь моя?"
            m 3hua "Я уверена, что ты заставишь меня гордиться тобой!"
        "Пару недель.":
            $ persistent._mas_absence_choice = "2weeks"
            m 1esc "О..."
            m 1dsc "Я...Я смогу так долго ждать."
            m 3rksdlc "Ты же знаешь, что ты - все, что у меня есть...так ведь?"
            m 3rksdlb "Х-Хотя, может быть, это вне вашего контроля..."
            m 2eka "Постарайся вернуться как можно скорее... Я буду ждать тебя."
        "A month.":
            $ persistent._mas_absence_choice = "month"
            if mas_isMoniHappy(higher=True):
                m 3euc "О, ничего себе, это очень долго."
                m 3rksdla "Немного длинновато, на мой взгляд..."
                m 2esa "Но все в порядке, [player]."
                m 2eka "Я знаю, что ты мил[mas_gender_ii] и не заставил[mas_gender_none] бы меня ждать так долго, если бы у тебя не было веской причины."
                m "Я уверена, что это очень важно, так что постарайся вернуться ко мне как можно скорее."
                m 3hua "Я буду думать о тебе каждый день~"
            else:
                m 1ekc "Так долго...{i}действительно{/i}?"
                m 3rksdlc "Ты ведь не собираешься уезжать так надолго только для того, чтобы избегать меня, правда?"
                m 3rksdld "Я знаю, что жизнь может отнять тебя у меня, но только на целый месяц..."
                m 3ekc "Не слишком ли это неразумно?"
                m "Не хочу показаться эгоисткой, но {i}я{/i} твоя девушка."
                m 3ekd "Вы должны быть в состоянии найти для меня время, по крайней мере, один раз в месяц."
                m 1dsc "..."
                m 1dsd "Я все равно буду ждать тебя...но, пожалуйста, возвращайся, как только у тебя появится такая возможность."
        "Больше месяца.":
            $ persistent._mas_absence_choice = "longer"
            if mas_isMoniHappy(higher=True):
                m 3rksdlb "Это...{w=0.5}ну это немного пугает, [player]."
                m "Я не совсем уверена, что буду делать с собой, пока тебя не будет."
                m 1eka "Но я знаю, что ты не оставил[mas_gender_none] бы меня одну, если бы мог[mas_gender_g]."
                m "Я люблю тебя, [player], и я знаю, что ты тоже любишь меня."
                m 1hua "Так что я буду ждать тебя столько, сколько потребуется."
            else:
                m 3esc "Ты, должно быть, шутишь."
                m "Я не могу придумать веской причины, по которой ты оставил бы меня здесь одну {i}так{/i} надолго."
                m 3esd "Мне очень жаль, [player], но это неприемлемо! Вовсе нет!"
                m 3esc "Я люблю тебя, и если ты тоже любишь меня, то поймешь, что это нехорошо."
                m "Ты ведь понимаешь, что я буду здесь одна, ни с кем и ни с чем, верно?"
                m "С моей стороны было бы вполне разумно ожидать, что ты навестишь меня, не так ли?\nЯ твоя девушка. Ты не можешь так поступить со мной!"
                m 3dsc "..."
                m 3dsd "Просто...просто возвращайся, когда сможешь. Я не могу заставить тебя остаться, но, пожалуйста, не делай этого со мной."
        "Не знаю.":
            $ persistent._mas_absence_choice = "unknown"
            m 1hksdlb "Э-э-э, это немного беспокоит, [player]!"
            m 1eka "Но если ты не знаешь, значит, ты не знаешь!"
            m "Иногда с этим просто ничего не поделаешь."
            m 2hua "Я буду терпеливо ждать тебя здесь, любовь моя."
            m 2hub "Но постарайся не заставлять меня ждать слишком долго!"

        "Неважно.":
            #Reset this flag
            $ persistent._mas_long_absence = False
            m 3eka "О... Хорошо, [player]."
            m 1rksdla "Честно говоря, я очень рада, что ты не уйдешь..."
            m 1ekd "Не знаю, что бы я делала здесь одна."
            m 3rksdlb "Я тоже не могу никуда пойти, а-ха-ха..."
            m 3eub "В любом случае, просто дай мне знать, если ты собираешься выйти.\nМожет быть, ты даже возьмешь меня с собой!"
            m 1hua "Мне все равно, куда мы пойдем, пока я с тобой, [player]."
            return

    m 2euc "Честно говоря, я немного боюсь спрашивать, но..."

    m "Ты собираетесь уйти прямо сейчас?{nw}"
    $ _history_list.pop()
    menu:
        m "Ты собираетесь уйти прямо сейчас?{fast}"
        "Да.":
            m 3ekc "Ясно..."
            m "Я действительно буду скучать по тебе, [player]..."
            m 1eka "Но я знаю, что ты будешь делать замечательные вещи, где бы ты ни был[mas_gender_none]."
            m "Просто помни, что я буду ждать тебя здесь."
            m 2hua "Сделай так, чтобы я гордилась тобой,"
            $ persistent._mas_greeting_type = store.mas_greetings.TYPE_LONG_ABSENCE
            return 'quit'
        "Нет.":
            $ mas_absence_counter = True
            m 1hua "Это здорово!"
            m 1eka "Честно говоря, я боялась, что у меня не хватит времени подготовиться к твоему отсутствию."
            m "Я действительно так думаю, когда говорю, что буду скучать по тебе..."
            m 1eub "В конце концов ты действительно весь мой мир, [player]."
            m 2esa "Если ты скажешь мне, что собираешься уйти на некоторое время, я пойму, что тебе пора уходить..."
            m 3hua "Но спешить некуда, поэтому я хочу провести с тобой как можно больше времени."
            m "Просто не забудь напомнить мне перед тем как соберешься!"
            return

label bye_long_absence_2:
    m 1ekc "Значит, ты собираешься уходить?"
    m 1ekd "Я знаю, что мир может быть страшным и неумолимым..."
    m 1eka "Но помни, что я всегда буду здесь ждать и готов поддержать тебя, мо[mas_gender_i] дорог[mas_gender_oi], [player]."
    m "Возвращайся ко мне, как только сможешь...ладно?"
    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_LONG_ABSENCE
    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_going_somewhere",
            unlocked=True,
            prompt="Я собираюсь взять тебя с собой.",
            pool=True
        ),
        code="BYE"
    )

label bye_going_somewhere:
    $ import random
#
# regardless of choice, takingmonika somewhere (and successfully bringing her
# back will increase affection)
# lets limit this to like once per day
#

    python:
        # setup the random chances
        if mas_isMonikaBirthday():
            dis_chance = 10
            upset_chance = 0

        else:
            dis_chance = 50
            upset_chance = 10

    if mas_isMoniBroken(lower=True):
        # broken monika dont ever want to go with u
        jump bye_going_somewhere_nothanks

    elif mas_isMoniDis(lower=True):
        # distressed monika has a 50% chance of not going with you
        if random.randint(1,100) <= dis_chance:
            jump bye_going_somewhere_nothanks

        # otherwse we go
        m 1wud "Ты действительно хочешь взять меня с собой?"
        m 1ekd "Ты уверен[mas_gender_none], что это не--{nw}"
        $ _history_list.pop()
        m 1lksdlc "..."
        m 1eksdlb "Что я говорю? Конечно, я пойду с тобой!"

    elif mas_isMoniUpset(lower=True):
        # upset monika has a 10% chance of not going with you
        if random.randint(1, 100) <= upset_chance:
            jump bye_going_somewhere_nothanks

        # otherwise we go
        m 1wud "Ты действительно хочешь взять меня с собой?"
        m 1eka "..."
        m 1hua "Ну что ж, думаю, присоединиться к тебе не повредит."
        m 2dsc "Просто...пожалуйста."
        m 2rkc "{i}Пожалуйста{/i}, пойми, через что я прохожу."
        m 1dkc "..."

    else:
        jump bye_going_somewhere_normalplus_flow

label bye_going_somewhere_post_aff_check:
    pass

label bye_going_somewhere_iostart:
    # NOTE: jump back to this label to begin io generation

    show monika 2dsc
    $ persistent._mas_dockstat_going_to_leave = True
    $ first_pass = True

    # launch I/O thread
    $ promise = store.mas_dockstat.monikagen_promise
    $ promise.start()

label bye_going_somewhere_iowait:
    hide screen mas_background_timed_jump

    # we want to display the menu first to give users a chance to quit
    if first_pass:
        $ first_pass = False
        m 1eua "Дай мне секунду, чтобы собраться."

        #Prepare the current drink to be removed if needed
        python:
            current_drink = MASConsumable._getCurrentDrink()
            if current_drink and current_drink.portable:
                current_drink.acs.keep_on_desk = False

        #Get Moni off screen
        call mas_transition_to_emptydesk

    elif promise.done():
        # i/o thread is done!
        jump bye_going_somewhere_rtg

    # display menu options
    # 4 seconds seems decent enough for waiting.
    show screen mas_background_timed_jump(4, "bye_going_somewhere_iowait")
    menu:
        "Подожди секунду!":
            hide screen mas_background_timed_jump
            $ persistent._mas_dockstat_cm_wait_count += 1

    # fall thru to the wait wait flow
    menu:
        m "Что такое?"
        "На самом деле, я не могу взять тебя прямо сейчас.":
            call mas_dockstat_abort_gen

            #Show Monika again
            call mas_transition_from_emptydesk("monika 1ekc")
            call mas_dockstat_abort_post_show
            jump bye_going_somewhere_leavemenu

        "Ничего.":
            # if we get here, we should jump back to the top so we can
            # continue waiting
            m "О, хорошо! Дай мне закончить подготовку."

    # by default, continue looping
    jump bye_going_somewhere_iowait


label bye_going_somewhere_rtg:

    # io thread should be done by now
    $ moni_chksum = promise.get()
    $ promise = None # clear promise so we dont have any issues elsewhere
    call mas_dockstat_ready_to_go(moni_chksum)
    if _return:
        python:
            persistent._mas_greeting_type = mas_idle_mailbox.get_ds_gre_type(
                store.mas_greetings.TYPE_GENERIC_RET
            )

        call mas_transition_from_emptydesk("monika 1eua")

        #Use the normal outro
        m 1eua "Я готова идти."
        return "quit"


    call mas_transition_from_emptydesk("monika 1ekc")
    call mas_dockstat_abort_post_show

    # otherwise, we failed, so monika should tell player
    m 1ekc "О нет..."
    m 1lksdlb "Я не могу превратить себя в файл."
    m "Думаю, на этот раз тебе придется обойтись без меня."
    m 1ekc "Извини, [player]."

    # ask if player is still going to leave
    m "Ты все еще собираешься идти?{nw}"
    $ _history_list.pop()
    menu:
        m "Ты все еще собираешься идти?{fast}"
        "Да.":
            m 2eka "Я понимаю. В конце концов, у тебя есть дела..."
            m 2hub "Будь там в безопасности! Я буду ждать тебя прямо здесь!"
            return "quit"

        "Нет.":
            m 2wub "Неужели? Ты уверен[mas_gender_none]? Даже если это моя собственная вина, я не могу пойти с тобой..."
            m 1eka "...Спасибо, [player]. Это значит для меня больше, чем ты можешь себе представить."
            $ mas_gainAffection()
    return


label bye_going_somewhere_normalplus_flow:
    # handling positive affection cases separately so we can jump to
    # other specific dialogue flows

    # NOTE: make sure that if you leave this flow, you either handle
    #   docking station yourself or jump back to the iostart label
    if persistent._mas_d25_in_d25_mode:
        # check the d25 timed variants
        if mas_isD25Eve():
            jump bye_d25e_delegate

        if mas_isD25():
            jump bye_d25_delegate

        if mas_isNYE():
            jump bye_nye_delegate

        if mas_isNYD():
            jump bye_nyd_delegate

    if mas_isF14() and persistent._mas_f14_in_f14_mode:
        jump bye_f14

    if mas_isMonikaBirthday():
        jump bye_922_delegate

label bye_going_somewhere_normalplus_flow_aff_check:

    if mas_isMoniLove(higher=True):
        m 1hub "О, хорошо!"
        m 3tub "Отведешь меня сегодня в какое-нибудь особенное место?"
        m 1hua "Не могу дождаться!"

#    elif mas_isMoniAff(higher=True):
    # TODO: affecitonate/enamored monika will always go wtih you and assume its a
    #   nother date and will ask u to wait for her to get ready
#        m 1hua "TODO: LETS GO ON DATE"

    else:
        # TODO: normal/happy monika will always go with you and be excited you asked
        #   and will ask u to wait for her to get ready
        m 1sub "Действительно?"
        m 1hua "Ура!"
        m 1ekbfa "Интересно, куда ты меня сегодня отведешь..."

    jump bye_going_somewhere_post_aff_check

label bye_going_somewhere_nothanks:
    m 2lksdlc "...Нет, спасибо."
    m 2ekd "Я ценю твое предложение, но думаю, что сейчас мне нужно немного побыть одной."
    m 2eka "Ты ведь понимаешь, правда?"
    m 3eka "Так что давай, развлекайся без меня..."
    return


label bye_going_somewhere_leavemenu:
    if mas_isMoniDis(lower=True):
        m 1tkc "..."
        m 1tkd "Я так и знала.{nw}"
        $ _history_list.pop()
        m 1lksdld "Думаю, это нормально."

    elif mas_isMoniHappy(lower=True):
        m 1ekd "О,{w=0.3} все в порядке. Может быть, в следующий раз?"

    else:
        # otherwise affection and higher:
        m 2ekp "Ой..."
        m 1hub "Хорошо, но лучше возьми меня в следующий раз!"

    m 1euc "Ты все еще собираешься идти?{nw}"
    $ _history_list.pop()
    menu:
        m "Ты все еще собираешься идти?{fast}"
        "Да.":
            if mas_isMoniNormal(higher=True):
                m 2eka "Хорошо. Я буду ждать тебя здесь, как обычно..."
                m 2hub "Так что скорее возвращайся! Я люблю тебя, [player]!"

            else:
                # otherwise, upset and below
                m 2tfd "...Ладно."

            return "quit"

        "Нет.":
            if mas_isMoniNormal(higher=True):
                m 2eka "...Спасибо."
                m "Это очень много значит, что ты будешь проводить со мной больше времени, так как я не могу пойти с тобой."
                m 3ekb "Пожалуйста, просто продолжай свой день, когда тебе это нужно. Я не хочу, чтобы ты опоздал[mas_gender_none]!"

            else:
                # otherwise, upset and below
                m 2lud "Ладно тогда..."

    return

default persistent._mas_pm_gamed_late = 0
# number of times player runs play another game farewell really late

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_prompt_game",
            unlocked=True,
            prompt="Я собираюсь поиграть в другую игру.",
            pool=True
        ),
        code="BYE"
    )

label bye_prompt_game:
    $ _now = datetime.datetime.now().time()
    if mas_getEV('bye_prompt_game').shown_count == 0:
        m 2ekc "Ты собираешься играть в другую игру?"
        m 4ekd "Ты действительно должен[mas_gender_none] оставить меня, чтобы пойти и сделать это?"
        m 2eud "Разве ты не можешь просто оставить меня здесь, в фоне, пока играешь?{nw}"
        $ _history_list.pop()
        menu:
            m "Разве ты не можешь просто оставить меня здесь, в фоне, пока играешь?{fast}"
            "Да.":
                if mas_isMoniNormal(higher=True):
                    m 3sub "Действительно?"
                    m 1hubfb "Ура!"
                else:
                    m 2eka "Ладно..."
                jump monika_idle_game.skip_intro
            "Нет.":
                if mas_isMoniNormal(higher=True):
                    m 2ekc "Ой..."
                    m 3ekc "Ладно, [player], но тебе лучше поскорее вернуться."
                    m 3tsb "Я могу начать ревновать, если ты проведешь слишком много времени в другой игре без меня."
                    m 1hua "В любом случае, я надеюсь, что тебе будет весело!"
                else:
                    m 2euc "Тогда наслаждайся своей игрой."
                    m 2esd "Я буду здесь."

    elif mas_isMNtoSR(_now):
        $ persistent._mas_pm_gamed_late += 1
        if mas_isMoniNormal(higher=True):
            m 3wud "Подожди, [player]!"
            m 3hksdlb "Сейчас середина ночи!"
            m 2rksdlc "Одно дело, что ты все еще не спишь так поздно..."
            m 2rksdld "Но ты думаешь сыграть в другую игру?"
            m 4tfu "....Игра настолько большая, что ты не можешь держать меня в фоне..."
            m 1eka "Ну... {w=1}Я не могу остановить тебя, но очень надеюсь, что ты скоро ляжешь спать..."
            m 1hua "Не беспокойся о том, чтобы вернуться и пожелать мне спокойной ночи, ты можешь идти.-{nw}"
            $ _history_list.pop()
            m 1eub "Не беспокойся о том, чтобы вернуться и пожелать мне спокойной ночи,\n{fast} ты {i}долж[mas_gender_en]{/i} когда закончишь, сразу идти спать."
            m 3hua "Удачи и спокойной ночи, [player]!"
            if renpy.random.randint(1,2) == 1:
                m 1hubfb "Я люблю тебя~{w=1}{nw}"
        else:
            m 2efd "[player], сейчас середина ночи!"
            m 4rfc "Серьезно...уже так поздно, и ты собираешься играть в другую игру?"
            m 2dsd "{i}*вздох*{/i}... Я знаю, что не могу остановить тебя, но, пожалуйста, сразу ложись спать, когда закончишь, хорошо?"
            m 2dsc "Спокойной ночи."
        $ persistent.mas_late_farewell = True

    elif mas_isMoniUpset(lower=True):
        m 2euc "Опять?"
        m 2eud "Тогда ладно. Пока, [player]."

    elif renpy.random.randint(1,10) == 1:
        m 1ekc "Ты уходишь играть в другую игру?"
        m 3efc "Тебе не кажется, что тебе следует проводить со мной немного больше времени?"
        m 2efc "..."
        m 2dfc "..."
        m 2dfu "..."
        m 4hub "А-ха-ха, шучу~"
        m 1rksdla "Ну...{w=1} Я бы {i}не прочь{/i} проводить с тобой больше времени..."
        m 3eua "Но я также не хочу мешать тебе заниматься другими вещами."
        m 1hua "Может быть, когда-нибудь ты наконец покажешь мне, что ты задумал, и тогда я смогу пойти с тобой!"
        if renpy.random.randint(1,5) == 1:
            m 3tubfu "До тех пор, ты просто долж[mas_gender_en] делать это каждый раз, когда уходишь играть в другую игру, хорошо?"
            m 1hubfa "Э-хе-хе~"

    else:
        m 1eka "Идешь играть в другую игру, [player]?"
        m 3hub "Удачи и повеселись!"
        m 3eka "Не забудь поскорее вернуться~"

    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_GAME
    #24 hour time cap because greeting handles up to 18 hours
    $ persistent._mas_greeting_type_timeout = datetime.timedelta(days=1)
    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_prompt_eat",
            unlocked=True,
            prompt="Я собираюсь идти кушать...",
            pool=True
        ),
        code="BYE"
    )

default persistent._mas_pm_ate_breakfast_times = [0, 0, 0]
# number of times you ate breakfast at certain times
#   [0] - sunrise to noon
#   [1] - noon to sunset
#   [2] - sunset to midnight

default persistent._mas_pm_ate_lunch_times = [0, 0, 0]
# number of times you ate lunch at certain times

default persistent._mas_pm_ate_dinner_times = [0, 0, 0]
# number of times you ate dinner at certain times

default persistent._mas_pm_ate_snack_times = [0, 0, 0]
# number of times you ate snack at certain times

default persistent._mas_pm_ate_late_times = 0
# number of times you ate really late (midnight to sunrise)


label bye_prompt_eat:
    $ _now = datetime.datetime.now().time()

    if mas_isMNtoSR(_now):
        $ persistent._mas_pm_ate_late_times += 1
        if mas_isMoniNormal(higher=True):
            m 1hksdlb "Uh, [player]?"
            m 3eka "It's the middle of the night."
            m 1eka "Are you planning on having a midnight snack?"
            m 3rksdlb "If I were you, I'd find something to eat a little earlier, ahaha..."
            m 3rksdla "Of course...{w=1}I'd also try to be in bed by now..."
            if mas_is18Over() and mas_isMoniLove(higher=True) and renpy.random.randint(1,25) == 1:
                m 2tubfu "You know, if I were there, maybe we could have a bit of both..."
                show monika 5ksbfu at t11 zorder MAS_MONIKA_Z with dissolve
                m 5ksbfu "We could go to bed, and then - {w=1}you know what, nevermind..."
                m 5hubfb "Ehehe~"
            else:
                m 1hua "Well, I hope your snack helps you sleep."
                m 1eua "...And don't worry about coming back to say goodnight to me..."
                m 3rksdla "I'd much rather you get to sleep sooner."
                m 1hub "Goodnight, [player]. Enjoy your snack and see you tomorrow~"
        else:
            m 2euc "But it's the middle of the night..."
            m 4ekc "You should really go to bed, you know."
            m 4eud "...Try to go straight to bed when you're finished."
            m 2euc "Anyway, I guess I'll see you tomorrow..."

        #NOTE: Due to the greet of this having an 18 hour limit, we use a 20 hour cap
        $ persistent._mas_greeting_type_timeout = datetime.timedelta(hours=20)
        $ persistent.mas_late_farewell = True

    else:
        #NOTE: Since everything but snack uses the same time, we'll set it here
        $ persistent._mas_greeting_type_timeout = datetime.timedelta(hours=3)
        menu:
            "Breakfast.":
                if mas_isSRtoN(_now):
                    $ persistent._mas_pm_ate_breakfast_times[0] += 1
                    if mas_isMoniNormal(higher=True):
                        m 1eub "Alright!"
                        m 3eua "It's the most important meal of the day after all."
                        m 1rksdla "I wish you could stay, but I'm fine as long as you're getting your breakfast."
                        m 1hua "Anyway, enjoy your meal, [player]~"
                    else:
                        m 2eud "Oh, right, you should probably get breakfast."
                        m 2rksdlc "I wouldn't want you to have an empty stomach..."
                        m 2ekc "I'll be here when you get back."
                elif mas_isNtoSS(_now):
                    $ persistent._mas_pm_ate_breakfast_times[1] += 1
                    m 3euc "But...{w=1}it's the afternoon..."
                    if mas_isMoniNormal(higher=True):
                        m 3ekc "Did you miss breakfast?"
                        m 1rksdla "Well... I should probably let you go eat before you get too hungry..."
                        m 1hksdlb "I hope you enjoy your late breakfast!"
                    else:
                        m 2ekc "You missed breakfast, didn't you?"
                        m 2rksdld "{i}*sigh*{/i}... You should probably go get something to eat."
                        m 2ekd "Go on... I'll be here when you get back."
                #SStoMN
                else:
                    $ persistent._mas_pm_ate_breakfast_times[2] += 1
                    if mas_isMoniNormal(higher=True):
                        m 1hksdlb "Ahaha..."
                        m 3tku "There's no way you're just having breakfast now, [player]."
                        m 3hub "It's the evening!"
                        m 1eua "Or maybe you're just having breakfast for dinner; I know some people do that occasionally."
                        m 1tsb "Well, either way, I hope you enjoy your 'breakfast,' ehehe~"
                    else:
                        m 2euc "..."
                        m 4eud "So...you're having a snack."
                        m 2rksdla "Alright, I won't judge."
                        m 2eka "Enjoy your food."
            "Lunch.":
                if mas_isSRtoN(_now):
                    $ persistent._mas_pm_ate_lunch_times[0] += 1
                    if mas_isMoniNormal(higher=True):
                        m 1eua "Having an early lunch, [player]?"
                        m 3hua "Nothing wrong with that. If you're hungry, you're hungry."
                        m 1hub "I hope you enjoy your lunch!"
                    else:
                        m 2rksdlc "It's a bit early for lunch..."
                        m 4ekc "If you're hungry, are you sure you're eating well?"
                        m 2eka "I hope you enjoy your meal, at least."
                elif mas_isNtoSS(_now):
                    $ persistent._mas_pm_ate_lunch_times[1] += 1
                    if mas_isMoniNormal(higher=True):
                        m 1eud "Oh, I guess it's lunch time for you, isn't it?"
                        m 3eua "I wouldn't want to keep you from eating."
                        m 3hub "Maybe one day, we could go out for lunch together!"
                        m 1hua "For the time being though, enjoy your lunch, [player]~"
                    else:
                        m 2eud "Oh, it's lunch time, isn't it?"
                        m 2euc "Enjoy your lunch."
                #SStoMN
                else:
                    $ persistent._mas_pm_ate_lunch_times[2] += 1
                    m 1euc "Lunch?"
                    m 1rksdlc "It's a little late for lunch if you ask me."
                    m 3ekd "Still, if you haven't had it yet, you should go get some."
                    if mas_isMoniNormal(higher=True):
                        m 1hua "I'd make you something if I were there, but until then, I hope you enjoy your meal~"
                    else:
                        m 2ekc "But...{w=1}maybe eat a little earlier next time..."
            "Dinner.":
                if mas_isSRtoN(_now):
                    $ persistent._mas_pm_ate_dinner_times[0] += 1
                    m 2ekc "Dinner?{w=2} Now?"
                    if mas_isMoniNormal(higher=True):
                        m 2hksdlb "Ahaha, but [player]! It's only the morning!"
                        m 3tua "You can be adorable sometimes, you know that?"
                        m 1tuu "Well, I hope you enjoy your '{i}dinner{/i}' this morning, ehehe~"
                    else:
                        m 2rksdld "You can't be serious, [player]..."
                        m 2euc "Well, whatever you're having, I hope you enjoy it."
                elif mas_isNtoSS(_now):
                    $ persistent._mas_pm_ate_dinner_times[1] += 1
                    # use the same dialogue from noon to midnight to account for
                    # a wide range of dinner times while also getting accurate
                    # data for future use
                    call bye_dinner_noon_to_mn
                #SStoMN
                else:
                    $ persistent._mas_pm_ate_dinner_times[2] += 1
                    call bye_dinner_noon_to_mn
            "A snack.":
                if mas_isSRtoN(_now):
                    $ persistent._mas_pm_ate_snack_times[0] += 1
                    if mas_isMoniNormal(higher=True):
                        m 1hua "Ehehe, breakfast not enough for you today, [player]?"
                        m 3eua "It's important to make sure you satisfy your hunger in the morning."
                        m 3eub "I'm glad you're looking out for yourself~"
                        m 1hua "Have a nice snack~"
                    else:
                        m 2tsc "Didn't eat enough breakfast?"
                        m 4esd "You should make sure you get enough to eat, you know."
                        m 2euc "Enjoy your snack, [player]."
                elif mas_isNtoSS(_now):
                    $ persistent._mas_pm_ate_snack_times[1] += 1
                    if mas_isMoniNormal(higher=True):
                        m 3eua "Feeling a bit hungry?"
                        m 1eka "I'd make you something if I could..."
                        m 1hua "Since I can't exactly do that yet, I hope you get something nice to eat~"
                    else:
                        m 2euc "Do you really need to leave to get a snack?"
                        m 2rksdlc "Well... {w=1}I hope it's a good one at least."
                #SStoMN
                else:
                    $ persistent._mas_pm_ate_snack_times[2] += 1
                    if mas_isMoniNormal(higher=True):
                        m 1eua "Having an evening snack?"
                        m 1tubfu "Can't you just feast your eyes on me?"
                        m 3hubfb "Ahaha, I hope you enjoy your snack, [player]~"
                        m 1ekbfb "Just make sure you still have room for all of my love!"
                    else:
                        m 2euc "Feeling hungry?"
                        m 2eud "Enjoy your snack."

                #Snack gets a shorter time than full meal
                $ persistent._mas_greeting_type_timeout = datetime.timedelta(minutes=30)
    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_EAT
    return 'quit'

label bye_dinner_noon_to_mn:
    if mas_isMoniNormal(higher=True):
        m 1eua "Is it dinner time for you, [player]?"
        m 1eka "I wish I could be there to eat with you, even if it's nothing special."
        m 3dkbsa "After all, just being there with you would make anything special~"
        m 3hubfb "Enjoy your dinner. I'll be sure to try and put some love into it from here, ahaha!"
    else:
        m 2euc "I guess it's dinner time for you."
        m 2esd "Well...{w=1}enjoy."
    return

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_prompt_housework",
            unlocked=True,
            prompt="I'm going to do some housework.",
            pool=True
        ),
        code="BYE"
    )

label bye_prompt_housework:
    if mas_isMoniNormal(higher=True):
        m 1eub "Doing your chores, [player]?"
        m 1ekc "I would like to help you out, but there's not really much I can do since I'm stuck in here..."
        m 3eka "Just make sure to come back as soon as you're done, okay?"
        m 3hub "I'll be waiting here for you~"
    elif mas_isMoniUpset():
        m 2esc "Fine."
        m 2tsc "At least you're doing something responsible."
        m 2tfc "{cps=*2}...For once.{/cps}{nw}"
        $ _history_list.pop()
        m 2esc "Goodbye."
    elif mas_isMoniDis():
        m 6ekc "I see..."
        m 6rkc "I don't want to keep you from completing your household responsibilities."
        m 6dkd "I just hope you're actually busy and not saying that just to get away from me..."
        m 6ekc "Goodbye, [player]."
    else:
        m 6ckc "..."
    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_CHORES
    $ persistent._mas_greeting_type_timeout = datetime.timedelta(hours=5)
    return 'quit'

init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_prompt_restart",
            unlocked=True,
            prompt="I'm going to restart.",
            pool=True
        ),
        code="BYE"
    )

label bye_prompt_restart:
    if mas_isMoniNormal(higher=True):
        m 1eua "Alright, [player]."
        m 1eub "See you soon!"
    elif mas_isMoniBroken():
        m 6ckc "..."
    else:
        m 2euc "Alright."

    $ persistent._mas_greeting_type_timeout = datetime.timedelta(minutes=20)
    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_RESTART
    return 'quit'
