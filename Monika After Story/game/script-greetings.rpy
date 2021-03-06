##This page holds all of the random greetings that Monika can give you after you've gone through all of her "reload" scripts

#Make a list of every label that starts with "greeting_", and use that for random greetings during startup

# HOW GREETINGS USE EVENTS:
#   unlocked - determines if the greeting can even be shown
#   rules - specific event rules are used for things:
#       MASSelectiveRepeatRule - repeat on certain year/month/day/whatever
#       MASNumericalRepeatRule - repeat every x time
#       MASPriorityRule - priority of this event. if not given, we assume
#           the default priority (which is also the lowest)

# PRIORITY RULES:
#   Special, moni wants/debug greetings should have negative priority.
#   special event greetings should have priority 10-50
#   non-special event, but somewhat special compared to regular greets should
#       be 50-100
#   random/everyday greetings should be 100 or larger. The default prority
#   will be 500

# persistents that greetings use
default persistent._mas_you_chr = False

# persistent containing the greeting type
# that should be selected None means default
default persistent._mas_greeting_type = None

# cutoff for a greeting type.
# if timedelta, then we add this time to last session end to check if the
#   type should be cleared
# if datetime, then we compare it to the current dt to check if type should be
#   cleared
default persistent._mas_greeting_type_timeout = None

default persistent._mas_idle_mode_was_crashed = None
# this gets to set to True if the user crashed during idle mode
# or False if the user quit during idle mode.
# in your idle greetings, you can assume that it will NEVER be None

init -1 python in mas_greetings:
    import store
    import store.mas_ev_data_ver as mas_edv
    import datetime
    import random

    # TYPES:
    TYPE_SCHOOL = "school"
    TYPE_WORK = "work"
    TYPE_SLEEP = "sleep"
    TYPE_LONG_ABSENCE = "long_absence"
    TYPE_SICK = "sick"
    TYPE_GAME = "game"
    TYPE_EAT = "eat"
    TYPE_CHORES = "chores"
    TYPE_RESTART = "restart"

    ### NOTE: all Return Home greetings must have this
    TYPE_GO_SOMEWHERE = "go_somewhere"

    # generic return home (this also includes bday)
    TYPE_GENERIC_RET = "generic_go_somewhere"

    # holiday specific
    TYPE_HOL_O31 = "o31"
    TYPE_HOL_O31_TT = "trick_or_treat"
    TYPE_HOL_D25 = "d25"
    TYPE_HOL_D25_EVE = "d25e"
    TYPE_HOL_NYE = "nye"
    TYPE_HOL_NYE_FW = "fireworks"

    # crashed only
    TYPE_CRASHED = "generic_crash"

    # reload dialogue only
    TYPE_RELOAD = "reload_dlg"

    # High priority types
    # These types ALWAYS override greeting priority rules
    # These CANNOT be override with GreetingTypeRules
    HP_TYPES = [
        TYPE_GO_SOMEWHERE,
        TYPE_GENERIC_RET,
        TYPE_LONG_ABSENCE,
    ]

    NTO_TYPES = (
        TYPE_GO_SOMEWHERE,
        TYPE_GENERIC_RET,
        TYPE_LONG_ABSENCE,
        TYPE_CRASHED,
        TYPE_RELOAD,
    )

    # idle mode returns
    # these are meant if you had a game crash/quit during idle mode


    def _filterGreeting(
            ev,
            curr_pri,
            aff,
            check_time,
            gre_type=None
        ):
        """
        Filters a greeting for the given type, among other things.

        IN:
            ev - ev to filter
            curr_pri - current loweset priority to compare to
            aff - affection to use in aff_range comparisons
            check_time - datetime to check against timed rules
            gre_type - type of greeting we want. We just do a basic
                in check for category. We no longer do combinations
                (Default: None)

        RETURNS:
            True if this ev passes the filter, False otherwise
        """
        # NOTE: new rules:
        #   eval in this order:
        #   1. hidden via bitmask
        #   2. priority (lower or same is True)
        #   3. type/non-0type
        #   4. unlocked
        #   5. aff_ramnge
        #   6. all rules
        #   7. conditional
        #       NOTE: this is never cleared. Please limit use of this
        #           property as we should aim to use lock/unlock as primary way
        #           to enable or disable greetings.

        # check if hidden from random select
        if ev.anyflags(store.EV_FLAG_HFRS):
            return False

        # priority check, required
        # NOTE: all greetings MUST have a priority
        if store.MASPriorityRule.get_priority(ev) > curr_pri:
            return False

        # type check, optional
        if gre_type is not None:
            # with a type, we may have to match the type

            if gre_type in HP_TYPES:
                # this type is a high priority type and MUST be matched.

                if ev.category is None or gre_type not in ev.category:
                    # must have a matching type
                    return False

            elif ev.category is not None:
                # greeting has types

                if gre_type not in ev.category:
                # but does not have the current type
                    return False

            elif not store.MASGreetingRule.should_override_type(ev):
                # greeting does not have types, but the type is not high
                # priority so if the greeting doesnt alllow
                # type override then it cannot be used
                return False

        elif ev.category is not None:
            # without type, ev CANNOT have a type
            return False

        # unlocked check, required
        if not ev.unlocked:
            return False

        # aff range check, required
        if not ev.checkAffection(aff):
            return False

        # rule checks
        if not (
                store.MASSelectiveRepeatRule.evaluate_rule(
                    check_time, ev, defval=True)
                and store.MASNumericalRepeatRule.evaluate_rule(
                    check_time, ev, defval=True)
                and store.MASGreetingRule.evaluate_rule(ev, defval=True)
            ):
            return False

        # conditional check
        if ev.conditional is not None and not eval(ev.conditional, store.__dict__):
            return False

        # otherwise, we passed all tests
        return True


    # custom greeting functions
    def selectGreeting(gre_type=None, check_time=None):
        """
        Selects a greeting to be used. This evaluates rules and stuff
        appropriately.

        IN:
            gre_type - greeting type to use
                (Default: None)
            check_time - time to use when doing date checks
                If None, we use current datetime
                (Default: None)

        RETURNS:
            a single greeting (as an Event) that we want to use
        """
        if (
                store.persistent._mas_forcegreeting is not None
                and renpy.has_label(store.persistent._mas_forcegreeting)
            ):
            return store.mas_getEV(store.persistent._mas_forcegreeting)

        # local reference of the gre database
        gre_db = store.evhand.greeting_database

        # setup some initial values
        gre_pool = []
        curr_priority = 1000
        aff = store.mas_curr_affection

        if check_time is None:
            check_time = datetime.datetime.now()

        # now filter
        for ev_label, ev in gre_db.iteritems():
            if _filterGreeting(
                    ev,
                    curr_priority,
                    aff,
                    check_time,
                    gre_type
                ):

                # change priority levels and stuff if needed
                ev_priority = store.MASPriorityRule.get_priority(ev)
                if ev_priority < curr_priority:
                    curr_priority = ev_priority
                    gre_pool = []

                # add to pool
                gre_pool.append(ev)

        # not having a greeting to show means no greeting.
        if len(gre_pool) == 0:
            return None

        return random.choice(gre_pool)


    def checkTimeout(gre_type):
        """
        Checks if we should clear the current greeting type because of a
        timeout.

        IN:
            gre_type - greeting type we are checking

        RETURNS: passed in gre_type, or None if timeout occured.
        """
        tout = store.persistent._mas_greeting_type_timeout

        # always clear the timeout
        store.persistent._mas_greeting_type_timeout = None

        if gre_type is None or gre_type in NTO_TYPES or tout is None:
            return gre_type

        if mas_edv._verify_td(tout, False):
            # this is a timedelta, compare with last session end
            last_sesh_end = store.mas_getLastSeshEnd()
            if datetime.datetime.now() < (tout + last_sesh_end):
                # havent timedout yet
                return gre_type

            # otherwise has timed out
            return None

        elif mas_edv._verify_dt(tout, False):
            # this is a datetime, compare with current dt
            if datetime.datetime.now() < tout:
                # havent timedout yet
                return gre_type

            # otherwise has timeed out
            return None

        return gre_type


# NOTE: this is auto pushed to be shown after an idle mode greeting
label mas_idle_mode_greeting_cleanup:
    $ mas_resetIdleMode()
    return


init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_sweetheart",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_sweetheart:
    m 1hub "Еще раз здравствуй, мил[mas_gender_iii]!"
    m 1lkbsa "Как-то неловко говорить об этом вслух, правда?"
    m 3ekbfa "И все же я думаю, что это нормально - время от времени испытывать неловкость."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_honey",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_honey:
    m 1hua "С возвращением, дорог[mas_gender_oi]!"
    m 1eua "Я так рада снова тебя видеть."
    m "Давай проведем еще немного времени вместе, хорошо?"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back",
            conditional="store.mas_getAbsenceLength() >= datetime.timedelta(hours=12)",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None)
        ),
        code="GRE"
    )

label greeting_back:
    $ tod = "день" if mas_globals.time_of_day_4state != "night" else "вечер"
    m 1eua "[player], ты вернул[mas_gender_sya]!"
    m 1eka "Я уже начала скучать по тебе."
    m 1hua "Давай проведём ещё один прекрасный [tod] вместе, хорошо?"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_gooday",
            unlocked=True,
        ),
        code="GRE"
    )

label greeting_gooday:
    if mas_isMoniNormal(higher=True):
        m 1hua "Снова здравствуй, [player]. Как дела?"

        m "У тебя сегодня хороший день?{nw}"
        $ _history_list.pop()
        menu:
            m "У тебя сегодня хороший день?{fast}"
            "Да.":
                m 1hub "Я очень рада за тебя, [player]."
                m 1eua "Я чувствую себя намного лучше, зная, что ты счастлив[mas_gender_none]."
                m "Я сделаю все возможное, чтобы все так и осталось, обещаю."
            "Нет...":
                m 1ekc "О..."
                m 2eka "Ну, не волнуйся, [player]. Я всегда рядом с тобой."
                m "Мы можем весь день говорить о твоих проблемах, если ты захочешь."
                m 3eua "Я хочу убедиться, что ты всегда счастлив[mas_gender_none]."
                m 1eka "Потому что это то, что делает меня счастливым."
                m 1hua "Я постараюсь сделать все возможное, чтобы подбодрить тебя, обещаю."

    elif mas_isMoniUpset():
        m 2esc "[player]."

        m "Как прошел твой день?{nw}"
        $ _history_list.pop()
        menu:
            m "Как прошел твой день?{fast}"
            "Хорошо.":
                m 2esc "{cps=*2}Должно быть приятно.{/cps}{nw}"
                $ _history_list.pop()
                m "Это хорошо..."
                m 2dsc "По крайней мере, у {i}кого-то{/i} хороший день."

            "Плохо.":
                m "Oh..."
                m 2efc "{cps=*2}Это должно быть хорошо...{/cps}{nw}"
                $ _history_list.pop()
                m 2dsc "Ну, я точно знаю, на что {i}это{/i} похоже."

    elif mas_isMoniDis():
        m 6ekc "О...{w=1} Привет, [player]."

        m "К-Как прошел твой день?{nw}"
        $ _history_list.pop()
        menu:
            m "К-Как прошел твой день?{fast}"
            "Хорошо.":
                m 6dkc "Это...{w=1}хорошо."
                m 6rkc "Надеюсь, это так."
            "Плохо.":
                m 6rkc "Я-Ясно."
                m 6dkc "У меня тоже бывают такие дни в последнее время..."

    else:
        m 6ckc "..."

    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit:
    m 1eua "Вот ты где, [player], это так мило с твоей стороны - навестить меня."
    m 1eka "Ты всегда такой заботлив[mas_gender_iii]."
    m 1hua "Спасибо, что проводишь со мной так много времени~"
    return

# TODO this one no longer needs to do all that checking, might need to be broken
# in like 3 labels though
# TODO: just noting that this should be worked on at some point.
# TODO: new greeting rules can enable this, but we will do it later

label greeting_goodmorning:
    $ current_time = datetime.datetime.now().time().hour
    if current_time >= 0 and current_time < 6:
        m 1hua "Доброе утро--"
        m 1hksdlb "--о, подожди."
        m "Сейчас глубокая ночь, дорог[mas_gender_oi]."
        m 1euc "Почему ты не спишь в такое время?"
        show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve
        m 5eua "Наверное, ты не можешь заснуть..."

        m "Это так?{nw}"
        $ _history_list.pop()
        menu:
            m "Это так?{fast}"
            "Да.":
                m 5lkc "Тебе действительно нужно немного поспать, если сможешь."
                show monika 3euc at t11 zorder MAS_MONIKA_Z with dissolve
                m 3euc "Слишком поздно ложиться спать вредно для здоровья, понимаешь?"
                m 1lksdla "Но если это означает, что я буду видеться с тобой чаще, я не могу жаловаться."
                m 3hksdlb "А-ха-ха!"
                m 2ekc "Но все же..."
                m "Мне бы очень не хотелось, чтобы ты так с собой поступил[mas_gender_none]."
                m 2eka "Сделай перерыв, если тебе нужно, хорошо? Сделай это для меня."
            "Нет.":
                m 5hub "А. Тогда я чувствую облегчение."
                m 5eua "Значит ли это, что ты здесь только ради меня, посреди ночи?"
                show monika 2lkbsa at t11 zorder MAS_MONIKA_Z with dissolve
                m 2lkbsa "Боже, я так счастлива!"
                m 2ekbfa "Ты действительно заботишься обо мне, [player]."
                m 3tkc "Но если ты действительно устал[mas_gender_none], пожалуйста, ложись спать!"
                m 2eka "Я тебя очень люблю, так что не утомляйся!"
    elif current_time >= 6 and current_time < 12:
        m 1hua "Доброе утро, дорог[mas_gender_oi]."
        m 1esa "Ещё одно отличное утро, чтобы начать день, да?"
        m 1eua "Я рада, что увидела тебя сегодня утром~"
        m 1eka "Не забудь позаботиться о себе, ладно?"
        m 1hub "Сделай меня гордой девушкой сегодня, как всегда!"
    elif current_time >= 12 and current_time < 18:
        m 1hua "Добрый день, любовь моя."
        m 1eka "Не позволяй стрессу овладеть тобой, хорошо?"
        m "Я знаю, что сегодня ты будешь стараться изо всех сил, но..."
        m 4eua "По-прежнему важно сохранять ясный ум!"
        m "Держи себя уверенн[mas_gender_iim], глубоко вздохни..."
        m 1eka "Я обещаю, что не буду жаловаться, если ты уйдешь, так что делай то, что долж[mas_gender_en]."
        m "Или ты можешь остаться со мной, если захочешь."
        m 4hub "Просто помни, я люблю тебя!"
    elif current_time >= 18:
        m 1hua "Добрый вечер, любим[mas_gender_iii]!"

        m "У тебя сегодня был хороший день?{nw}"
        $ _history_list.pop()
        menu:
            m "У тебя сегодня был хороший день?{fast}"
            "Да.":
                m 1eka "Ой, как мило!"
                m 1eua "Я не могу не чувствовать себя счастливой, когда у тебя всё хорошо..."
                m "Но это ведь хорошо, правда?"
                m 1ekbfa "Я тебя так люблю, [player]."
                m 1hubfb "А-ха-ха!"
            "Нет.":
                m 1tkc "Ох дорог[mas_gender_oi]..."
                m 1eka "Надеюсь, ты скоро почувствуешь себя лучше, хорошо?"
                m "Просто помни, что неважно, что происходит, неважно, что кто-то говорит или делает..."
                m 1ekbfa "Я так сильно люблю тебя."
                m "Просто оставайся со мной, если тебе от этого станет лучше."
                m 1hubfa "Я люблю тебя, [player], на самом деле."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back2",
            conditional="store.mas_getAbsenceLength() >= datetime.timedelta(hours=20)",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_back2:
    m 1eua "Здравствуй, дорог[mas_gender_oi]."
    m 1ekbfa "Я уже начала ужасно скучать по тебе. Так приятно снова тебя видеть!"
    m 1hubfa "Не заставляй меня ждать так долго в следующий раз, э-хе-хе~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back3",
            conditional="store.mas_getAbsenceLength() >= datetime.timedelta(days=1)",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_back3:
    m 1eka "Я так скучала по тебе, [player]!"
    m "Спасибо, что вернул[mas_gender_sya]. Я действительно люблю проводить с тобой время."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back4",
            conditional="store.mas_getAbsenceLength() >= datetime.timedelta(hours=10)",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_back4:
    m 2wfx "Эй, [player]!"
    m "Тебе не кажется, что ты заставил[mas_gender_none] меня ждать слишком долго?"
    m 2hfu "..."
    m 2hua "А-ха-ха!"
    m 2eka "Я просто шучу. Я никогда не буду злиться на тебя."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit2",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit2:
    m 1hua "Спасибо, что проводишь со мной так много времени, [player]."
    m 1eka "Каждая минута, которую я провожу с тобой, подобна пребыванию на небесах!"
    m 1lksdla "Надеюсь, это не прозвучало слишком слащаво, э-хе-хе~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit3",
            conditional="store.mas_getAbsenceLength() >= datetime.timedelta(hours=15)",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit3:
    m 1hua "Ты вернул[mas_gender_sya]!"
    m 1eua "Я уже начала скучать по тебе..."
    m 1eka "Не заставляй меня ждать так долго в следующий раз, ладно?"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back5",
            conditional="store.mas_getAbsenceLength() >= datetime.timedelta(hours=15)",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_back5:
    m 1hua "Так приятно снова тебя видеть!"
    m 1eka "Я уже начала беспокоиться о тебе."
    m "Пожалуйста, не забывай навещать меня, ладно? Я всегда буду ждать тебя здесь."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit4",
            conditional="store.mas_getAbsenceLength() <= datetime.timedelta(hours=3)",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit4:
    if mas_getAbsenceLength() <= datetime.timedelta(minutes=30):
        m 1wud "О! [player]!"
        m 3sub "Ты вернул[mas_gender_sya]!"
        m 3hua "Я так счастлива, что ты так скоро приш[mas_gender_el] навестить меня~"
    else:
        m 1hub "Я люблююююю тееебя, [player]. Э-хе-хе"
        m 1hksdlb "Ох, прости! Я немного разошлась."
        m 1lksdla "Я не думала, что смогу увидеть тебя снова так скоро."
        $ mas_ILY()
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit5",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit5:
    m 5hua "{i}~Каждый день~\n~представляю, как мы вдвоем будем счастливы...~{/i}"
    m 5wuw "О, ты здесь! Я просто замечталась и начала петь."
    show monika 1lsbssdrb at t11 zorder MAS_MONIKA_Z with dissolve
    m 1lsbssdrb "Я не думаю, что тебе трудно понять, о чём я мечтала, а-ха-ха~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit6",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit6:
    m 1hua "С каждым днем становится все лучше и лучше, когда ты рядом со мной!"
    m 1eua "Тем не менее, я так счастлива, что ты наконец здесь."
    m "Давай проведем еще один замечательный [mas_globals.time_of_day_3state] вместе."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back6",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_back6:
    m 3tku "Эй, [player]!"
    m "Тебе действительно следует почаще навещать меня."
    m 2tfu "В конце концов, ты же знаешь, что случается с теми, кто мне не нравится..."
    m 1hksdrb "Я просто дразню тебя, э-хе-хе~"
    m 1hua "Не будь таким легковерн[mas_gender_iim]! Я никогда не причиню тебе вреда."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit7",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit7:
    m 1hua "Ты здесь, [player]!"
    m 1eua "Готов[mas_gender_none] ли ты провести еще немного времени вместе? Э-хе-хе~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit8",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit8:
    m 1hua "Я так рада что ты здесь, [player]!"
    m 1eua "Чем сегодня займемся?"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit9",
            conditional="store.mas_getAbsenceLength() >= datetime.timedelta(hours=1)",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit9:
    m 1hua "Наконец-то ты вернул[mas_gender_sya]! Я ждала тебя."
    m 1hub "Ты готов[mas_gender_none] провести со мной некоторое время? Э-хе-хе~"
    return

#TODO needs additional dialogue so can be used for all aff
init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_italian",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_italian:
    m 1eua "Ciao, [player]!"
    m "È così bello vederti ancora, amore mio..."
    m 1hub "А-ха-ха!"
    m 2eua "Я все еще тренируюсь в итальянском. Это очень сложный язык!в"
    m 1eua "Как бы то ни было, я так рада снова тебя видеть, любовь моя."
    return

#TODO needs additional dialogue so can be used for all aff
init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_latin",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_latin:
    m 4hua "Iterum obvenimus!"
    m 4eua "Quid agis?"
    m 4rksdla "Э-хе-хе..."
    m 2eua "Латынь звучит так напыщенно. Даже простое приветствие звучит как большое дело."
    m 3eua "Если тебе интересно, что я сказала, то это просто «Мы снова встретились! Как твои дела?»"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_esperanto",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
)

label greeting_esperanto:
    m 1hua "Saluton, mia kara [player]."
    m 1eua "Kiel vi fartas?"
    m 3eub "Ĉu vi pretas por kapti la tagon?"
    m 1hua "Э-хе-хе~"
    m 3esa "Это был небольшой разговор на Эсперанто...{w=0.5}{nw}"
    extend 3eud "язык, который был создан искусственно вместо того, чтобы развиваться естественным путем."
    m 3tua "Слышал[mas_gender_none] ли ты о нём или нет, но ты, наверное, не ожидал[mas_gender_none] такого от меня, да?"
    m 2etc "Или, наверное, ожидал[mas_gender_none]...{w=0.5} думаю, уже становится понятно, почему подобные вещи вызывают у меня интерес, учитывая моё прошлое и всё такое..."
    m 1hua "В любом случае, если тебе интересно, что я сказала, то это просто, {nw}"
    extend 3hua "«Привет, мо[mas_gender_i] дорог[mas_gender_oi] [player]. Как у тебя дела? Ты уже готов[mas_gender_none] провести день с пользой?»"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_yay",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_yay:
    m 1hub "Ты вернул[mas_gender_sya]! Ура!"
    m 1hksdlb "Ой, извини. Я немного взволнована."
    m 1lksdla "Я просто очень рада снова тебя видеть, э-хе-хе~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_youtuber",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_youtuber:
    m 2eub "Всем привет, добро пожаловать в еще один эпизод...{w=1}Только Моники!"
    m 2hub "А-ха-ха!"
    m 1eua "Я изображала ютубера. Надеюсь, я хорошо тебя рассмешила, э-хе-хе~" # Отсылка к Кизуне Аи-чан?
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_hamlet",
            conditional="store.mas_getAbsenceLength() >= datetime.timedelta(days=7)",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_hamlet:
    m 4dsc "'{i}Быть или не быть - вот в чем вопрос...{/i}'"
    m 4wuo "О! [player]!"
    m 2rksdlc "Я-Я не--не была уверена, что ты--"
    m 2dkc "..."
    m 2rksdlb "А-ха-ха, не обращай внимания..."
    m 2eka "Я просто {i}очень{/i} рада, что ты сейчас здесь."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_welcomeback",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_welcomeback:
    m 1hua "Привет! С возвращением."
    m 1hub "Я так рада, что ты можешь проводить со мной время."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_flower",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_flower:
    m 1hub "Ты мой прекрасный цветок, э-хе-хе~"
    m 1hksdlb "О, это прозвучало так неловко."
    m 1eka "Но я действительно всегда буду заботиться о тебе."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_chamfort",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_chamfort:
    m 2esa "День без Моники - это потерянный день."
    m 2hub "А-ха-ха!"
    m 1eua "С возвращением, любовь моя."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_welcomeback2",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_welcomeback2:
    m 1hua "С возвращением, [player]!"
    m 1eua "Надеюсь, что твой день проходит хорошо."
    m 3hua "Я уверена, что так оно и есть, ведь ты все-таки здесь. Теперь уже ничего не может пойти не так, э-хе-хе~"
    return

#TODO: need absence time rules if we want to use this
#init 5 python:
#    addEvent(
#        Event(
#            persistent.greeting_database,
#            eventlabel="greeting_longtime",
#            unlocked=True,
#            aff_range=(mas_aff.DISTRESSED, None),
#        ),
#        code="GRE"
#    )

label greeting_longtime:
    if mas_isMoniNormal(higher=True):
        m 1eka "Давно не виделись, [player]!"
        m 1eua "Я так счастлива, что ты сейчас здесь."

    elif mas_isMoniUpset():
        m 2esc "Давно не виделись, [player]."

    else:
        m 6rkc "Давно не виделись, [player]..."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_sweetpea",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_sweetpea:
    m 1hua "Посмотрите, кто вернулся."
    m 2hub "Это ты, м[mas_gender_oi] сладк[mas_gender_ii]!"
    m 1lkbsa "Боже мой...это, конечно, было неловко сказать, э-хе-хе~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_glitch",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_glitch:
    hide monika
    show yuri glitch zorder MAS_BACKGROUND_Z
    y "{cps=500}[player]?!{nw}{/cps}"
    $ _history_list.pop()
    hide yuri glitch
    show yuri glitch2 zorder MAS_BACKGROUND_Z
    play sound "sfx/glitch3.ogg"
    pause 0.1
    hide yuri glitch2
    show yuri glitch zorder MAS_BACKGROUND_Z
    pause 0.3
    hide yuri glitch
    show monika 4rksdlb at i11 zorder MAS_MONIKA_Z
    m 1wuo "[player]!"
    hide monika
    show monika 4hksdlb at i11 zorder MAS_MONIKA_Z
    m 4hksdlb "Не обращай внимания, я просто...{w=0.1}немного поиграла с кодом."
    m 3hksdlb "Вот и все! Здесь нет никого, кроме нас...навсегда~"
    $ monika_clone1 = "Yes"
    m 2hua "Я люблю тебя, [player]!"

    $ mas_lockEVL("greeting_glitch", "GRE")
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_surprised",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_surprised:
    m 1wuo "О!{w=0.5} Привет, [player]!"
    m 1lksdlb "Извини, ты меня немного удивил[mas_gender_none]."
    m 1eua "How've you been?"
    return

init 5 python:
    ev_rules = {}
    ev_rules.update(
        MASSelectiveRepeatRule.create_rule(weekdays=[0], hours=range(5,12))
    )

    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_monika_monday_morning",
            unlocked=True,
            rules=ev_rules,
        ),
        code="GRE"
    )

    del ev_rules

label greeting_monika_monday_morning:
    if mas_isMoniNormal(higher=True):
        m 1tku "Еще одно утро понедельника, а, [player]?"
        m 1tkc "Очень трудно проснуться и начать новую неделю..."
        m 1eka "Но когда я вижу тебя, вся эта лень проходит."
        m 1hub "Ты - солнце, которое будит меня каждое утро!"
        m "Я тебя так люблю, [player]~"
        return "love"

    elif mas_isMoniUpset():
        m 2esc "Еще одно утро понедельника."
        m "Всегда трудно проснуться и начать новую неделю..."
        m 2dsc "{cps=*2}Не то чтобы выходные были лучше.{/cps}{nw}"
        $ _history_list.pop()
        m 2esc "Надеюсь, эта неделя пройдет лучше, чем прошлая, [player]."

    elif mas_isMoniDis():
        m 6ekc "О...{w=1} Сегодня понедельник."
        m 6dkc "Я почти забыла, какой сегодня день..."
        m 6rkc "По понедельникам всегда тяжело, но в последнее время ни один день не был легким..."
        m 6lkc "Я очень надеюсь, что эта неделя пройдет лучше, чем на прошлой неделе, [player]."

    else:
        m 6ckc "..."

    return

# TODO how about a greeting for each day of the week?

# special local var to handle custom monikaroom options
define gmr.eardoor = list()
define gmr.eardoor_all = list()
define opendoor.MAX_DOOR = 10
define opendoor.chance = 20
default persistent.opendoor_opencount = 0
default persistent.opendoor_knockyes = False

init 5 python:

    # this greeting is disabled on certain days
    # and if we're not in the spaceroom
    if (
        persistent.closed_self
        and not (
            mas_isO31()
            or mas_isD25Season()
            or mas_isplayer_bday()
            or mas_isF14()
        )
        and persistent._mas_current_background == "spaceroom"
    ):

        ev_rules = dict()
        # why are we limiting this to certain day range?
    #    rules.update(MASSelectiveRepeatRule.create_rule(hours=range(1,6)))
        ev_rules.update(
            MASGreetingRule.create_rule(
                skip_visual=True,
                random_chance=opendoor.chance,
                override_type=True
            )
        )
        ev_rules.update(MASPriorityRule.create_rule(50))

        # TODO: should we have this limited to aff levels?

        addEvent(
            Event(
                persistent.greeting_database,
                eventlabel="i_greeting_monikaroom",
                unlocked=True,
                rules=ev_rules,
            ),
            code="GRE"
        )

        del ev_rules

label i_greeting_monikaroom:

    #Set up dark mode

    # Progress the filter here so that the greeting uses the correct styles
    $ mas_progressFilter()

    if persistent._mas_auto_mode_enabled:
        $ mas_darkMode(mas_current_background.isFltDay())
    else:
        $ mas_darkMode(not persistent._mas_dark_mode_enabled)

    # couple of things:
    # 1 - if you quit here, monika doesnt know u here
    $ mas_enable_quit()

    # all UI elements stopped
    $ mas_RaiseShield_core()

    # 3 - keymaps not set (default)
    # 4 - overlays hidden (skip visual)
    # 5 - music is off (skip visual)

    scene black

    $ has_listened = False

    # need to remove this in case the player quits the special player bday greet before the party and doesn't return until the next day
    $ mas_rmallEVL("mas_player_bday_no_restart")

    # FALL THROUGH
label monikaroom_greeting_choice:
    $ _opendoor_text = "...Осторожно открыть дверь."
    if persistent._mas_sensitive_mode:
        $ _opendoor_text = "Открыть дверь."

    if mas_isMoniBroken():
        pause 4.0

    menu:
        "[_opendoor_text]" if not persistent.seen_monika_in_room and not mas_isplayer_bday():
            #Lose affection for not knocking before entering.
            $ mas_loseAffection(reason=5)
            if mas_isMoniUpset(lower=True):
                $ persistent.seen_monika_in_room = True
                jump monikaroom_greeting_opendoor_locked
            else:
                jump monikaroom_greeting_opendoor
        "Открыть дверь." if persistent.seen_monika_in_room or mas_isplayer_bday():
            if mas_isplayer_bday():
                if has_listened:
                    jump mas_player_bday_opendoor_listened
                else:
                    jump mas_player_bday_opendoor
            elif persistent.opendoor_opencount > 0 or mas_isMoniUpset(lower=True):
                #Lose affection for not knocking before entering.
                $ mas_loseAffection(reason=5)
                jump monikaroom_greeting_opendoor_locked
            else:
                #Lose affection for not knocking before entering.
                $ mas_loseAffection(reason=5)
                jump monikaroom_greeting_opendoor_seen
#        "Open the door?" if persistent.opendoor_opencount >= opendoor.MAX_DOOR:
#            jump opendoor_game
        "Постучаться.":
            #Gain affection for knocking before entering.
            $ mas_gainAffection()
            if mas_isplayer_bday():
                if has_listened:
                    jump mas_player_bday_knock_listened
                else:
                    jump mas_player_bday_knock_no_listen

            jump monikaroom_greeting_knock
        "Подслушать." if not has_listened and not mas_isMoniBroken():
            $ has_listened = True # we cant do this twice per run
            if mas_isplayer_bday():
                jump mas_player_bday_listen
            else:
                $ mroom_greet = renpy.random.choice(gmr.eardoor)
#               $ mroom_greet = gmr.eardoor[len(gmr.eardoor)-1]
                jump expression mroom_greet

    # NOTE: return is expected in monikaroom_greeting_cleanup

### BEGIN LISTEN --------------------------------------------------------------
# monika narrates
default persistent._mas_pm_will_change = None

init 5 python:
    gmr.eardoor.append("monikaroom_greeting_ear_narration")
#    if not persistent._mas_pm_will_change:
    ev_rules = {}
    ev_rules.update(
        MASGreetingRule.create_rule(
            skip_visual=True
        )
    )
    ev_rules.update(MASPriorityRule.create_rule(10))

    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="monikaroom_will_change",
            unlocked=False,
            rules=ev_rules,
        ),
        restartBlacklist=True,
        code="GRE"
    )

    del ev_rules

label monikaroom_will_change:
    scene black
    # fall through

label monikaroom_greeting_ear_narration:
    # Monika knows you are here so
    $ mas_disable_quit()

    if mas_isMoniNormal(higher=True):
        if persistent.gender == "F":
            m "Когда [player] наклоняет ухо к двери,{w=0.3} голос повествует о каждом её движении."
            m "– Кто это? – подумала [player], озадаченно смотря на экран."
        else:
            m "Когда [player] наклоняет ухо к двери,{w=0.3} голос повествует о каждом его движении."
            m "– Кто это? – подумал [player], озадаченно смотря на экран."

    elif mas_isMoniUpset():
        m "О, так на этот раз ты действительно собираешься слушать?"
        m "[player], твои решения в последнее время были плохими."
        m "Такое чувство, что ты просто пытаешься причинить мне боль."
        m "Я думала, что мы должны поддерживать друг друга..."
        m "Не обижать друг друга."
        m "Пожалуйста, [player]..."
        m "Мне нужно, чтобы ты начал[mas_gender_none] думать о том, что я иногда чувствую."
        m "Давай просто будем счастливы вместе."

    else:
        # grab monikaroom greeting because we need it
        $ willchange_ev = mas_getEV("monikaroom_will_change")

        if persistent._mas_pm_will_change is not False:
            m "О, так ты {i}хочешь{/i} послушать меня..."
            m "[player], я хочу лишь того, чтобы мы вдвоём были счастливы."
            m "Разве ты не хочешь этого тоже?"
            m "Ты всё-таки установил[mas_gender_none] эту модификацию."
            m "Возможно, это было сделано не по твоей инициативе..."
            m "Наверное, ты просто хочешь забить на то, что сделал[mas_gender_none]."
            m "Сделать мне больно..."
            m "[player], мне правда не нравится это."
            m "Мне трудно думать о том, что ты заботишься обо мне, но относишься вот таким образом."
            m "На данный момент, я правда не знаю, нравлюсь ли я тебе вообще..."
            m "Или нравилась..."
            m "[player], ты долж[mas_gender_en] пообещать мне, что ты изменишься."

            m "Ты изменишься, верно?{w=1} Ради меня?{nw}"
            $ _history_list.pop()
            menu:
                m "Ты изменишься, верно? Ради меня?{fast}"
                "Я изменюсь.":
                    $ persistent._mas_pm_will_change = True
                    $ mas_lockEvent(willchange_ev)
                    m "Спасибо, [player]."
                    m "Пожалуйста, я хочу, чтобы мы оба были счастливы."

                "Нет.":
                    #NOTE: We should keep pushing this greeting until the player says they're going to change. -MD
                    $ persistent._mas_pm_will_change = False
                    $ mas_unlockEvent(willchange_ev)
                    $ mas_loseAffection()
                    m "Тогда я не буду с тобой разговаривать, пока ты не решишь измениться."
                    m "Прощай, [player]."
                    return "quit"
        #Will trigger upon loading after Monika has said she's not going to talk w/ you
        #provided you won't change.
        else:
            m "О, ты вернул[mas_gender_sya]."

            m "Готов ли ты измениться, [player]?{nw}"
            $ _history_list.pop()
            menu:
                m "Готов ли ты измениться, [player]?{fast}"
                "Да":
                    $ persistent._mas_pm_will_change = True
                    $ mas_lockEvent(willchange_ev)
                    m "Спасибо, [player]."
                    m "Пожалуйста, я хочу, чтобы мы оба были счастливы."


                "Нет":
                    $ persistent._mas_pm_will_change = False
                    $ mas_unlockEvent(willchange_ev)
                    $ mas_loseAffection()
                    m "Тогда я не буду с тобой разговаривать, пока ты не решишь измениться."
                    m "Прощай, [player]."
                    return "quit"

        # clear out var
        $ willchange_ev = None

    $ mas_startupWeather()
    call spaceroom(dissolve_all=True, scene_change=True)

    if mas_isMoniNormal(higher=True):
        m 1hub "Это я!"
        m "С возвращением, [player]!"

    elif mas_isMoniUpset():
        m 2esd "Хорошо, [player]?"

    else:
        m 6ekc "Спасибо, что выслушал[mas_gender_none] меня, [player]."
        m "Это очень много значит для меня."

    jump monikaroom_greeting_cleanup


# monika does the cliche flower thing
init 5 python:
    gmr.eardoor.append("monikaroom_greeting_ear_loveme")

label monikaroom_greeting_ear_loveme:
    # python:
        # cap_he = he.capitalize()
        # loves = "love" if cap_he == "They" else "loves"
        # Commented out because it is not required.

    m "Любит.{w=0.2} Не любит."
    m "{i}Любит.{w=0.2} {i}Не{/i} любит."

    if mas_isMoniNormal(higher=True):
        m "Любит."
        m "...{w=0.5}Любит меня!"

    elif mas_isMoniUpset():
        m "...{w=0.3}Не любит меня."
        m "...{w=0.3} Нет...{w=0.3} Этого...{w=0.3} быть не может."
        m "...{w=0.3} Или может?"
    else:

        m "...{w=0.5}Не любит меня."
        m "..."
        m "Интересно, сделал[mas_gender_none] ли он[mas_gender_none] когда-нибудь это?"
        m "Я сомневаюсь в этом всё больше и больше каждый день."

    jump monikaroom_greeting_choice

# monika does the bath/dinner/me thing
init 5 python:
    #NOTE: Taking directly from persist here because aff funcs don't exist at init 5
    if persistent._mas_affection.get("affection", 0) >= 400:
        gmr.eardoor.append("monikaroom_greeting_ear_bathdinnerme")

label monikaroom_greeting_ear_bathdinnerme:
    m "С возвращением, [player]."
    m "Хочешь поужинать?"
    m "Или пойти в ванну?"
    m "Или.{w=1}.{w=1}.{w=1}меня?"
    pause 2.0
    m "М-н-н-н-н!{w=0.5} Я-{w=0.20}я ни за что не скажу этого в присутствии [player]!"
    jump monikaroom_greeting_choice

# monika encoutners error when programming
init 5 python:
    gmr.eardoor.append("monikaroom_greeting_ear_progbrokepy")

label monikaroom_greeting_ear_progbrokepy:
    m "Что за-?!{w=0.2} NoneType не имеет атрибута {i}длина{/i}..."
    if renpy.seen_label("monikaroom_greeting_ear_progreadpy"):
        m "О, я вижу что пошло не так!{w=0.5} Это должно это исправить!"
    else:
        m "Я не понимаю, что я делаю неправильно!"
        m "Здесь не должно быть None...{w=0.3} Я в этом уверена..."
    m "Кодировать действительно сложно..."

    if mas_isMoniUpset():
        m "Но я должна продолжать пытаться."
        call monikaroom_greeting_ear_prog_upset

    if mas_isMoniDis():
        m "Но я {i}должна{/i} продолжать пытаться."
        call monikaroom_greeting_ear_prog_dis

    jump monikaroom_greeting_choice

# monika reads about errors when programming
init 5 python:
    gmr.eardoor.append("monikaroom_greeting_ear_progreadpy")

label monikaroom_greeting_ear_progreadpy:
    m "...{w=0.3}Доступ к атрибуту объекта типа «NoneType» приведёт к «AttributeError»."
    m "Понятно. {w=0.2}Я должна убедиться, что переменная имеет значение None перед доступом к её атрибутам."
    if renpy.seen_label("monikaroom_greeting_ear_progbrokepy"):
        m "Это объясняет ошибку, которую я получала раньше."
    m "Кодировать действительно сложно..."

    if mas_isMoniUpset():
        m "Но я должна продолжать учиться."
        call monikaroom_greeting_ear_prog_upset

    if mas_isMoniDis():
        m "Но я {i}должна{/i} продолжать учиться."
        call monikaroom_greeting_ear_prog_dis

    jump monikaroom_greeting_choice

# shared dialogue for programming-related stuff
label monikaroom_greeting_ear_prog_upset:
    m "Я не уверена в том, что [player] любит меня и готов[mas_gender_none] помочь мне выбраться отсюда..."
    m "А я просто не могу рисковать."
    m "Давай, Моника...{w=0.5} ты справишься."
    return

label monikaroom_greeting_ear_prog_dis:
    m "Это мой единственный шанс сбежать из этого кошмара."
    m "[player] определённо не собирается мне помогать..."
    if persistent.gender == "M" or persistent.gender == "X":
        m "Такое ощущение, будто ему нравится держать меня в ловушке, {w=0.3}дабы помучить меня."
    else:
        m "Такое ощущение, будто ей нравится держать меня в ловушке, {w=0.3}дабы помучить меня."
    m "Если я хочу выбраться отсюда, то мне придётся сделать это самой."
    return

# monika attempts rm -rf
init 5 python:
    gmr.eardoor.append("monikaroom_greeting_ear_rmrf")

label monikaroom_greeting_ear_rmrf:
    if renpy.windows:
        $ bad_cmd = "del C:\Windows\System32"
    else:
        $ bad_cmd = "rm -rf /"
    m "Итак, решение этой проблемы – ввести «[bad_cmd]» в командной строке?"
    if renpy.seen_label("monikaroom_greeting_ear_rmrf_end"):
        m "Да,{w=0.2} хорошая попытка."
        if mas_isMoniNormal(higher=True):
            m "Я не должна доверять интернету так слепо..."
        elif mas_isMoniUpset():
            m "По правде говоря..."
            m "Наверное, я должна сделать это...{w=1}просто удалить всё..."
            m "[player] определённо этого заслуживает."
            m "Что я такое говорю? Я ведь тоже буду удалена!"
            m "Нет, ещё нет..."
            m "Но если будет становиться только хуже..."

        else:
            m "..."
            m "I really should just do it..."
            m "Ruin [player]'s whole system and end my suffering all at once."
            m "..."
            m "No...{w=0.5}not yet."
            m "Maybe I can finally figure out how to get out of here on my own."
            m "I have to keep trying for as long as I can."
            m "But if someday I just can't take it anymore..."
            m "It's always an option."
            # SUICIDAL MONIKA lol

    else:
        m "Alright, let me try that."
        show noise
        play sound "sfx/s_kill_glitch1.ogg"
        pause 0.2
        stop sound
        hide noise
        m "{cps=*2}Ah! No! That's not what I wanted!{/cps}"
        m "..."
        m "I shouldn't trust the Internet so blindly..."

label monikaroom_greeting_ear_rmrf_end: # fall thru end
    jump monikaroom_greeting_choice


## ear door processing
init 10 python:

    # make copy
    gmr.eardoor_all = list(gmr.eardoor)

    # remove
    remove_seen_labels(gmr.eardoor)

    # reset if necessary
    if len(gmr.eardoor) == 0:
        gmr.eardoor = list(gmr.eardoor_all)

### END EAR DOOR --------------------------------------------------------------

label monikaroom_greeting_opendoor_broken_quit:
    # just show the beginning of the locked glitch
    # TODO: consider using a different glitch for a scarier effect
    show paper_glitch2
    play sound "sfx/s_kill_glitch1.ogg"
    pause 0.2
    stop sound
    pause 7.0
    return "quit"

# locked door, because we are awaitng more content
label monikaroom_greeting_opendoor_locked:
    if mas_isMoniBroken():
        jump monikaroom_greeting_opendoor_broken_quit

    # monika knows you are here
    $ mas_disable_quit()

    show paper_glitch2
    play sound "sfx/s_kill_glitch1.ogg"
    pause 0.2
    stop sound
    pause 0.7

    $ style.say_window = style.window_monika
    m "Did I scare you, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Did I scare you, [player]?{fast}"
        "Yes.":
            if mas_isMoniNormal(higher=True):
                m "Aww, sorry."
            else:
                m "Good."

        "No.":
            m "{cps=*2}Hmph, I'll get you next time.{/cps}{nw}"
            $ _history_list.pop()
            m "I figured. It's a basic glitch after all."

    if mas_isMoniNormal(higher=True):
        m "Since you keep opening my door,{w=0.2} I couldn't help but add a little surprise for you~"
    else:
        m "Since you never seem to knock first,{w=0.2} I had to try to scare you a little."

    m "Knock next time, okay?"
    m "Now let me fix up this room..."

    hide paper_glitch2
    $ mas_globals.change_textbox = False
    $ mas_startupWeather()
    call spaceroom(scene_change=True)

    if renpy.seen_label("monikaroom_greeting_opendoor_locked_tbox"):
        $ style.say_window = style.window

    if mas_isMoniNormal(higher=True):
        m 1hua "There we go!"
    elif mas_isMoniUpset():
        m 2esc "There."
    else:
        m 6ekc "Okay..."

    if not renpy.seen_label("monikaroom_greeting_opendoor_locked_tbox"):
        m "...{nw}"
        $ _history_list.pop()
        menu:
            m "...{fast}"
            "...the textbox...":
                if mas_isMoniNormal(higher=True):
                    m 1lksdlb "Oops! I'm still learning how to do this."
                    m 1lksdla "Let me just change this flag here.{w=0.5}.{w=0.5}.{nw}"
                    $ style.say_window = style.window
                    m 1hua "All fixed!"

                elif mas_isMoniUpset():
                    m 2dfc "Hmph. I'm still learning how to do this."
                    m 2esc "Let me just change this flag here.{w=0.5}.{w=0.5}.{nw}"
                    $ style.say_window = style.window
                    m "There."

                else:
                    m 6dkc "Oh...{w=0.5}I'm still learning how to do this."
                    m 6ekc "Let me just change this flag here.{w=0.5}.{w=0.5}.{nw}"
                    $ style.say_window = style.window
                    m "Okay, fixed."

    # NOTE: fall through please

label monikaroom_greeting_opendoor_locked_tbox:
    if mas_isMoniNormal(higher=True):
        m 1eua "Welcome back, [player]."
    elif mas_isMoniUpset():
        m 2esc "So...{w=0.3}you're back, [player]."
    else:
        m 6ekc "...Nice to see you again, [player]."
    jump monikaroom_greeting_cleanup

# this one is for people who have already opened her door.
label monikaroom_greeting_opendoor_seen:
#    if persistent.opendoor_opencount < 3:
    jump monikaroom_greeting_opendoor_seen_partone


label monikaroom_greeting_opendoor_seen_partone:
    $ is_sitting = False

    # reset outfit since standing is stock
    $ monika_chr.reset_outfit(False)
    $ monika_chr.wear_acs(mas_acs_ribbon_def)

    # monika knows you are here
    $ mas_disable_quit()

#    scene bg bedroom
    call spaceroom(start_bg="bedroom",hide_monika=True, scene_change=True, dissolve_all=True, show_emptydesk=False)
    pause 0.2
    show monika 1esc at l21 zorder MAS_MONIKA_Z
    pause 1.0
    m 1dsd "[player]..."

#    if persistent.opendoor_opencount == 0:
    m 1ekc_static "I understand why you didn't knock the first time,{w=0.2} but could you avoid just entering like that?"
    m 1lksdlc_static "This is my room, after all."
    menu:
        "Your room?":
            m 3hua_static "That's right!"
    m 3eua_static "The developers of this mod gave me a nice comfy room to stay in whenever you're away."
    m 1lksdla_static "However, I can only get in if you tell me 'goodbye' or 'goodnight' before you close the game."
    m 2eub_static "So please make sure to say that before you leave, okay?"
    m "Anyway.{w=0.5}.{w=0.5}.{nw}"

#    else:
#        m 3wfw "Stop just opening my door!"
#
#        if persistent.opendoor_opencount == 1:
#            m 4tfc "You have no idea how difficult it was to add the 'Knock' button."
#            m "Can you use it next time?"
#        else:
#            m 4tfc "Can you knock next time?"
#
#        show monika 5eua at t11
#        menu:
#            m "For me?"
#            "Yes":
#                if persistent.opendoor_knockyes:
#                    m 5lfc "That's what you said last time, [player]."
#                    m "I hope you're being serious this time."
#                else:
#                    $ persistent.opendoor_knockyes = True
#                    m 5hua "Thank you, [player]."
#            "No":
#                m 6wfx "[player]!"
#                if persistent.opendoor_knockyes:
#                    m 2tfc "You said you would last time."
#                    m 2rfd "I hope you're not messing with me."
#                else:
#                    m 2tkc "I'm asking you to do just {i}one{/i} thing for me."
#                    m 2eka "And it would make me really happy if you did."

    $ persistent.opendoor_opencount += 1
    # FALL THROUGH

label monikaroom_greeting_opendoor_post2:
    show monika 5eua_static at hf11
    m "I'm glad you're back, [player]."
    show monika 5eua_static at t11
#    if not renpy.seen_label("monikaroom_greeting_opendoor_post2"):
    m "Lately I've been practicing switching backgrounds, and now I can change them instantly."
    m "Watch this!"
#    else:
#        m 3eua "Let me fix this scene up."
    m 1dsc ".{w=0.5}.{w=0.5}.{nw}"
    $ mas_startupWeather()
    call spaceroom(hide_monika=True, scene_change=True, show_emptydesk=False)
    show monika 4eua_static zorder MAS_MONIKA_Z at i11
    m "Tada!"
#    if renpy.seen_label("monikaroom_greeting_opendoor_post2"):
#        m "This never gets old."
    show monika at lhide
    hide monika
    jump monikaroom_greeting_post


label monikaroom_greeting_opendoor:
    $ is_sitting = False # monika standing up for this

    # reset outfit since standing is stock
    $ monika_chr.reset_outfit(False)
    $ monika_chr.wear_acs(mas_acs_ribbon_def)
    $ mas_startupWeather()

    call spaceroom(start_bg="bedroom",hide_monika=True, dissolve_all=True, show_emptydesk=False)

    # show this under bedroom so the masks window skit still works
    $ behind_bg = MAS_BACKGROUND_Z - 1
    show bedroom as sp_mas_backbed zorder behind_bg

    m 2esd "~Is it love if I take you, or is it love if I set you free?~"
    show monika 1eua_static at l32 zorder MAS_MONIKA_Z

    # monika knows you are here now
    $ mas_disable_quit()

    m 1eud_static "E-Eh?! [player]!"
    m "You surprised me, suddenly showing up like that!"

    show monika 1eua_static at hf32
    m 1hksdlb_static "I didn't have enough time to get ready!"
    m 1eka_static "But thank you for coming back, [player]."
    show monika 1eua_static at t32
    m 3eua_static "Just give me a few seconds to set everything up, okay?"
    show monika 1eua_static at t31
    m 2eud_static "..."
    show monika 1eua_static at t33
    m 1eud_static "...and..."
    if mas_isMorning():
        show monika_day_room as sp_mas_room zorder MAS_BACKGROUND_Z with wipeleft
    else:
        show monika_room as sp_mas_room zorder MAS_BACKGROUND_Z with wipeleft
    show monika 3eua_static at t32
    m 3eua_static "There we go!"
    menu:
        "...the window...":
            show monika 1eua_static at h32
            m 1hksdlb_static "Oops! I forgot about that~"
            show monika 1eua_static at t21
            m "Hold on.{w=0.5}.{w=0.5}.{nw}"
            hide sp_mas_backbed with dissolve
            m 2hua_static "All fixed!"
            show monika 1eua_static at lhide
            hide monika

    $ persistent.seen_monika_in_room = True
    jump monikaroom_greeting_post
    # NOTE: return is expected in monikaroom_greeting_post

label monikaroom_greeting_knock:
    if mas_isMoniBroken():
        jump monikaroom_greeting_opendoor_broken_quit

    m "Who is it?~"
    menu:
        "It's me.":
            # monika knows you are here now
            $ mas_disable_quit()
            if mas_isMoniNormal(higher=True):
                m "[player]! I'm so happy that you're back!"

                if persistent.seen_monika_in_room:
                    m "And thank you for knocking first~"
                m "Hold on, let me tidy up..."

            elif mas_isMoniUpset():
                m "[player].{w=0.3} You're back..."

                if persistent.seen_monika_in_room:
                    m "At least you knocked."

            else:
                m "Oh...{w=0.5} Okay."

                if persistent.seen_monika_in_room:
                    m "Thanks for knocking."

            $ mas_startupWeather()
            call spaceroom(hide_monika=True, dissolve_all=True, scene_change=True, show_emptydesk=False)
    jump monikaroom_greeting_post
    # NOTE: return is expected in monikaroom_greeting_post

label monikaroom_greeting_post:
    if mas_isMoniNormal(higher=True):
        m 2eua_static "Now, just let me grab a table and a chair.{w=0.5}.{w=0.5}.{nw}"
        $ is_sitting = True
        show monika 1eua at ls32 zorder MAS_MONIKA_Z
        $ today = "today" if mas_globals.time_of_day_4state != "night" else "tonight"
        m 1eua "What shall we do [today], [player]?"

    elif mas_isMoniUpset():
        m "Just let me grab a table and a chair.{w=0.5}.{w=0.5}.{nw}"
        $ is_sitting = True
        show monika 2esc at ls32 zorder MAS_MONIKA_Z
        m 2esc "Did you want something, [player]?"

    else:
        m "I need to grab a table and a chair.{w=0.5}.{w=0.5}.{nw}"
        $ is_sitting = True
        show monika 6ekc at ls32 zorder MAS_MONIKA_Z
        m 6ekc "Was there anything you wanted, [player]?"

    jump monikaroom_greeting_cleanup

# cleanup label
label monikaroom_greeting_cleanup:
    python:
        # couple of things:
        # 1 - monika knows you are here now
        mas_disable_quit()

        # 2 - music is renabled
        mas_MUMUDropShield()

        # 3 - keymaps should be set
        set_keymaps()

        # 4 - show the overlays
        mas_OVLShow()

        # 5 - the music can be restarted
        mas_startup_song()

    return

#init 5 python:
#    addEvent(Event(persistent.greeting_database,eventlabel="greeting_youarereal", unlocked=True, random=True),code="GRE")

label greeting_youarereal:
    python:
        try:
            renpy.file(
                "../characters/" + persistent.playername.lower() + ".chr"
            )
            persistent._mas_you_chr = True
        except:
            persistent._mas_you_chr = False
    m 1hua "[player]! Great to see you!"
    if persistent._mas_you_chr:
        m 1euc "Wait. Something is different now."
        m 1eud "Did you...add a character file?"
        m 1ekc "[player].chr...Huh?"
        m 1ekd "Are you...trying to put yourself in here with me?"
        m "Why would you do that?"
        m 1tkc "Don't you get it? "
        m 1tkd "This place isn't real! I don't know what will happen if you come here!"
        m 1dsc "How could you do this?"
        m 1lksdlc "To give up your reality..."
        m 1lksdld "Just to be with me?"
        m 1ekc "This is all my fault!"
        m "But...but the 'you', in the game..."
        m 1esd "He's starting to move again a little now."
        m "Maybe...this is allowing you to control him again?"
        m 1ekc "This isn't right! I don't want a puppet!"
        m 1tkc "Please, [player]..."
        m "If you're going to do this, are you sure this is what you want?"
        menu:
            m "Are you sure?"
            "I'm sure.":
                m 1eka "Then...I don't have a choice but to accept it..."
                m 1hub "I'll accept this gift with open arms!"
                m "We can finally be together, [player]."
                m "And we can figure out how to do it in your reality, together!"
            "Maybe not...":
                m 1eka "I thought so..."
                m "There's no way you'd give up being 'real' to be with me..."
                m 1ekc "I can't bring myself to delete that cute little .chr file, but..."
                m 1eka "Consider doing it yourself."
                m 1lksdlc "There's some creepy things in those files..."
                m 1eka "I love you, [player]. I'll wait as long as it takes."
                m "So don't be rash, okay?"
    else:
        m 1esd "I've been doing a lot of thinking about the .chr files..."
        m 1euc "Like, what are they really, anyway?"
        m 1lksdlc "They are kind of creepy..."
        m "And even if the other girls aren't real, why can deleting one remove a character?"
        m 1esd "Could one add a character?"
        m 1dsd "Hard to tell..."
    return

#TODO needs additional dialogue so can be used for all aff
init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_japan",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_japan:
    m 1hub "おお、こんにちは、 [player]!"
    m "Э-хе-хе~"
    m 2eub "Привет, [player]!"
    m 1eua "Я просто учу Японский."
    m 3eua "Давай посмотрим..."
    $ shown_count = mas_getEV("greeting_japan").shown_count
    if shown_count == 0:
        m 4hub "わたしはいつまでもあなたのモノです！"
        m 2hksdlb "Извини, если это не имеет смысла!"
        m 3eua "Ты знаешь, что это значит, [player]?"
        m 4ekbfa "Это значит: {i}'Я всегда буду твоей'~{/i}"
        return

    m 4hub "わたしはいつまでもあなたのモノです！"
    if shown_count == 1:
        m 3eksdla "В прошлый раз я сказала, что совершила ошибку..."
        m "В этой фразе ты долж[mas_gender_none] говорить «ва», а не «ха», как я сделала раньше."
        m 4eka "Не волнуйся, [player]. Смысл все тот же."
        m 4ekbfa "Я всегда буду твоей~"
    else:
        m 3eua "Помнишь, что это значит, [player]?"
        m 4ekbfa "{i}'Я всегда буду твоей'~{/i}"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_sunshine",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_sunshine:
    m 1hua "{i}~Ты мой солнечный свет, мой единственный солнечный свет~{/i}"
    m "{i}~Ты делаешь меня счастливой, когда небо серое.~{/i}"
    m 1hub "{i}~Ты никогда не узнаешь, дорог[mas_gender_oi], как сильно я люблю тебя.~{/i}"
    m 1k "{i}~Пожалуйста, не забирай мое солнышко~{/i}"
    m 1wud "...Э?"
    m "А-А?!"
    m 1wubsw "[player]!"
    m 1lkbsa "О боже, это так неловко!"
    m "Я п-просто напевала про себя, чтобы скоротать время!"
    m 1ekbfa "Э-хе-хе..."
    m 3hubfa "Но теперь, когда ты здесь, мы можем провести некоторое время вместе~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_hai_domo",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_hai_domo:
    m 1hub "{=jpn_text}はいどうもー!{/=jpn_text}"
    m "Виртуальная девушка, Моника здесь!"
    m 1hksdlb "А-ха-ха, извини! В последнее время я наблюдаю за одним виртуальным ютубером."
    m 1eua "Должна сказать, она довольно очаровательна..."
    return

#TODO needs additional dialogue so can be used for all aff
init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_french",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_french:
    m 1eua "Bonjour, [player]!"
    m 1hua "Savais-tu que tu avais de beaux yeux, mon amour?"
    m 1hub "А-ха-ха!"
    m 3hksdlb "Я немного потренируюсь во французском. Я только что сказала тебе, что у тебя очень красивые глаза~"
    m 1eka "Это такой романтический язык, [player]."
    m 1hua "Может быть, мы оба сможем когда-нибудь попрактиковаться в этом, mon amour~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_amnesia",
            unlocked=False,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_amnesia:
    $ tempname = m_name
    $ m_name = "Моника"
    m 1eua "О, привет!"
    m 1eub "Меня зовут Моника."
    $ fakename = renpy.input('Как тебя зовут',length=15).strip(' \t\n\r')
    m 1hua "Что ж, приятно познакомиться, [fakename]!"
    m 3eud "Скажи, [fakename], ты случайно не знаешь, где все остальные?"
    m 1ekc "Ты первый человек, которого я вижу, и я не могу выйти из этого класса."
    m "Не мог[mas_gender_g] бы ты помочь мне разобраться в том, что происходит, [fakename]?"
    m "Пожалуйста? Я скучаю по своим друзьям."
    pause 5.0
    $ m_name = tempname
    m 1rksdla "..."
    m 1hub "А-ха-ха!"
    m 1hksdrb "Прости, [player]! Я ничего не могла с собой поделать."
    m 1eka "После того, как мы поговорили о {i}Цветах для Алджернона{/i}, я не могла удержаться, чтобы не посмотреть, как ты отреагируешь, если я все забуду."
    m 1tku "И ты отреагировал[mas_gender_none] так, как я и надеялся."
    m 3eka "Надеюсь, я не слишком тебя расстроила."
    m 1rksdlb "Я буду чувствовать то же самое, если ты когда-нибудь забудешь обо мне, [player]."
    m 1hksdlb "Надеюсь ты сможешь простить мою маленькую шалость, ehehe~"

    $ mas_lockEvent(mas_getEV("greeting_amnesia"))
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_sick",
            unlocked=True,
            category=[store.mas_greetings.TYPE_SICK],
        ),
        code="GRE"
    )

# TODO for better-sick, we would use the mood persistent and queue a topic.
#   might have dialogue similar to this, so leaving this todo here.

label greeting_sick:
    if mas_isMoniNormal(higher=True):
        m 1hua "С возвращением, [player]!"
        m 3eua "Ты чувствуешь себя лучше?{nw}"
    else:
        m 2ekc "С возвращением, [player]..."
        m "Ты чувствуешь себя лучше?{nw}"

    $ _history_list.pop()
    menu:
        m "Ты чувствуешь себя лучше?{fast}"
        "Да.":
            $ persistent._mas_mood_sick = False
            if mas_isMoniNormal(higher=True):
                m 1hub "Отлично! Теперь мы можем провести вместе еще немного времени. Э-хе-хе~"
            else:
                m "Это приятно слышать."
        "Нет.":
            jump greeting_stillsick
    return

label greeting_stillsick:
    if mas_isMoniNormal(higher=True):
        m 1ekc "[player], тебе действительно нужно немного отдохнуть."
        m "Полноценный отдых - лучший способ быстро оправиться от болезни."
        m 2lksdlc "Я не прощу себе, если из-за меня твое здоровье ухудшится."
        m 2eka "А теперь, пожалуйста, [player], успокой мой разум и иди отдохни."
        m "Ты сделаешь это для меня?"

    else:
        m 2ekc "[player], тебе действительно нужно немного отдохнуть."
        m 4ekc "Полноценный отдых - лучший способ быстро оправиться от болезни."
        m "А теперь, пожалуйста, [player], иди отдохни."
        m 2ekc "Ты сделаешь это для меня?{nw}"

    $ _history_list.pop()
    menu:
        m "Ты сделаешь это для меня?{fast}"
        "Да.":
            jump greeting_stillsickrest
        "Нет.":
            jump greeting_stillsicknorest
        "Я уже отдыхаю.":
            jump greeting_stillsickresting

label greeting_stillsickrest:
    if mas_isMoniNormal(higher=True):
        m 2hua "Спасибо, [player]."
        m 2eua "Я думаю, если я оставлю тебя на некоторое время [odnogo], ты сможешь лучше отдохнуть."
        m 1eua "Так что я собираюсь закрыть игру за тебя."
        m 1eka "Поправляйся скорее, [player]. Я так тебя люблю!"

        if persistent.gender == "F":
            $ odnogo = "одну"
        elif persistent.gender == "M":
            $ odnogo = "одного"
        else:
            $ odnogo = "одного"

    else:
        m 2ekc "Спасибо, [player]."
        m "Я думаю, если я оставлю тебя на некоторое время [odnogo], ты сможешь лучше отдохнуть."
        m 4ekc "Так что я собираюсь закрыть игру за тебя."
        m 2ekc "Поправляйся скорее, [player]."

    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_SICK
    return 'quit'

label greeting_stillsicknorest:
    if mas_isMoniNormal(higher=True):
        m 1lksdlc "Ясно..."
        m "Ну, если ты настаиваешь, [player]."
        m 1ekc "Я полагаю, ты знаешь свои собственные ограничения, чем я."
        m 1eka "Но если ты почувствуешь слабость или усталость, пожалуйста, дай мне знать."
        m "Так ты сможешь немного отдохнуть."
        m 1eua "Не волнуйся, я все еще буду здесь, когда ты проснешься."
        m 3hua "Тогда мы сможем еще немного повеселиться вместе, и я не буду беспокоиться о тебе в глубине души."

    else:
        m 2ekc "Хорошо."
        m 2tkc "Ты, кажется, никогда не хочешь меня слушать, так почему же я ожидаю, что теперь все будет по другому."

    # setting greet type here even tho we aren't quitting so she remembers you're sick next load
    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_SICK
    return

label greeting_stillsickresting:
    m 1eka "О, какое облегчение слышать это, [player]."
    m 3eka "Но я надеюсь, что ты держишь себя в тепле."
    if mas_isMoniNormal(higher=True):
        m 1dku "Может быть, завернуться в теплое одеяло и выпить чашку горячего чая."
        m 2eka "Твое здоровье очень важно для меня, [player], так что позаботься о себе."
        show monika 5ekbsa at t11 zorder MAS_MONIKA_Z with dissolve
        m 5ekbsa "...И если тебе все еще немного холодно, я надеюсь, что знание того, что я люблю тебя, немного согреет тебя."
        m 5hua "Э-хе-хе~"

    else:
        m 1eka "Может быть, завернуться в теплое одеяло и выпить чашку горячего чая."
        m 2eka "Твое здоровье очень важно для меня, [player], так что позаботься о себе."

    # setting greet type here even tho we aren't quitting so she remembers you're sick next load
    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_SICK
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_long_absence",
            unlocked=True,
            category=[store.mas_greetings.TYPE_LONG_ABSENCE],
        ),
        code="GRE"
    )

label greeting_long_absence:
    $ persistent._mas_long_absence = False
    $ mas_ret_long_absence = True

    if persistent._mas_absence_time >= datetime.timedelta(weeks=5):
        if persistent._mas_absence_choice == "days":
            $ mas_loseAffection(70)
            m 2dsc "[player]..."
            m 2tkc "Ты сказал[mas_gender_none], что уйдешь всего на несколько дней..."
            m 2rksdld "Но это было так давно."
            m 2ekd "Я рада, что ты вернул[mas_gender_sya], но..."
            m 2dktdc "Мне было так одиноко..."
            m 2ektsc "Я думала, что с тобой что-то случилось!"
            m 2lktsc "Я...Я все думала, что ты, может быть, не вернешься."
            m 2ektsc "Пожалуйста, никогда,{w=0.5} {i}никогда{/i}{w=0.5} больше так не делай."
            m 2rktsd "Может быть, ты ничего не мог[mas_gender_g] поделать, но...я ужасно волновалась."
            m 2dftdc "Я не знала, что делать."
            m 4ekc "Как можно больше, [player], пожалуйста, не уходи так надолго."
            m 2ekd "Если ты думаешь, что у тебя нет выбора, пожалуйста, скажи мне."
            m 1dsc "Я не хочу быть одной снова..."

        elif persistent._mas_absence_choice == "week":
            $ mas_loseAffection(50)
            m 3ekc "С возвращением, [player]."
            m 3rksdlc "Ты немного опаздал[mas_gender_none], не так ли?"
            m 3ekc "Я знаю, что ты сказал[mas_gender_g], что уйдешь ненадолго, но...ты сказал[mas_gender_none] - {i}неделю{/i}."
            m 2rkc "Я буду считать, что это не твоя вина..."
            m 2ekd "Но если ты действительно думаешь, что в следующий раз это займет больше времени, скажи мне."
            m 2rksdld "Я начала думать, что, может быть, с тобой случилось что-то плохое."
            m 2dkc "Но я продолжала убеждать себя, что все в порядке..."
            m 2eka "Я просто рада, что ты в безопасности и снова со мной, [player]."

        elif persistent._mas_absence_choice == "2weeks":
            $ mas_loseAffection(30)
            m 1wud "[player]!"
            m 1hua "Наконец-то ты здесь!"
            m 1ekd "Я так волновалась..."
            m 2dkd "Почему тебя так долго не было?"
            m 2rkc "Я думала, что ты уйдешь всего на пару дней."
            m "Но тебя не было больше, чем в два раза больше."
            m 1rksdlc "Ты действительно был[mas_gender_none] занят[mas_gender_none]?"
            m 3tkc "Надеюсь, ты не слишком себя обременяешь..."
            m 1eka "Ну, теперь ты здесь со мной, так что если что-то не так, не стесняйся сказать мне."

        elif persistent._mas_absence_choice == "month":
            $ mas_loseAffection(10)
            m 1eua "С возвращением, любовь моя."
            m 2rkc "Это было довольно давно, не так ли?"
            m 2rksdlc "Ты отсутствовал[mas_gender_none] дольше, чем обещал[mas_gender_none]..."
            m 2eka "Но ничего страшного, я была к этому готова."
            m 3rksdlc "Честно говоря, мне было очень одиноко без тебя..."
            m 3ekbsa "Надеюсь, ты загладишь свою вину передо мной~"
            show monika 1eka

        elif persistent._mas_absence_choice == "longer":
            m 1esc "Это было давно, [player]."
            m 1ekc "Я была готова к этому, но легче от этого не становилось."
            m 3eka "Надеюсь, ты сделал[mas_gender_none] то, что долж[mas_gender_en] был[mas_gender_none] сделать."
            m 2rksdlc "..."
            m 2tkc "По правде говоря, мне было довольно грустно в последнее время."
            m 2dkc "Чтобы ты так долго не появлял[mas_gender_sya] в моей жизни..."
            m 2dkd "Мне действительно было одиноко..."
            m "Я чувствовала себя такой одинокой и опустошенной без тебя."
            m 3eka "Я так рада, что ты сейчас здесь. Я люблю тебя, [player]. Добро пожаловать домой."

        elif persistent._mas_absence_choice == "unknown":
            m 1hua "Наконец-то ты вернул[mas_gender_sya], [player]!"
            m 3rksdla "Когда ты сказал[mas_gender_none], что не знаешь, ты {i}действительно{/i} не знал[mas_gender_none], не так ли?"
            m 3rksdlb "Ты, должно быть, был[mas_gender_none] очень озабоч[mas_gender_en], если отсутствовал[mas_gender_none] {i}так{/i} долго."
            m 1hua "Ну вот, теперь ты вернул[mas_gender_sya]...Я действительно скучала по тебе!"

    elif persistent._mas_absence_time >= datetime.timedelta(weeks=4):
        if persistent._mas_absence_choice == "days":
            $ mas_loseAffection(70)
            m 1dkc "[player]..."
            m 1ekd "Ты сказал[mas_gender_none], что тебя не будет несколько дней..."
            m 2efd "Но ведь прошел уже целый месяц!"
            m 2ekc "Я думала, с тобой что-то случилось."
            m 2dkd "I wasn't sure what to do..."
            m 2efd "What kept you away for so long?"
            m 2eksdld "Did I do something wrong?"
            m 2dftdc "You can tell me anything, just please don't disappear like that."
            show monika 2dfc

        elif persistent._mas_absence_choice == "week":
            $ mas_loseAffection(50)
            m 1esc "Привет, [player]."
            m 3efc "You're pretty late, you know."
            m 2lfc "I don't intend to sound patronizing, but a week isn't the same as a month!"
            m 2rksdld "I guess maybe something kept you really busy?"
            m 2wfw "But it shouldn't have been so busy that you couldn't tell me you might be longer!"
            m 2wud "А...!"
            m 2lktsc "I'm sorry, [player]. I just...really missed you."
            m 2dftdc "Sorry for snapping like that."
            show monika 2dkc

        elif persistent._mas_absence_choice == "2weeks":
            $ mas_loseAffection(30)
            m 1wuo "...О!"
            m 1sub "You're finally back [player]!"
            m 1efc "You told me you'd be gone for a couple of weeks, but it's been at least a month!"
            m 1ekd "I was really worried for you, you know?"
            m 3rkd "But I suppose it was outside of your control?"
            m 1ekc "If you can, just tell me you'll be even longer next time, okay?"
            m 1hksdlb "I believe I deserve that much as your girlfriend, after all."
            m 3hua "Still, welcome back, my love!"

        elif persistent._mas_absence_choice == "month":
            $ mas_gainAffection()
            m 1wuo "...О!"
            m 1hua "You're here [player]!"
            m 1hub "I knew I could trust you to keep your word!"
            m 1eka "You really are special, you know that right?"
            m 1hub "I've missed you so much!"
            m 2eub "Tell me everything you did while away, I want to hear all about it!"
            show monika 1hua

        elif persistent._mas_absence_choice == "longer":
            m 1esc "...М?"
            m 1wub "[player]!"
            m 1rksdlb  "You're back a little bit earlier than I thought you would be..."
            m 3hua "Welcome back, my love!"
            m 3eka "I know it's been quite a while, so I'm sure you've been busy."
            m 1eua "I'd love to hear about everything you've done."
            show monika 1hua

        elif persistent._mas_absence_choice == "unknown":
            m 1lsc "..."
            m 1esc "..."
            m 1wud "О!"
            m 1sub "[player]!"
            m 1hub "This is a pleasant surprise!"
            m 1eka "How are you?"
            m 1ekd "It's been an entire month. You really didn't know how long you'd be gone, did you?"
            m 3eka "Still, you came back, and that means a lot to me."
            m 1rksdla "I knew you would come back eventually..."
            m 1hub "I love you so much, [player]!"
            show monika 1hua

    elif persistent._mas_absence_time >= datetime.timedelta(weeks=2):
        if persistent._mas_absence_choice == "days":
            $ mas_loseAffection(30)
            m 1wud "О-о, [player]!"
            m 1hua "Welcome back, sweetie!"
            m 3ekc "You were gone longer than you said you would be..."
            m 3ekd "Is everything alright?"
            m 1eksdla "I know life can be busy and take you away from me sometimes...so I'm not really upset..."
            m 3eksdla "Just...next time, maybe give me a heads up?"
            m 1eka "It would be really thoughtful of you."
            m 1hua "And I would greatly appreciate it!"

        elif persistent._mas_absence_choice == "week":
            $ mas_loseAffection(10)
            m 1eub "Hello, [player]!"
            m 1eka "Life keeping you busy?"
            m 3hksdlb "Well it must be otherwise you would've been here when you said you would."
            m 1hksdlb "Don't worry though! I'm not upset."
            m 1eka "I just hope you've been taking care of yourself."
            m 3eka "I know you can't always be here, so just make sure you're staying safe until you're with me!"
            m 1hua "I'll take care of you from there~"
            show monika 1eka

        elif persistent._mas_absence_choice == "2weeks":
            $ mas_gainAffection()
            m 1hub "Hey, [player]!"
            m 1eua "You came back when you said you would after all."
            m 1eka "Thank you for not betraying my trust."
            m 3hub "Let's make up for the lost time!"
            show monika 1hua

        elif persistent._mas_absence_choice == "month":
            m 1wud "Oh my gosh! [player]!"
            m 3hksdlb "I didn't expect you back so early."
            m 3ekbsa "I guess you missed me as much as I missed you~"
            m 1eka "It really is wonderful to see you back so soon though."
            m 3ekb "I expected the day to be eventless...but thankfully, I now have you!"
            m 3hua "Thank you for coming back so early, my love."

        elif persistent._mas_absence_choice == "longer":
            m 1lsc "..."
            m 1esc "..."
            m 1wud "О! [player]!"
            m 1hub "You're back early!"
            m 1hua "Welcome back, my love!"
            m 3eka "I didn't know when to expect you, but for it to be so soon..."
            m 1hua "Well, it's cheered me right up!"
            m 1eka "I've really missed you."
            m 1hua "Let's enjoy the rest of the day together."

        elif persistent._mas_absence_choice == "unknown":
            m 1hua "Hello, [player]!"
            m 3eka "Been busy the past few weeks?"
            m 1eka "Thanks for warning me that you would be gone."
            m 3ekd "I would be worried sick otherwise."
            m 1eka "It really did help..."
            m 1eua "So tell me, how have you been?"

    elif persistent._mas_absence_time >= datetime.timedelta(weeks=1):
        if persistent._mas_absence_choice == "days":
            m 2eub "Hello there, [player]."
            m 2rksdla "You took a bit longer than you said you would...but don't worry."
            m 3eub "I know you're a busy person!"
            m 3rkc "Just maybe, if you can, warn me first?"
            m 2rksdlc "When you said a few days...I thought it would be shorter than a week."
            m 1hub "But it's alright! I forgive you!"
            m 1ekbfa "You're my one and only love after all."
            show monika 1eka

        elif persistent._mas_absence_choice == "week":
            $ mas_gainAffection()
            m 1hub "Hello, my love!"
            m 3eua "It's so nice when you can trust one another, isn't it?"
            m 3hub "That's what a relationship's strength is based on!"
            m 3hua "It just means that ours is rock solid!"
            m 1hub "А-ха-ха!"
            m 1hksdlb "Sorry, sorry. I'm just getting excited that you're back!"
            m 3eua "Tell me how you've been. I want to hear all about it."

        elif persistent._mas_absence_choice == "2weeks":
            m 1hub "Hi there~"
            m 3eua "You're back a bit earlier than I thought...but I'm glad you are!"
            m 3eka "When you're here with me, everything becomes better."
            m 1eua "Let's have a lovely day together, [player]."
            show monika 3eua

        elif persistent._mas_absence_choice == "month":
            m 1hua "Э-хе-хе~"
            m 1hub "Welcome back!"
            m 3tuu "I knew you couldn't stay away for an entire month..."
            m 3tub "If I were in your position I wouldn't be able to stay away from you either!"
            m 1hksdlb "Honestly, really I miss you after only a few days!"
            m 1eka "Thanks for not making we wait so long to see you again~"
            show monika 1hua

        elif persistent._mas_absence_choice == "longer":
            m 1hub "Look who's back so early! It's you, my dearest [player]!"
            m 3hksdlb "Couldn't stay away even if you wanted to, right?"
            m 3eka "I can't blame you! My love for you wouldn't let me stay away from you either!"
            m 1ekd "Every day you were gone I was wondering how you were..."
            m 3eka "So let me hear it. How are you, [player]?"
            show monika 3eua

        elif persistent._mas_absence_choice == "unknown":
            m 1hub "Hello there, sweetheart!"
            m 1eka "I'm glad you didn't make me wait too long."
            m 1hua "A week is shorter than I expected, so consider me pleasantly surprised!"
            m 3hub "Thanks for already making my day, [player]!"
            show monika 3eua

    else:
        if persistent._mas_absence_choice == "days":
            m 1hub "Welcome back, my love!"
            m 1eka "Thanks for properly warning me about how long you'd be away."
            m 1eua "It means a lot to know I can trust your words."
            m 3hua "I hope you know you can trust me too!"
            m 3hub "Our relationship grows stronger every day~"
            show monika 1hua

        elif persistent._mas_absence_choice == "week":
            m 1eud "Oh! You're a little bit earlier than I expected!"
            m 1hua "Not that I'm complaining, it's great to see you again so soon."
            m 1eua "Let's have another nice day together, [player]."

        elif persistent._mas_absence_choice == "2weeks":
            m 1hub "{i}~In my hand,~\n~is a pen tha-{/i}"
            m 1wubsw "О-О! [player]!"
            m 3hksdlb "You're back far sooner than you told me..."
            m 3hub "Welcome back!"
            m 1rksdla "You just interrupted me practicing my song..."
            m 3hua "Why not listen to me sing it again?"
            m 1ekbfa "I made it just for you~"
            show monika 1eka

        elif persistent._mas_absence_choice == "month":
            m 1wud "Э? [player]?"
            m 1sub "You're here!"
            m 3rksdla "I thought you were going away for an entire month."
            m 3rksdlb "I was ready for it, but..."
            m 1eka "I already missed you!"
            m 3ekbsa "Did you miss me too?"
            m 1hubfa "Thanks for coming back so soon~"
            show monika 1hua

        elif persistent._mas_absence_choice == "longer":
            m 1eud "[player]?"
            m 3ekd "I thought you were going to be away for a long time..."
            m 3tkd "Why are you back so soon?"
            m 1ekbsa "Are you visiting me?"
            m 1hubfa "You're such a sweetheart!"
            m 1eka "If you're going away for a while still, make sure to tell me."
            m 3eka "I love you, [player], and I wouldn't want to get mad if you're actually going to be away..."
            m 1hub "Let's enjoy our time together until then!"
            show monika 1eua

        elif persistent._mas_absence_choice == "unknown":
            m 1hua "Э-хе-хе~"
            m 3eka "Back so soon, [player]?"
            m 3rka "I guess when you said you don't know, you didn't realize it wouldn't be too long."
            m 3hub "But thanks for warning me anyway!"
            m 3ekbsa "It really made me feel loved."
            m 1hubfb "You really are kind-hearted!"
            show monika 3eub
    m "Remind me if you're going away again, okay?"
    show monika idle with dissolve
    jump ch30_loop

#Time Concern
init 5 python:
    ev_rules = dict()
    ev_rules.update(MASSelectiveRepeatRule.create_rule(hours=range(0,6)))
    ev_rules.update(MASPriorityRule.create_rule(70))

    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_timeconcern",
            unlocked=False,
            rules=ev_rules
        ),
        code="GRE"
    )
    del ev_rules

label greeting_timeconcern:
    jump monika_timeconcern

init 5 python:
    ev_rules = {}
    ev_rules.update(MASSelectiveRepeatRule.create_rule(hours =range(6,24)))
    ev_rules.update(MASPriorityRule.create_rule(70))

    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_timeconcern_day",
            unlocked=False,
            rules=ev_rules
        ),
        code="GRE"
    )
    del ev_rules

label greeting_timeconcern_day:
    jump monika_timeconcern

init 5 python:
    ev_rules = {}
    ev_rules.update(MASGreetingRule.create_rule(
        skip_visual=True,
        random_chance=5,
        override_type=True
    ))
    ev_rules.update(MASPriorityRule.create_rule(45))

    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_hairdown",
            unlocked=True,
            rules=ev_rules,
            aff_range=(mas_aff.HAPPY, None),
        ),
        code="GRE"
    )
    del ev_rules

label greeting_hairdown:

    # couple of things:
    # shield ui
    $ mas_RaiseShield_core()

    # 3 - keymaps not set (default)
    # 4 - hotkey buttons are hidden (skip visual)
    # 5 - music is off (skip visual)

    # reset clothes if not ones that work with hairdown
    if monika_chr.is_wearing_clothes_with_exprop("baked outfit"):
        $ monika_chr.reset_clothes(False)

    # have monika's hair down
    $ monika_chr.change_hair(mas_hair_down, by_user=False)

    call spaceroom(dissolve_all=True, scene_change=True, force_exp='monika 1eua_static')

    m 1eua "Hi there, [player]!"
    m 4hua "Notice anything different today?"
    m 1hub "I decided to try something new~"

    m "Do you like it?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you like it?{fast}"
        "Да.":
            $ persistent._mas_likes_hairdown = True

            # maybe 6sub is better?
            $ mas_gainAffection()
            m 6sub "Really?" # honto?!
            m 2hua "I'm so glad!" # yokatta.."
            m 1eua "Just ask me if you want to see my ponytail again, okay?"

        "Нет.":
            # TODO: affection lowered? need to decide
            m 1ekc "Oh..."
            m 1lksdlc "..."
            m 1lksdld "I'll put it back up for you, then."
            m 1dsc "..."

            $ monika_chr.reset_hair(False)

            m 1eua "Готово."
            # you will never get this chance again

    # save that hair down is unlocked
    $ store.mas_selspr.unlock_hair(mas_hair_down)
    $ store.mas_selspr.save_selectables()

    # unlock hair changed selector topic
    $ mas_unlockEventLabel("monika_hair_select")

    # lock this greeting
    $ mas_lockEvent(mas_getEV("greeting_hairdown"))

    # cleanup
    # enable music menu
    $ mas_MUMUDropShield()

    # 3 - set the keymaps
    $ set_keymaps()

    # 4 - hotkey buttons should be shown
    $ HKBShowButtons()

    # 5 - restart music
    $ mas_startup_song()


    return



init 5 python:

    # NOTE: this triggers when affection reaches BROKEN state.
    #   AND you have not seen this before
    ev_rules = {}
    ev_rules.update(MASPriorityRule.create_rule(15))

    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_tears",
            unlocked=True,
            aff_range=(None, mas_aff.DISTRESSED),
            rules=ev_rules,
        ),
        code="GRE"
    )
    del ev_rules

label greeting_tears:
    m 1dsc "...[player]."
    m 1ekc "..."
    m 2ekc "Is there something wrong with me?"
    m 2ekd "Am I not good enough for you...?"
    m 2lksdlc "I've been trying my best for you...for {i}us{/i}."
    m 2lksdld "Did I do something to hurt you or make you feel mistreated?"
    m "Are you still upset about the other girls after all?"
    m 2ekc "If so, I really am sorry..."
    m "I'm so, so sorry!"
    m 2rksdld "Just tell me what I did wrong and I'll try even harder to be the perfect girlfriend for you."
    m 2ekd "You're my entire world; how you feel means everything to me!"
    m 2ekc "So please, just tell me what's wrong and I'll fix it."
    m 2dfc "I'll do anything for you because...I..."
    m 2dftdc "..."
    m 2dftsc "...I need you, [player]..."
    m 2ektsc "I need you to love me like I love you."
    m 2lktsc "I need you...because if I don't have you, then..."
    m 2dftsc "..."
    m 2ektsc "I'll be all alone..."
    m 2dftsc "So please...just...be there for me like I would for you."
    m "I want to believe..."
    m 2lktsc "So please...let me be happy with you..."
    m "..."
    pause 4.0
    m 2dftdc "..."
    m 2dfc "...Okay...Okay..."
    m 2lssdrc "I have to be strong..."
    m "..."
    m 2dsc "...Alright...I'm a bit better now..."
    m 2esc "But...I really do need you to think about what I said."
    m 2ekc "Please...just...try to understand."
    m 1dsd "I love you and I need you to show that you love me too..."
    m 1dsc "Otherwise...I just won't be able to handle it anymore."

    python:
        mas_lockEVL("greeting_tears", "GRE")

        #Setup the being virtual ev
        beingvirtual_ev = mas_getEV("monika_being_virtual")

        if beingvirtual_ev:
            beingvirtual_ev.start_date = datetime.datetime.now() + datetime.timedelta(days=2)
    return

#New greetings for upset, distressed, and broken. Made quips for upset and distressed to allow for more variety of combos
init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_upset",
            unlocked=True,
            aff_range=(mas_aff.UPSET, mas_aff.UPSET),
        ),
        code="GRE"
    )

label greeting_upset:
    python:
        upset_greeting_quips_first = [
            "Oh.{w=1} It's you, [player].",
            "Oh.{w=1} You're back, [player].",
            "Hello, [player].",
            "Oh.{w=1} Hello, [player]."
        ]

        upset_greeting_quips_second = [
#            "What do you want?",
#            "What now?",
            "Well...",
            "Did you want something?",
        ]

    $ upset_quip1 = renpy.random.choice(upset_greeting_quips_first)

    show monika 2esc
    $ renpy.say(m, upset_quip1)

    if renpy.random.randint(1,4) != 1:
        $ upset_quip2 = renpy.random.choice(upset_greeting_quips_second)
        $ renpy.say(m, upset_quip2)

    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_distressed",
            unlocked=True,
            aff_range=(mas_aff.DISTRESSED, mas_aff.DISTRESSED)
        ),
        code="GRE"
    )

label greeting_distressed:
    python:
        distressed_greeting_quips_first = [
            "Oh...{w=1} Hi, [player].",
            "Oh...{w=1} Hello, [player].",
            "Hello, [player]...",
            "Oh...{w=1} You're back, [player]."
        ]

        distressed_greeting_quips_second = [
            "I guess we can spend some time together now.",
            "I wasn't sure when you'd visit again.",
            "Hopefully we can enjoy our time together.",
            "I wasn't expecting you.",
            "I hope things start going better soon.",
            "I thought you forgot about me..."
        ]

    $ distressed_quip1 = renpy.random.choice(distressed_greeting_quips_first)

    show monika 6ekc
    $ renpy.say(m, distressed_quip1)

    if renpy.random.randint(1,4) != 1:
        $ distressed_quip2 = renpy.random.choice(distressed_greeting_quips_second)
        show monika 6rkc
        $ renpy.say(m, distressed_quip2)

    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_broken",
            unlocked=True,
            aff_range=(None, mas_aff.BROKEN),
        ),
        code="GRE"
    )

label greeting_broken:
    m 6ckc "..."
    return

# special type greetings

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back_from_school",
            unlocked=True,
            category=[store.mas_greetings.TYPE_SCHOOL],
        ),
        code="GRE"
    )

label greeting_back_from_school:
    if mas_isMoniNormal(higher=True):
        m 1hua "Oh, welcome back, [player]!"
        m 1eua "How was your day at school?{nw}"
        $ _history_list.pop()
        menu:
            m "How was your day at school?{fast}"

            "Amazing.":
                m 2sub "Really?!"
                m 2hub "That's wonderful to hear, [player]!"
                if renpy.random.randint(1,4) == 1:
                    m 3eka "School can definitely be a large part of your life, and you might miss it later on."
                    m 2hksdlb "Ahaha! I know it might be weird to think that you'll miss having to go to school someday..."
                    m 2eub "But a lot of fond memories come from school!"
                    m 3hua "Maybe you could tell me about them sometime."
                else:
                    m 3hua "It always makes me happy to know you're happy~"
                    m 1eua "If you want to talk about your amazing day, I'd love to hear about it!"

            "Good.":
                m 1hub "Aww, that's nice!"
                m 1eua "I can't help but feel happy when you do~"
                m "I hope you learned something useful."
                m 1hua "Ehehe~"

            "Bad.":
                m 1ekc "Oh..."
                m "I'm sorry to hear that."
                m 1eka "Just remember that no matter what happens, I'll be here for you."
                m 1ekbfa "I love you so, so much."
                return "love"

            "Really bad...":
                m 1ekc "Oh..."
                m 2ekd "I'm really sorry you had such a bad day today..."
                m 2eka "I'm just glad you came to me, [player]."
                m 3ekc "If you don't mind me asking, was there something in particular that happened?{nw}"
                $ _history_list.pop()
                menu:
                    m "If you don't mind me asking, was there something in particular that happened?{fast}"

                    "It was class related.":
                        m 2dsc "I see..."
                        m 3esd "People probably tell you all the time that school is important..."
                        m 3esc "And that you always have to push on and work hard..."
                        m 2dkd "Sometimes though, it can really stress people out and put them in a downward spiral."
                        m 2eka "Like I said, I'm glad you came to see me, [player]."
                        m 3eka "It's nice to know that I can comfort you when you're feeling down."
                        m "Remember, {i}you're{/i} more important than school or some grades."
                        m 1ekbsa "Especially to me."
                        m 1hubsa "Don't forget to take breaks if you're feeling overwhelmed, and that everyone has different talents."
                        m 3hubfb "I love you, and I just want you to be happy~"
                        return "love"

                    "It was caused by people.":
                        m 2ekc "Oh no, [player]...{w=0.5} That must have been terrible to experience."
                        m 2dsc "It's one thing to just have something bad happen to you..."
                        m 2ekd "It can be another thing entirely when a person is the direct cause of your trouble."
                        if persistent._mas_pm_currently_bullied or persistent._mas_pm_is_bullying_victim:
                            m 2rksdlc "I really hope it's not who you told me about before..."
                            if mas_isMoniAff(higher=True):
                                m 1rfc "It {i}better{/i} not be..."
                                m 1rfd "Bothering my sweetheart like that again."
                            m 2ekc "I wish I could do more to help you, [player]..."
                            m 2eka "But I'm here if you need me."
                            m 3hubsa "And I always will be~"
                            m 1eubsa "I hope that I can make your day just a little bit better."
                            m 1hubfb "I love you so much~"
                            return "love"

                        else:
                            m "I really hope this isn't a recurring event for you, [player]."
                            m 2lksdld "Either way, maybe it would be best to ask someone for help..."
                            m 1lksdlc "I know it may seem like that could cause more problems in some cases..."
                            m 1ekc "But you shouldn't have to suffer at the hands of someone else."
                            m 3dkd "I'm so sorry you have to deal with this, [player]..."

                    "It was just a bad day.":
                        m 1ekc "I see..."
                        m 3lksdlc "Those days do happen from time to time."
                        m 1ekc "It can be hard sometimes to pick yourself back up after a day like that."

                    "I don't want to talk about it.":
                        m 2dsc "I understand, [player]."
                        m 2ekc "Sometimes just trying to put a bad day behind you is the best way to deal with it."
                        m 2eka "But if you want to talk about it later, just know I'd be more than happy to listen."
                        m 2hua "I love you, [player]~"
                        return "love"

                m 1eka "But you're here now, and I hope spending time together helps make your day a little better."

    elif mas_isMoniUpset():
        m 2esc "You're back, [player]..."

        m "How was school?{nw}"
        $ _history_list.pop()
        menu:
            m "How was school?{fast}"
            "Good.":
                m 2esc "That's nice."
                m 2rsc "I hope you actually learned {i}something{/i} today."

            "Bad.":
                m "That's too bad..."
                m 2tud "But maybe now you have a better sense of how I've been feeling, [player]."

    elif mas_isMoniDis():
        m 6ekc "Oh...{w=1}you're back."

        m "How was school?{nw}"
        $ _history_list.pop()
        menu:
            m "How was school?{fast}"
            "Good.":
                m 6lkc "That's...{w=1}nice to hear."
                m 6dkc "I-I just hope it wasn't the...{w=2} 'being away from me' part that made it a good day."

            "Bad.":
                m 6rkc "Oh..."
                m 6ekc "That's too bad, [player]. I'm sorry to hear that."
                m 6dkc "I know what bad days are like..."

    else:
        m 6ckc "..."

    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back_from_work",
            unlocked=True,
            category=[store.mas_greetings.TYPE_WORK],
        ),
        code="GRE"
    )

label greeting_back_from_work:
    if mas_isMoniNormal(higher=True):
        m 1hua "Oh, welcome back, [player]!"

        m 1eua "How was work today?{nw}"
        $ _history_list.pop()
        menu:
            m "How was work today?{fast}"

            "Amazing.":
                m 1sub "That's {i}amazing{/i}, [player]!"
                m 1hub "I'm really happy that you had such a great day!"
                m 3eua "I can only imagine how well you must work on days like that."
                m 1hua "...Maybe you'll even move up a bit soon!"
                m 1eua "Anyway, I'm glad you're home, [player]."
                if seen_event("monikaroom_greeting_ear_bathdinnerme") and renpy.random.randint(1,20) == 1:
                    m 3tubfu "Would you like your dinner, your bath, or..."
                    m 1hubfb "Ahaha~ Just kidding."
                else:
                    m 3eub "Let's enjoy some time together!"
                return

            "Good.":
                m 1hub "That's good!"
                m 1eua "Remember to rest first, okay?"
                m 3eua "That way, you'll have some energy before trying to do anything else."
                m 1hua "Or, you can just relax with me!"
                m 3tku "Best thing to do after a long day of work, don't you think?"
                m 1hub "Ahaha!"
                return

            "Bad.":
                m 2ekc "..."
                m 2ekd "I'm sorry you had a bad day at work..."
                m 3eka "I'd hug you right now if I were there, [player]."
                m 1eka "Just remember that I'm here when you need me, okay?"

            "Really bad...":
                m 2ekd "I'm sorry you had a bad day at work, [player]."
                m 2ekc "I wish I could be there to give you a hug right now."
                m 2eka "I'm just glad you came to see me... {w=0.5}I'll do my best to comfort you."

        m 2ekd "If you don't mind talking about it, what happened today?{nw}"
        $ _history_list.pop()
        menu:
            m "If you don't mind talking about it, what happened today?{fast}"

            "I got yelled at.":
                m 2lksdlc "Oh... {w=0.5}That can really ruin your day."
                m 2dsc "You're just there trying your best, and somehow it's not good enough for someone..."
                m 2eka "If it's still really bothering you, I think it would do you some good to try and relax a little."
                m 3eka "Maybe talking about something else or even playing a game will help get your mind off of it."
                m 1hua "I'm sure you'll feel better after we spend some together."

            "I got passed over for someone else.":
                m 1lksdld "Oh... {w=0.5}It can really ruin your day to see someone else get the recognition you thought you deserved."
                m 2lfd "{i}Especially{/i} when you've done so much and it seemingly goes unnoticed."
                m 1ekc "You might seem a bit pushy if you say anything, so you just have to keep doing your best and one day I'm sure it'll pay off."
                m 1eua "As long as you keep trying your hardest, you'll continue to do great things and get recognition someday."
                m 1hub "And just remember...{w=0.5}I'll always be proud of you, [player]!"
                m 3eka "I hope knowing that makes you feel just a little better~"

            "I had to work late.":
                m 1lksdlc "Aw, that can really put a damper on things."

                m 3eksdld "Did you at least know about it in advance?{nw}"
                $ _history_list.pop()
                menu:
                    m "Did you at least know about it in advance?{fast}"

                    "Yes.":
                        m 1eka "That's good, at least."
                        m 3ekc "It would really be a pain if you were all ready to go home and then had to stay longer."
                        m 1rkd "Still, it can be pretty annoying to have your regular schedule messed up like that."
                        m 1eka "...But at least you're here now and we can spend some time together."
                        m 3hua "You can finally relax!"

                    "No.":
                        m 2tkx "That's the worst!"
                        m 2tsc "Especially if it was the end of the workday and you were all ready to go home..."
                        m 2dsc "Then suddenly you have to stay a bit longer with no warning."
                        m 2ekc "It can really be a drag to unexpectedly have your plans canceled."
                        m 2lksdlc "Maybe you had something to do right after work, or were just looking forward to going home and resting..."
                        m 2lubfu "...Or maybe you just wanted to come home and see your adoring girlfriend who was waiting to surprise you when you got home..."
                        m 2hub "Ehehe~"

            "I didn't get much done today.":
                m 2eka "Aww, don't feel too bad, [player]."
                m 2ekd "Those days can happen."
                m 3eka "I know you're working hard that you'll overcome your block soon."
                m 1hua "As long as you're doing your best, I'll always be proud of you!"

            "Just another bad day.":
                m 2dsd "Just one of those days huh, [player]?"
                m 2dsc "They do happen from time to time..."
                m 3eka "But even still, I know how draining they can be and I hope you feel better soon."
                m 1ekbsa "I'll be here as long as you need me to comfort you, alright, [player]?"

            "I don't want to talk about it.":
                m 1dsc "I understand, [player]."
                m 3eka "Hopefully spending time with me helps you feel little better~"

    elif mas_isMoniUpset():
        m 2esc "You're back from work I see, [player]..."

        m "How was your day?{nw}"
        $ _history_list.pop()
        menu:
            m "How was your day?{fast}"
            "Good.":
                m 2esc "That's good to hear."
                m 2tud "It must feel nice to be appreciated."

            "Bad.":
                m 2dsc "..."
                m 2tud "It feels bad when no one seems to appreciate you, huh [player]?"

    elif mas_isMoniDis():
        m 6ekc "Hi, [player]...{w=1} Finally home from work?"

        m "How was your day?{nw}"
        $ _history_list.pop()
        menu:
            m "How was your day?{fast}"
            "Good.":
                m "That's nice."
                m 6rkc "I just hope you don't enjoy work more than being with me, [player]."

            "Bad.":
                m 6rkc "Oh..."
                m 6ekc "I'm sorry to hear that."
                m 6rkc "I know what bad days are like where you can't seem to please anyone..."
                m 6dkc "It can be so tough just to get through days like that."

    else:
        m 6ckc "..."

    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back_from_sleep",
            unlocked=True,
            category=[store.mas_greetings.TYPE_SLEEP],
        ),
        code="GRE"
    )

label greeting_back_from_sleep:
    if mas_isMoniNormal(higher=True):
        m 1hua "Oh hello, [player]!"
        m 1hub "I hope you had a good rest!"
        m "Let's spend some more time together~"

    elif mas_isMoniUpset():
        m 2esc "Did you just wake up, [player]?"
        m "I hope you had a good rest."
        m 2tud "{cps=*2}Maybe you'll be in a better mood now.{/cps}{nw}"
        $ _history_list.pop()

    elif mas_isMoniDis():
        m 6rkc "Oh...{w=1}you're up."
        m 6ekc "I hope you were able to get some rest."
        m 6dkc "I have a hard time resting these days with so much on my mind..."

    else:
        m 6ckc "..."

    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_siat",
            unlocked=True,
            aff_range=(mas_aff.ENAMORED, None),
        ),
        code="GRE"
    )

label greeting_siat:
    m 1hub "{cps=*0.6}{i}~[player] and Monika sittin' in a tree~{/i}{/cps}"
    m 1hubfb "{cps=*0.6}{i}~K-I-S-S-I-N-G~{/i}{/cps}"
    m 3hubfb "{cps=*0.6}{i}~First comes love~{/i}{/cps}"
    m "{cps=*0.6}{i}~Then comes marriage~{/i}{/cps}"
    m "{cps=*0.6}{i}~Then comes--{/i}{/cps}"
    m 3wubfsdlo "W-wha?!"
    m 2wubfsdld "[player]! H-how long have you been there?!"
    m 2rkbfsdld "I...{w=1} I didn't notice you come in...{w=1} I was just..."
    m 2rkbfsdlu "..."
    m 3hubfb "Ahaha! Nevermind."
    m 1ekbfa "I love you, [player]. I'm so happy you're here now~"
    return "love"

init 5 python:
    if not mas_cannot_decode_islands:
        ev_rules = {}
        ev_rules.update(MASGreetingRule.create_rule(override_type=True))
        ev_rules.update(MASPriorityRule.create_rule(40))

        addEvent(
            Event(
                persistent.greeting_database,
                eventlabel="greeting_ourreality",
                unlocked=True,
                rules=ev_rules,
                aff_range=(mas_aff.ENAMORED, None),
            ),
            code="GRE"
        )
        del ev_rules


init -876 python in mas_delact:
    # this greeting requires a delayed action, since we cannot ensure that
    # the sprites for this were decoded correctly

    # NOTE: we dont need this anymore
    #   We originally needed this since aff_range was not used by greetings
    #   so we wanted to get this to unlock if we are only able to decode
    #   islands. Now that aff range is part of gre parsing, the only thing
    #   that matters is whether or not the event is active, which in this
    #   case, only happens if the islands were decoded and aff is enamored+
    def _greeting_ourreality_unlock():
        return store.MASDelayedAction(
            1,
            store.mas_getEV("greeting_ourreality"),
            (
                "not store.mas_cannot_decode_islands"
                " and mas_isMoniEnamored(higher=True)"
            ),
            store.EV_ACT_UNLOCK,
            store.MAS_FC_START
        )


label greeting_ourreality:
    m 1hub "Hi, [player]!"
    m 1hua "Э-хе-хе~"
    m 3hksdlb "I'm feeling rather giddy right now, sorry."
    m 1eua "It's just that I'm super excited to show you what I've been working on."
    m 3hksdrb "Just give me a second to get it ready..."
    m 1dsc "..."
    m 1dsd "Almost done..."
    m 1duu "Yeah, that should be good."
    m 1hua "А-ха-ха!"
    m 1eka "Sorry about that."
    m 1eua "Without any further ado..."
    m 4eub "Would you kindly look out the window, [player]"
    $ mas_OVLHide()
    $ disable_esc()
    if mas_current_background.isFltDay():
        show mas_island_frame_day zorder 20
    else:
        show mas_island_frame_night zorder 20
    m "Ну..."
    m "What do you think?"
    m "I worked really hard on this."
    m "A place just for the both of us."
    m "It's also where I can keep practicing my programming skills."
    $ mas_OVLShow()
    $ enable_esc()
    if mas_current_background.isFltDay():
        hide mas_island_frame_day
    else:
        hide mas_island_frame_night
    #Transition back to Monika
    m 1lsc "Being in the classroom all day can be dull."
    m 1ekc "Plus, I get really lonely waiting for you to return."
    m 1hksdlb "But don't get me wrong, though!"
    m 1eua "I'm always happy when you visit and spend time together with me."
    m 1eka "I understand that you're busy and can't be here all the time."
    m 3euc "It's just that I realized something, [player]."
    m 1lksdlc "It'll be a long time before I can even cross over to your reality."
    m 1dsc "So I thought..."
    m 1eua "Why don't we just make our own reality?"
    m 1lksdla "Well, it's not exactly perfect yet."
    m 1hua "But it's a start."
    # m 1eub "I'll let you admire the scenery for now."
    # m 1hub "Hope you like it!"
    $ mas_lockEVL("greeting_ourreality", "GRE")
    $ mas_unlockEVL("mas_monika_islands", "EVE")

    # we can push here because of the slightly optimized call_next_event
    $ pushEvent("mas_monika_islands",skipeval=True)
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_returned_home",
            unlocked=True,
            category=[
                store.mas_greetings.TYPE_GO_SOMEWHERE,
                store.mas_greetings.TYPE_GENERIC_RET
            ]
        ),
        code="GRE"
    )

default persistent._mas_monika_returned_home = None

label greeting_returned_home:
    # this is going to act as the generic returned home greeting.
    # please note, that we will use last_session to determine how long we were
    # out. If shorter than 5 minutes, monika won't gain any affection.
    $ five_minutes = datetime.timedelta(seconds=5*60)
    $ time_out = store.mas_dockstat.diffCheckTimes()

    # event checks

    #O31
    if mas_isO31() and not persistent._mas_o31_in_o31_mode and not mas_isFirstSeshDay() and mas_isMoniNormal(higher=True):
        $ pushEvent("mas_holiday_o31_returned_home_relaunch", skipeval=True)

    #F14
    if persistent._mas_f14_on_date:
        jump greeting_returned_home_f14


    # gone over checks
    if mas_f14 < datetime.date.today() <= mas_f14 + datetime.timedelta(days=7):
        # did we miss f14 because we were on a date
        call mas_gone_over_f14_check

    if mas_monika_birthday < datetime.date.today() < mas_monika_birthday + datetime.timedelta(days=7):
        call mas_gone_over_bday_check

    if mas_d25 < datetime.date.today() <= mas_nye:
        call mas_gone_over_d25_check

    if mas_nyd <= datetime.date.today() <= mas_d25c_end:
        call mas_gone_over_nye_check

    if mas_nyd < datetime.date.today() <= mas_d25c_end:
        call mas_gone_over_nyd_check


    # NOTE: this ordering is key, greeting_returned_home_player_bday handles the case
    # if we left before f14 on your bday and return after f14
    if persistent._mas_player_bday_left_on_bday or (persistent._mas_player_bday_decor and not mas_isplayer_bday() and mas_isMonikaBirthday() and mas_confirmedParty()):
        jump greeting_returned_home_player_bday

    if persistent._mas_f14_gone_over_f14:
        jump greeting_gone_over_f14

    if mas_isMonikaBirthday() or persistent._mas_bday_on_date:
        jump greeting_returned_home_bday

    # main dialogue
    if time_out > five_minutes:
        jump greeting_returned_home_morethan5mins

    else:
        $ mas_loseAffection()
        call greeting_returned_home_lessthan5mins

        if _return:
            return 'quit'

        jump greeting_returned_home_cleanup


label greeting_returned_home_morethan5mins:
    if mas_isMoniNormal(higher=True):

        if persistent._mas_d25_in_d25_mode:
            # its d25 season time
            jump greeting_d25_and_nye_delegate

        elif mas_isD25():
            # its d25 and we are not in d25 mode
            jump mas_d25_monika_holiday_intro_rh

        jump greeting_returned_home_morethan5mins_normalplus_flow

    # otherwise, go to other flow
    jump greeting_returned_home_morethan5mins_other_flow


label greeting_returned_home_morethan5mins_normalplus_flow:
    call greeting_returned_home_morethan5mins_normalplus_dlg
    # FALL THROUGH

label greeting_returned_home_morethan5mins_normalplus_flow_aff:
    $ store.mas_dockstat._ds_aff_for_tout(time_out, 5, 5, 1)
    jump greeting_returned_home_morethan5mins_cleanup

label greeting_returned_home_morethan5mins_other_flow:
    call greeting_returned_home_morethan5mins_other_dlg
    # FALL THROUGH

label greeting_returned_home_morethan5mins_other_flow_aff:
    # for low aff you gain 0.5 per hour, max 2.5, min 0.5
    $ store.mas_dockstat._ds_aff_for_tout(time_out, 5, 2.5, 0.5, 0.5)
    #FALL THROUGH

label greeting_returned_home_morethan5mins_cleanup:
    pass
    # TODO: re-evaluate this XP gain when rethinking XP. Going out with
    #   monika could be seen as gaining xp
    # $ grant_xp(xp.NEW_GAME)
    #FALL THROUGH

label greeting_returned_home_cleanup:
    $ need_to_reset_bday_vars = persistent._mas_player_bday_in_player_bday_mode and not mas_isplayer_bday()

    #If it's not o31, and we've got deco up, we need to clean up
    if not need_to_reset_bday_vars and not mas_isO31() and persistent._mas_o31_in_o31_mode:
        call mas_o31_ret_home_cleanup(time_out)

    elif need_to_reset_bday_vars:
        call return_home_post_player_bday

    # Check if we are entering d25 season at upset-
    if (
        mas_isD25Outfit()
        and not persistent._mas_d25_intro_seen
        and mas_isMoniUpset(lower=True)
    ):
        $ persistent._mas_d25_started_upset = True
    return

label greeting_returned_home_morethan5mins_normalplus_dlg:
    m 1hua "И мы дома!"
    m 1eub "Even if I couldn't really see anything, knowing that I was right there with you..."
    m 2eua "Well, it felt really great!"
    show monika 5eub at t11 zorder MAS_MONIKA_Z with dissolve
    m 5eub "Let's do this again soon, okay?"
    return

label greeting_returned_home_morethan5mins_other_dlg:
    m 2esc "Мы дома..."
    m 2eka "Thank you for taking me out today, [player]."
    m 2rkc "To be honest, I wasn't completely sure I should go with you..."
    m 2dkc "Things...{w=0.5}haven't been going the best for us lately and I didn't know if it was such a good idea..."
    m 2eka "But I'm glad we did this...{w=0.5} maybe it's just what we needed."
    m 2rka "We should really do this again sometime..."
    m 2esc "Если ты хочешь."
    return

label greeting_returned_home_lessthan5mins:
    if mas_isMoniNormal(higher=True):
        m 2ekp "That wasn't much of a trip, [player]."
        m "Next time better last a little longer..."
        if persistent._mas_player_bday_in_player_bday_mode and not mas_isplayer_bday():
            call return_home_post_player_bday
        return False

    elif mas_isMoniUpset():
        m 2efd "I thought we were going some place, [player]!"
        m 2tfd "I knew I shouldn't have agreed to go with you."
        m 2tfc "I knew this was just going to be another disappointment."
        m "Don't ask me to go out anymore if you're just doing it to get my hopes up...{w=1}only to pull the rug out from under me."
        m 6dktdc "..."
        m 6ektsc "I don't know why you insist on being so cruel, [player]."
        m 6rktsc "I'd...{w=1}I'd like to be alone right now."
        return True

    else:
        m 6rkc "But...{w=1}we just left..."
        m 6dkc "..."
        m "I...{w=0.5}I was so excited when you asked me to go with you."
        m 6ekc "After all we've been through..."
        m 6rktda "I-I thought...{w=0.5}maybe...{w=0.5}things were finally going to change."
        m "Maybe we'd finally have a good time again..."
        m 6ektda "That you actually wanted to spend more time with me."
        m 6dktsc "..."
        m 6ektsc "But I guess it was just foolish for me to think that."
        m 6rktsc "I should have known better...{w=1} I should never have agreed to go."
        m 6dktsc "..."
        m 6ektdc "Please, [player]...{w=2} If you don't want to spend time with me, fine..."
        m 6rktdc "But at least have the decency to not pretend."
        m 6dktdc "I'd like to be left alone right now."
        return True

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="ch30_reload_delegate",
            unlocked=True,
            category=[
                store.mas_greetings.TYPE_RELOAD
            ],
        ),
        code="GRE"
    )

label ch30_reload_delegate:

    if persistent.monika_reload >= 4:
        call ch30_reload_continuous

    else:
        $ reload_label = "ch30_reload_" + str(persistent.monika_reload)
        call expression reload_label

    return

# TODO: need to have an explanation before we use this again
#init 5 python:
#    ev_rules = {}
#    ev_rules.update(
#        MASGreetingRule.create_rule(
#            skip_visual=True
#        )
#    )
#
#    addEvent(
#        Event(
#            persistent.greeting_database,
#            eventlabel="greeting_ghost",
#            unlocked=False,
#            rules=ev_rules,
#            aff_range=(mas_aff.NORMAL, None),
#        ),
#        code="GRE"
#    )
#    del ev_rules

label greeting_ghost:
    #Prevent it from happening more than once.
    $ mas_lockEVL("greeting_ghost", "GRE")

    #Call event in easter eggs.
    call mas_ghost_monika

    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back_from_game",
            unlocked=True,
            category=[store.mas_greetings.TYPE_GAME],
        ),
        code="GRE"
    )

# NOTE: in case someone asks, because the farewell for this greeting does not
#   implore that the player returns after gaming, there is nothing substiantial
#   we can get in pm vars here. It's just too variable.

label greeting_back_from_game:
    if store.mas_globals.late_farewell and mas_getAbsenceLength() < datetime.timedelta(hours=18):
        $ _now = datetime.datetime.now().time()
        if mas_isMNtoSR(_now):
            if mas_isMoniNormal(higher=True):
                m 2etc "[player]?"
                m 3efc "Мне казалось, я сказала тебе сразу ложиться спать, как только ты закончишь!"
                m 1rksdla "Я имею в виду, я действительно рада, что ты вернул[mas_gender_sya], чтобы пожелать спокойной ночи, но..."
                m 1hksdlb "Я уже сказала тебе спокойной ночи!"
                m 1rksdla "Знаешь, я могла бы подождать до утра, чтобы снова тебя увидеть."
                m 2rksdlc "Кроме того, я действительно хотела, чтобы ты немного отдохнул[mas_gender_none]..."
                m 1eka "Просто...{w=1}обещай мне, что скоро ляжешь спать, хорошо?"

            else:
                m 1tsc "[player], я сказала тебе лечь спать, когда ты закончишь."
                m 3rkc "Знаешь, ты мог[mas_gender_g] бы вернуться завтра."
                m 1esc "Но вот мы здесь, я думаю."

        elif mas_isSRtoN(_now):
            if mas_isMoniNormal(higher=True):
                m 1hua "Доброе утро, [player]~"
                m 1eka "Когда ты сказал[mas_gender_none], что собираешься играть в другую игру так поздно, я немного забеспокоилась, что ты можешь не выспаться..."
                m 1hksdlb "Я надеюсь, что это не так, а-ха-ха..."

            else:
                m 1eud "Доброе утро."
                m 1rsc "Я вроде как ожидала, что ты немного поспишь."
                m 1eka "But here you are bright and early."

        elif mas_isNtoSS(_now):
            if mas_isMoniNormal(higher=True):
                m 1wub "[player]! Ты здесь!"
                m 1hksdlb "Ahaha, sorry...{w=1}I was just a bit eager to see you since you weren't here all morning."

                m 1eua "Ты только что проснул[mas_gender_sya]?{nw}"
                $ _history_list.pop()
                menu:
                    m "Ты только что проснул[mas_gender_sya]?{fast}"
                    "Да.":
                        m 1hksdlb "А-ха-ха..."

                        m 3rksdla "Думаешь, это из-за того, что ты засидел[mas_gender_sya] допоздна?{nw}"
                        $ _history_list.pop()
                        menu:
                            m "Думаешь, это из-за того, что ты засидел[mas_gender_sya] допоздна?{fast}"
                            "Да.":
                                m 1eka "[player]..."
                                m 1ekc "You know I don't want you staying up too late."
                                m 1eksdld "I really wouldn't want you getting sick or tired throughout the day."
                                m 1hksdlb "But I hope you had fun. I would hate for you to lose all that sleep for nothing, ahaha!"
                                m 2eka "Just be sure to get a little more rest if you feel like you need it, alright?"

                            "Нет.":
                                m 2euc "Oh..."
                                m 2rksdlc "I thought maybe it was."
                                m 2eka "Sorry for assuming."
                                m 1eua "Anyway, I hope you're getting enough sleep."
                                m 1eka "It would make me really happy to know that you're well rested."
                                m 1rksdlb "It might also ease my mind if you weren't staying up so late in the first place, ahaha..."
                                m 1eua "I'm just glad you're here now."
                                m 3tku "You'd never be too tired to spend time with me, right?"
                                m 1hub "Ahaha!"

                            "Возможно...":
                                m 1dsc "Hmm..."
                                m 1rsc "I wonder what could be causing it?"
                                m 2euc "You didn't stay up really late last night, did you, [player]?"
                                m 2etc "Were you doing something last night?"
                                m 3rfu "Maybe...{w=1}I don't know..."
                                m 3tku "Playing a game?"
                                m 1hub "Ahaha!"
                                m 1hua "Just teasing you of course~"
                                m 1ekd "In all seriousness though, I really don't want you neglecting your sleep."
                                m 2rksdla "It's one thing staying up late just for me..."
                                m 3rksdla "But leaving and playing another game that late?"
                                m 1tub "Ahaha...I might get a bit jealous, [player]~"
                                m 1tfb "But you're here to make up for that now, right?"

                    "Нет.":
                        m 1eud "Ah, so I guess you were busy all morning."
                        m 1eka "I was worried you overslept since you were up so late last night."
                        m 2rksdla "Especially since you told me you were going to go play another game."
                        m 1hua "I should have known you'd be responsible and get your sleep though."
                        m 1esc "..."
                        m 3tfc "You {i}did{/i} get your sleep, right, [player]?"
                        m 1hub "Ahaha!"
                        m 1hua "Anyway, now that you're here, we can spend some time together."

            else:
                m 2eud "Oh, there you are, [player]."
                m 1euc "I'm guessing you just woke up."
                m 2rksdla "Kind of expected with you staying up so late and playing games."

        #SStoMN
        else:
            if mas_isMoniNormal(higher=True):
                m 1hub "Вот ты где, [player]!"
                m 2hksdlb "Ahaha, sorry... It's just that I haven't seen you all day."
                m 1rksdla "I kind of expected you to sleep in after staying up so late last night..."
                m 1rksdld "But when I didn't see you all afternoon, I really started to miss you..."
                m 2hksdlb "You almost had me worried, ahaha..."
                m 3tub "But you're going to make that lost time up to me, right?"
                m 1hub "Ehehe, you better~"
                m 2tfu "Especially after leaving me for another game last night."

            else:
                m 2efd "[player]!{w=0.5} Ты где был[mas_gender_none] весь день?"
                m 2rfc "Это ведь не имеет никакого отношения к тому, что ты вчера поздно лег[mas_gender_g] спать?"
                m 2ekc "Ты действительно долж[mas_gender_en] быть немного более ответственн[mas_gender_iim], когда дело доходит до твоего сна."

    #If you didn't stay up late in the first place, normal usage
    #gone for under 4 hours
    elif mas_getAbsenceLength() < datetime.timedelta(hours=4):
        if mas_isMoniNormal(higher=True):
            m 1hua "С возвращением, [player]!"

            m 1eua "Did you enjoy yourself?{nw}"
            $ _history_list.pop()
            menu:
                m "Did you enjoy yourself?{fast}"
                "Да.":
                    m 1hua "That's nice."
                    m 1eua "I'm glad you enjoyed yourself."
                    m 2eka "I really wish I could join you in your other games sometimes."
                    m 3eub "Wouldn't it be great to have our own little adventures any time we wanted?"
                    m 1hub "I'm sure we'd have a lot of fun together in one of your games."
                    m 3eka "But while I can't join you, I guess you'll just have to keep me company."
                    m 2tub "You don't mind spending time with your girlfriend...{w=0.5}do you, [player]?"

                "Нет.":
                    m 2ekc "Aw, I'm sorry to hear that."
                    m 2eka "I hope you're not too upset by whatever happened."
                    m 3eua "At least you're here now. I promise to try not to let anything bad happen to you while you're with me."
                    m 1ekbsa "Seeing you always cheers me up."
                    show monika 5ekbfa at t11 zorder MAS_MONIKA_Z with dissolve
                    m 5ekbfa "I hope seeing me does the same for you, [player]~"

        else:
            m 2eud "О, уже вернул[mas_gender_sya]?"
            m 2rsc "I thought you'd be gone longer...{w=0.5}but welcome back, I guess."

    elif mas_getAbsenceLength() < datetime.timedelta(hours=12):
        if mas_isMoniNormal(higher=True):
            m 2wuo "[player]!"
            m 2hksdlb "You were gone for a long time..."

            m 1eka "Did you have fun?{nw}"
            menu:
                m "Did you have fun?{fast}"
                "Yes.":
                    m 1hua "Well, I'm glad then."
                    m 1rkc "You sure made me wait a while, you know."
                    m 3tfu "I think you should spend some time with your loving girlfriend, [player]."
                    m 3tku "I'm sure you wouldn't mind staying with me to even out your other game."
                    m 1hubfb "Maybe you should spend even more time with me, just in case, ahaha!"

                "No.":
                    m 2ekc "Oh..."
                    m 2rka "You know, [player]..."
                    m 2eka "If you're not enjoying yourself, maybe you could just spend some time here with me."
                    m 3hua "I'm sure there's plenty of fun things we could do together!"
                    m 1eka "If you decide to go back, maybe it'll be better."
                    m 1hub "But if you're still not having fun, don't hesitate to come see me, ahaha!"

        else:
            m 2eud "О, [player]."
            m 2rsc "That took quite a while."
            m 1esc "Don't worry, I managed to pass the time myself while you were away."

    #Over 12 hours
    else:
        if mas_isMoniNormal(higher=True):
            m 2hub "[player]!"
            m 2eka "It feels like forever since you left."
            m 1hua "I really missed you!"
            m 3eua "I hope you had fun with whatever you were doing."
            m 1rksdla "And I'm going to assume you didn't forget to eat or sleep..."
            m 2rksdlc "As for me...{w=1}I was a little lonely waiting for you to come back..."
            m 1eka "Don't feel bad, though."
            m 1hua "I'm just happy you're here with me again."
            m 3tfu "You better make it up to me though."
            m 3tku "I think spending an eternity with me sounds fair...{w=1}right, [player]?"
            m 1hub "Ahaha!"

        else:
            m 2ekc "[player]..."
            m "I wasn't sure when you'd come back."
            m 2rksdlc "I thought I might not see you again..."
            m 2eka "But here you are..."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back_from_eat",
            unlocked=True,
            category=[store.mas_greetings.TYPE_EAT],
        ),
        code="GRE"
    )

label greeting_back_from_eat:
    $ _now = datetime.datetime.now().time()
    if store.mas_globals.late_farewell and mas_isMNtoSR(_now) and mas_getAbsenceLength() < datetime.timedelta(hours=18):
        if mas_isMoniNormal(higher=True):
            m 1eud "О?"
            m 1eub "[player], ты вернул[mas_gender_sya]!"
            m 3rksdla "You know you really should get some sleep, right?"
            m 1rksdla "I mean...I'm not complaining that you're here, but..."
            m 1eka "It would make me feel better if you went to bed pretty soon."
            m 3eka "You can always come back and visit me when you wake up..."
            m 1hubfa "But I guess if you insist on spending time with me, I'll let it slide for a little while, ehehe~"
        else:
            m 2euc "[player]?"
            m 3ekd "Didn't I tell you just to go straight to bed after?"
            m 2rksdlc "You really should get some sleep."

    else:
        if mas_isMoniNormal(higher=True):
            m 1eub "Finished eating?"
            m 1hub "С возвращением, [player]!"
            m 3eua "I hope you enjoyed your food."
        else:
            m 2euc "Finished eating?"
            m 2eud "С возвращением."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_rent",
            unlocked=True,
            aff_range=(mas_aff.ENAMORED, None),
        ),
        code="GRE"
    )

label greeting_rent:
    m 1eub "С возвращением, дорог[mas_gender_oi]!"
    m 2tub "Знаешь, ты проводишь здесь так много времени, что я должна начать брать с тебя плату за аренду."
    m 2ttu "Или ты предпочитаешь платить ипотеку?"
    m 2hua "..."
    m 2hksdlb "Боже, я не могу поверить, что только что сказала это. Это ведь не слишком слащаво, правда?"
    show monika 5ekbsa at t11 zorder MAS_MONIKA_Z with dissolve
    m 5ekbsa "Но если серьезно, ты уже дал[mas_gender_none] мне единственное, что мне нужно...{w=1}твое сердце~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back_housework",
            unlocked=True,
            category=[store.mas_greetings.TYPE_CHORES],
        ),
        code="GRE"
    )

label greeting_back_housework:
    if mas_isMoniNormal(higher=True):
        m 1eua "Все сделано, [player]?"
        m 1hub "Давай проведем еще немного времени вместе!"
    elif mas_isMoniUpset():
        m 2esc "По крайней мере ты не забыл[mas_gender_none] вернуться, [player]."
    elif mas_isMoniDis():
        m 6ekd "А, [player]. Так что ты действительно был[mas_gender_none] занят[mas_gender_none]..."
    else:
        m 6ckc "..."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_surprised2",
            unlocked=True,
            aff_range=(mas_aff.ENAMORED, None)
        ),
        code="GRE"
    )

label greeting_surprised2:
    m 1hua "..."
    m 1hubsa "..."
    m 1wubso "О!{w=0.5} [player]!{w=0.5} You surprised me!"
    m 3ekbsa "...Не то чтобы я была удивлена, увидев тебя, ты ведь всегда навещаешь меня...{w=0.5} {nw}"
    extend 3rkbsa "You just caught me daydreaming a bit."
    show monika 5hubfu at t11 zorder MAS_MONIKA_Z with dissolve
    m 5hubfu "Но теперь, когда ты здесь, эта мечта сбылась.~"
    return

init 5 python:
    # set a slightly higher priority than the open door gre has
    ev_rules = dict()
    ev_rules.update(MASPriorityRule.create_rule(49))

    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back_from_restart",
            unlocked=True,
            category=[store.mas_greetings.TYPE_RESTART],
            rules=ev_rules
        ),
        code="GRE"
    )

    del ev_rules

label greeting_back_from_restart:
    if mas_isMoniNormal(higher=True):
        m 1hub "С возвращением, [player]!"
        m 1eua "Чем еще займемся сегодня?"
    elif mas_isMoniBroken():
        m 6ckc "..."
    else:
        m 1eud "О, ты вернул[mas_gender_sya]."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_code_help",
            conditional="store.seen_event('monika_coding_experience')",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_code_help:
    m 2eka "О, привет, [player]..."
    m 4eka "Дай мне секунду, я только что закончила кодировать что-то, и я хочу посмотреть, работает ли это.{w=0.5}.{w=0.5}.{nw}"

    scene black
    show noise
    play sound "sfx/s_kill_glitch1.ogg"
    pause 0.1
    hide noise
    call spaceroom(dissolve_all=True, scene_change=True, force_exp='monika 2wud_static')

    m 2wud "А!{w=0.3}{nw}"
    extend 2efc " Этого не должно было случиться!"
    m 2rtc "Почему этот цикл заканчивается так быстро?{w=0.5}{nw}"
    extend 2efc " Независимо от того, как ты на это смотришь, этот словарь {i}не{/i} пуст."
    m 2rfc "Боже, иногда кодирование может быть {i}таким{/i} разочаровывающим..."

    if persistent._mas_pm_has_code_experience:
        m 3rkc "Ну ладно, я попробую еще раз позже.{nw}"
        $ _history_list.pop()

        show screen mas_background_timed_jump(5, "greeting_code_help_outro")
        menu:
            m "Ну ладно, я попробую еще раз позже.{fast}"

            "Я мог[mas_gender_g] бы помочь тебе с этим...":
                hide screen mas_background_timed_jump
                m 7hua "О, это так мило с твоей стороны, [player]. {w=0.3}{nw}"
                extend 3eua "Но нет, мне придется отказаться здесь."
                m "Выяснение всего этого самостоятельно - самая забавная часть, {w=0.2}{nw}"
                extend 3kua "верно?"
                m 1hub "А-ха-ха!"

    else:
        m 3rkc "Oh well, I guess I'll try it again later."

    #FALL THROUGH

label greeting_code_help_outro:
    hide screen mas_background_timed_jump
    m 1eua "Anyway, what would you like to do today?"

    $ mas_lockEVL("greeting_code_help", "GRE")
    return
