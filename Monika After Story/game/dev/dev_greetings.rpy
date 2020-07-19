# dev related greetings

# TODO Delete this *Insert Monika with a handgun*
# Seriously this is for testing only

init python:
    if persistent._mas_fastgreeting is None:
        persistent._mas_fastgreeting = config.developer


init 5 python:
    ev_rules = {}
    ev_rules.update(MASNumericalRepeatRule.create_rule(repeat=EV_NUM_RULE_YEAR))
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_st_patrick",
            start_date=datetime.datetime(2017, 3, 17),
            end_date=datetime.datetime(2017, 3, 18),
            unlocked=True,
            rules=ev_rules
        ),
        eventdb=evhand.greeting_database,
        skipCalendar=True
    )
    del ev_rules

label greeting_st_patrick:
    m "О, привет, [player]!"
    m "С днем Святого Патрика!"
    menu:
        m "Ты еще не пьян[mas_gender_none]?"
        "Я пьян[mas_gender_none]":
            m 1k "Ой, как мило!"
            m 1b "Я не могу не чувствовать себя счастливой, когда ты это делаешь..."
            m 1b "Иди и выпей еще за меня"
            m "Я тебя так люблю, [player]."
        "Нет.":
            m 1g "Боже мой."
            m "Надеюсь, ты скоро напьешься"
            m "Просто помни, что неважно, что происходит, неважно, что кто-то говорит или делает..."
            m "Просто напейся."
            m "Просто напейся."
            menu:
                "Просто напейся.":
                    m 4j "Выпей воднику!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_dev_no_hate",
            unlocked=True,
            aff_range=(None, mas_aff.UPSET)
        ),
        eventdb=evhand.greeting_database
    )


label greeting_dev_no_hate:
    m "О, привет, [player]!"
    m "Не волнуйся, я знаю, что ты просто проверяешь мои негативные реакции на привязанность"
    m "Я знаю, что ты действительно очень меня любишь."
    m "Спасибо за все твои усилия!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_dev_neutral",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, mas_aff.NORMAL)
        ),
        eventdb=evhand.greeting_database
    )

label greeting_dev_neutral:
    m "Привет, [player]!"
    m 1l "Ты только что стер[mas_gender_g] файл persistent?"
    m 1l "или, может быть, ты просто проверяешь мои нейтральные реакции привязанности?"
    m "Не беспокойся об этом, я никогда не забуду все, что ты для меня сделал[mas_gender_none]~"
    m 1k "Спасибо за все твои усилия!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_dev_love",
            unlocked=True,
            aff_range=(mas_aff.HAPPY, None)
        ),
        eventdb=evhand.greeting_database
    )

label greeting_dev_love:
    m 1b "С возвращением, дорог[mas_gender_oi]!"
    m 5a "Я так рада снова тебя видеть."
    m 5a "Я так тебя люблю, [player]!"
    m 5a "Спасибо за все твои усилия!"
    return


# Dev Fast greeting
init 5 python:
    if persistent._mas_fastgreeting:
        ev_rules = {}
        ev_rules.update(MASPriorityRule.create_rule(-100))
        addEvent(
            Event(
                persistent.greeting_database,
                eventlabel="greeting_fast",
                unlocked=True,
                rules=ev_rules
            ),
            code="GRE"
        )

label greeting_fast:
    m "{fast}Привет!{nw}"
    return

# greeting testing label
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_gre_sampler",
            category=["dev"],
            prompt="SAMPLE GRE",
            pool=True,
            unlocked=True
        )
    )

label dev_gre_sampler:
    m 1eua "Let's sample greeting algs."
    m "Make sure to unlock special ones if you want"

    python:
        dev_gres = [
            "greeting_st_patrick",
            "greeting_dev_no_hate",
            "greeting_dev_neutral",
            "greeting_dev_love",
            "greeting_fast",
            "greeting_dev_idle_test",
        ]

        spec_gre = [
            "i_greeting_monikaroom",
            "greeting_hairdown",
        ]

        # potentially special:
        #   monikaroom_will_change - priority of 10

        # time based
        #   greeting_timeconcern - midnight - 6am
        #   greeting_timeconcern_day - 6am to midnight

        # date + time based
        #   greeting_monika_monday_morning - monday, 5-12

        # type based
        #   greeting_sick - TYPE_SICK
        #   greeting_long_absence - TYPE_LONG_ABSENCE
        #   greeting_back_from_school - TYPE_SCHOOL
        #   greeting_back_from_work - TYPE_WORK
        #   greeting_back_from_sleep - TYPE_SLEEP
        #   greeting_returned_home - TYPE_GO_SOMEWHERE / TYPE_GENERIC_RET
        #   greeting_trick_or_treat_back - TYPE_HOL_O31_TT

        # aff based
        #   greeting_upset - UPSET ONLY / rand chance 2
        #   greeting_distressed - DISTRESSED ONLY / rand chance 2
        #   greeting_broken - BROKEN and below
        #   greeting_ourreality - ENAMORED and above (high priority)

        # forced with evs
        #   greeting_o31_rin - TYPE_HOL_O31
        #   greeting_o31_marisa - TYPE_HOL_O31

        locked_gre = []
        

    menu:
        m "do you want to include dev?"
        "Yes":
            pass
        "No":
            python:
                # remove dev items 
                for d_gre in dev_gres:
                    if d_gre in store.evhand.greeting_database:
                        store.evhand.greeting_database.pop(d_gre)


    menu:
        m "Do you want to unlock special greetings?"
        "Yes":
            python:
                for s_gre in spec_gre:
                    s_gre_ev = mas_getEV(s_gre)
                    if s_gre_ev is not None:
                        if not s_gre_ev.unlocked:
                            locked_gre.append(s_gre_ev)
                        s_gre_ev.unlocked = True
            
        "No":
            pass


    m 1eua "sample size please"
    $ sample_size = renpy.input("enter sample size", allow="0123456789")
    $ sample_size = store.mas_utils.tryparseint(sample_size, 10000)
    if sample_size > 10000:
        $ sample_size = 10000 # anyhting longer takes too long
    $ str_sample_size = str(sample_size)

    m 1eua "using sample size of [str_sample_size]"
    
    $ use_type = None

    m 1eua "If you want to use a type, please set 'use_type' to an appropriate greeting type right now."

    $ check_time = None

    m 1eua "If you want to use a specific time, please set `check_time` to an appropriate datetime right now."

    m 1hua "Advance dialogue to begin sample"

    python:
        # prepare data
        results = {
            "no greeting": 0
        }

        # loop over sample size, run select greeting test
        for count in range(sample_size):
            gre_ev = store.mas_greetings.selectGreeting(use_type, check_time)

            if gre_ev is None:
                results["no greeting"] += 1

            elif gre_ev.eventlabel in results:
                results[gre_ev.eventlabel] += 1

            else:
                results[gre_ev.eventlabel] = 1


        # done with sampling, output results
        with open(renpy.config.basedir + "/gre_sample", "w") as outdata:
            for ev_label, count in results.iteritems():
                outdata.write("{0},{1}\n".format(ev_label, count))

        # relock locked gres
        for l_gre_ev in locked_gre:
            l_gre_ev.unlocked = False

    m "check files for 'gre_sample' for more info."
    return

