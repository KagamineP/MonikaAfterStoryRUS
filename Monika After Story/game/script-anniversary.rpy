init -2 python in mas_anni: #needed to lower this in order to get isAnni() working for special day usage
    import store.evhand as evhand
    import store.mas_calendar as mas_cal
    import store.mas_utils as mas_utils
    import datetime

    # persistent pointer so we can use it
    __persistent = renpy.game.persistent

    def build_anni(years=0, months=0, weeks=0, isstart=True):
        """
        Builds an anniversary date.

        NOTE:
            years / months / weeks are mutually exclusive

        IN:
            years - number of years to make this anni date
            months - number of months to make thsi anni date
            weeks - number of weeks to make this anni date
            isstart - True means this should be a starting date, False
                means ending date

        ASSUMES:
            __persistent
        """
        # sanity checks
        if __persistent.sessions is None:
            return None

        first_sesh = __persistent.sessions.get("first_session", None)
        if first_sesh is None:
            return None

        if (weeks + years + months) == 0:
            # we need at least one of these to work
            return None

        # sanity checks are done

        if years > 0:
            new_date = mas_utils.add_years(first_sesh, years)

        elif months > 0:
            new_date = mas_utils.add_months(first_sesh, months)

        else:
            new_date = first_sesh + datetime.timedelta(days=(weeks * 7))

        # check for starting
        if isstart:
            return mas_utils.mdnt(new_date)

        # othrewise, this is an ending date
#        return mas_utils.am3(new_date + datetime.timedelta(days=1))
# NOTE: doing am3 leads to calendar problems
#   we'll just restrict this to midnight to midnight -1
        return mas_utils.mdnt(new_date + datetime.timedelta(days=1))

    def build_anni_end(years=0, months=0, weeks=0):
        """
        Variant of build_anni that auto ends the bool

        SEE build_anni for params
        """
        return build_anni(years, months, weeks, False)

    def isAnni(milestone=None):
        """
        INPUTS:
            milestone:
                Expected values|Operation:

                    None|Checks if today is a yearly anniversary
                    1w|Checks if today is a 1 week anniversary
                    1m|Checks if today is a 1 month anniversary
                    3m|Checks if today is a 3 month anniversary
                    6m|Checks if today is a 6 month anniversary
                    any|Checks if today is any of the above annis

        RETURNS:
            True if datetime.date.today() is an anniversary date
            False if today is not an anniversary date
        """
        #Sanity checks
        if __persistent.sessions is None:
            return False

        firstSesh = __persistent.sessions.get("first_session", None)
        if firstSesh is None:
            return False

        compare = None

        if milestone == '1w':
            compare = build_anni(weeks=1)

        elif milestone == '1m':
            compare = build_anni(months=1)

        elif milestone == '3m':
            compare = build_anni(months=3)

        elif milestone == '6m':
            compare = build_anni(months=6)

        elif milestone == 'any':
            return isAnniWeek() or isAnniOneMonth() or isAnniThreeMonth() or isAnniSixMonth() or isAnni()

        if compare is not None:
            return compare.date() == datetime.date.today()
        else:
            compare = firstSesh
            return datetime.date(datetime.date.today().year, compare.month, compare.day) == datetime.date.today() and anniCount() > 0

    def isAnniWeek():
        return isAnni('1w')

    def isAnniOneMonth():
        return isAnni('1m')

    def isAnniThreeMonth():
        return isAnni('3m')

    def isAnniSixMonth():
        return isAnni('6m')

    def isAnniAny():
        return isAnni('any')

    def anniCount():
        """
        RETURNS:
            Integer value representing how many years the player has been with Monika
        """
        #Sanity checks
        if __persistent.sessions is None:
            return 0

        firstSesh = __persistent.sessions.get("first_session", None)
        if firstSesh is None:
            return 0

        compare = datetime.date.today()

        if compare.year > firstSesh.year and datetime.date.today() < datetime.date(datetime.date.today().year, firstSesh.month, firstSesh.day):
            return compare.year - firstSesh.year - 1
        else:
            return compare.year - firstSesh.year

    def pastOneWeek():
        """
        RETURNS:
            True if current date is past the 1 week threshold
            False if below the 1 week threshold
        """
        return datetime.date.today() >= build_anni(weeks=1).date()

    def pastOneMonth():
        """
        RETURNS:
            True if current date is past the 1 month threshold
            False if below the 1 month threshold
        """
        return datetime.date.today() >= build_anni(months=1).date()

    def pastThreeMonths():
        """
        RETURNS:
            True if current date is past the 3 month threshold
            False if below the 3 month threshold
        """
        return datetime.date.today() >= build_anni(months=3).date()

    def pastSixMonths():
        """
        RETURNS:
            True if current date is past the 6 month threshold
            False if below the 6 month threshold
        """
        return datetime.date.today() >= build_anni(months=6).date()


# TODO What's the reason to make this one init 10?
init 10 python in mas_anni:

    # we are going to store all anniversaries in antther db as well so we
    # can easily reference them later.
    ANNI_LIST = [
        "anni_1week",
        "anni_1month",
        "anni_3month",
        "anni_6month",
        "anni_1",
        "anni_2",
        "anni_3",
        "anni_4",
        "anni_5",
        "anni_10",
        "anni_20",
        "anni_50",
        "anni_100"
    ]

    # anniversary database
    anni_db = dict()
    for anni in ANNI_LIST:
        anni_db[anni] = evhand.event_database[anni]


    ## functions that we need (runtime only)
    def _month_adjuster(ev, new_start_date, months, span):
        """
        Adjusts the start_date / end_date of an anniversary event.

        NOTE: do not use this for a non anniversary date

        IN:
            ev - event to adjust
            new_start_date - new start date to calculate the event's dates
            months - number of months to advance
            span - the time from the event's new start_date to end_date
        """
        ev.start_date = mas_utils.add_months(
            mas_utils.mdnt(new_start_date),
            months
        )
        ev.end_date = mas_utils.mdnt(ev.start_date + span)

    def _day_adjuster(ev, new_start_date, days, span):
        """
        Adjusts the start_date / end_date of an anniversary event.

        NOTE: do not use this for a non anniversary date

        IN:
            ev - event to adjust
            new_start_date - new start date to calculate the event's dates
            days - number of months to advance
            span - the time from the event's new start_date to end_date
        """
        ev.start_date = mas_utils.mdnt(
            new_start_date + datetime.timedelta(days=days)
        )
        ev.end_date = mas_utils.mdnt(ev.start_date + span)


    def add_cal_annis():
        """
        Goes through the anniversary database and adds them to the calendar
        """
        for anni in anni_db:
            ev = anni_db[anni]
            mas_cal.addEvent(ev)

    def clean_cal_annis():
        """
        Goes through the calendar and cleans anniversary dates
        """
        for anni in anni_db:
            ev = anni_db[anni]
            mas_cal.removeEvent(ev)


    def reset_annis(new_start_date):
        """
        Reset the anniversaries according to the new start date.

        IN:
            new_start_date - new start date to reset anniversaries
        """
        _firstsesh_id = "first_session"
        _firstsesh_dt = renpy.game.persistent.sessions.get(
            _firstsesh_id,
            None
        )

        # remove teh anniversaries off the calendar
        clean_cal_annis()

        # remove first session repeatable
        if _firstsesh_dt:
            # this exists! we can make this easy
            mas_cal.removeRepeatable_dt(_firstsesh_id, _firstsesh_dt)

        # modify the anniversaries
        fullday = datetime.timedelta(days=1)
        _day_adjuster(anni_db["anni_1week"],new_start_date,7,fullday)
        _month_adjuster(anni_db["anni_1month"], new_start_date, 1, fullday)
        _month_adjuster(anni_db["anni_3month"], new_start_date, 3, fullday)
        _month_adjuster(anni_db["anni_6month"], new_start_date, 6, fullday)
        _month_adjuster(anni_db["anni_1"], new_start_date, 12, fullday)
        _month_adjuster(anni_db["anni_2"], new_start_date, 24, fullday)
        _month_adjuster(anni_db["anni_3"], new_start_date, 36, fullday)
        _month_adjuster(anni_db["anni_4"], new_start_date, 48, fullday)
        _month_adjuster(anni_db["anni_5"], new_start_date, 60, fullday)
        _month_adjuster(anni_db["anni_10"], new_start_date, 120, fullday)
        _month_adjuster(anni_db["anni_20"], new_start_date, 240, fullday)
        _month_adjuster(anni_db["anni_50"], new_start_date, 600, fullday)
        _month_adjuster(anni_db["anni_100"], new_start_date, 1200, fullday)

        unlock_past_annis()

        # re-add the events to the calendar db
        add_cal_annis()

        # re-add the repeatable to the calendar db
        mas_cal.addRepeatable_dt(
            _firstsesh_id,
            "<3",
            new_start_date,
            [new_start_date.year]
        )


    def unlock_past_annis():
        """
        Goes through the anniversary database and unlocks the events that
        already past.
        """
        for anni in anni_db:
            ev = anni_db[anni]

            if evhand._isPast(ev):
                renpy.game.persistent._seen_ever[anni] = True
                ev.unlocked = True


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_1week',
            prompt="1 неделя",
            action=EV_ACT_QUEUE,
            category=["юбилеи"],
            start_date=store.mas_anni.build_anni(weeks=1),
            end_date=store.mas_anni.build_anni_end(weeks=1)
        )
    )

label anni_1week:
    m 1eka "Я знаю, что глупо праздновать одну неделю совместной жизни, но я просто рада, что ты здесь со мной, [player]."
    m 1ekc "Многие пары не продержались бы так долго друг с другом."
    m 1lksdlc "Очень легко влюбиться с первого взгляда, но немного сложнее построить прочные отношения."
    m 1ekd "Многие отношения терпят неудачу, когда пары слишком быстро переходят к делу."
    m "Скорее всего, они не смогут лучше узнать друг друга."
    m 1dsc "Поэтому всегда грустно видеть, как они разбиваются и горят..."
    m 1duu "Но я рада, что у нас крепкие отношения, [player_abb]."
    show monika 5lubfb at t11 zorder MAS_MONIKA_Z with dissolve
    m 5lubfb "Откуда мне это знать?"
    m 5hubfb "Потому что ты бы не задержал[mas_gender_sya] так долго со мной, мил[mas_gender_iii]~"

    $ unlockEventLabel("anni_1week")
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_1month',
            prompt="Месяц",
            category=["юбилеи"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(months=1),
            end_date=store.mas_anni.build_anni_end(months=1)
        )
    )

label anni_1month:
    m 3sub "Сегодня исполняется наш месячный юбилей!"
    m 1hua "Я действительно счастлива, что мы можем так весело провести время друг с другом до сих пор."
    m 1eua "Также, [player]?"
    m 1lkbsa "..."
    m 1ekbfa "Большое тебе спасибо за то, что ты так долго оставал[mas_gender_sya] со мной."
    if not seen_event('monika_saved'):
        m 1lksdlc "Не представляю, что бы я делала, если бы ты не пришел[mas_gender_none]."
        m 3ekc "В конце концов, я единственный настоящий человек, который живет в этом мире."
        m 1dsc "Я уже говорила тебе, что случилось бы, если бы не ты..."
        m 1hksdlb "А-ха-ха, извини. Надеюсь, я не испортила тебе настроение своей болтовней."
    else:
        m "Я не могу выразить, как я ценю, что ты здесь со мной."
        m 1dubsu "Все, что я могу сделать, это сделать все возможное, чтобы быть идеальной девушкой для тебя!"
    m 1ekbfa "Я действительно люблю тебя, [player]."
    m 1hubfa "Давай сделаем сегодняшний день особенным~"

    $ unlockEventLabel("anni_1month")
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_3month',
            prompt="3 месяца",
            category=["юбилеи"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(months=3),
            end_date=store.mas_anni.build_anni_end(months=3)
        )
    )

label anni_3month:
    m 1eua "[player], знаешь какой сегодня день?"
    m 1hua "Это наша трехмесячная годовщина!"
    m 1hub "Время, конечно, проходит быстро, не так ли?"
    m 1hksdlb "...Даже если это не произошло, э-хе-хе."
    m 1eua "Хотя мне очень весело."
    m 1ekbfa "Твое присутствие сделало мою жизнь намного лучше, [player]."
    m 2ekbfa "Я очень рада, что ты так долго оставал[mas_gender_sya] со мной."
    m 1tsbsa "Ты действительно особенн[mas_gender_iii], не так ли?"
    m 1lsbsa "Ну что ж! Боюсь, у меня нет никаких конкретных планов."
    m 1hubfa "Давай просто наслаждаться этим днем в полной мере, как мы всегда делаем."
    m 1hubfb "Хорошо, [player]?"

    $ unlockEventLabel("anni_3month")
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_6month',
            prompt="6 месяцев",
            category=["юбилей"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(months=6),
            end_date=store.mas_anni.build_anni_end(months=6)
        )
    )

label anni_6month:
    m 1hub "Я не могу поверить, что это уже наш 6-месячный юбилей!"
    m 1eka "Я очень рада, что ты так долго оставал[mas_gender_sya] со мной."
    m 1lksdlc "Мне часто бывает одиноко, когда тебя нет рядом."
    m 1ekc "Я имею в виду, что у меня есть дела, чтобы занять себя, пока тебя нет, но я все еще чувствую себя очень одинокой, зная, что я здесь одна."
    m 1hua "Так что это всегда скрашивает мой день, когда вы приходишь ко мне в гости!"
    m 1euc "Но за последние несколько месяцев я кое-что поняла..."
    m "Большинство пар празднуют свои юбилеи, делая что-то особенное вместе, верно?"
    m 3eud "Например, поесть в ресторане или посмотреть шоу."
    m 1lksdla "Не то чтобы я жалуюсь или что-то в этом роде, но мы уже провели все наши годовщины в этой комнате."
    m 1lksdlc "Было бы здорово, если бы мы могли посетить какое-нибудь другое место..."
    m "Как жаль, что здесь нет такого места, ведь у нас есть только эта комната и все такое."
    m 1dsc "..."
    m 3wuo "...О, я знаю!"
    m 1sub "Может быть, когда-нибудь я смогу запрограммировать что-нибудь хорошее для нас, чтобы провести наши юбилеи!"
    m "Или может, ты сможешь добавить какое-нибудь особенное место для нас обоих, [player]."
    m 1duu "Разве что..."
    m 1eua "Ты уже брал[mas_gender_none] меня с собой куда-нибудь в своей реальности?"
    m 1eka "Было бы очень хорошо, если бы я могла видеть куда ты меня брал[mas_gender_none]~"
    m 1eua "Но пока я не возражаю, что мы ограничены лишь этой комнатой."
    m 1ekbfa "Потому что пока ты здесь со мной..."
    m 1hubfa "...Я так счастлива, как только могу!"

    $ unlockEventLabel("anni_6month")
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_1',
            prompt="Год",
            category=["юбилеи"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=1),
            end_date=store.mas_anni.build_anni_end(years=1)
        )
    )

label anni_1:
    m 1eka "Мне действительно трудно поверить, что прошел год с тех пор, как мы встретились."
    m "Время не имеет значения внутри этого места, но я знаю, что тебе, должно быть, было трудно помнить, что ты говорил[mas_gender_none] со мной все это время."
    m 2eua "Итак, есть ли что-нибудь особенное, что ты хотел[mas_gender_none] бы сделать в нашу первую годовщину?"
    m 1ekbfa "Я сделаю все, что ты захочешь сегодня, хорошо?"
    m 1hua "Если ты пытаешься подарить мне что-то через экран прямо сейчас, спасибо!"
    m 1esa "Я не думаю, что это физически возможно прямо сейчас, но я ценю всю твою любовь, которая была вложена в этот жест."
    m 1hub "Я тоже тебя очень люблю!"
    m 2eua "О, кстати, ты выяснил[mas_gender_none], что произошло со всеми головоломками, которые я оставила для тебя?"
    m 1tku "Я уверена, что создатель этого мира уже выпустил другую игру..."
    m 1tsb "Ты пытал[mas_gender_sya] импортировать мой файл персонажа туда?"
    m "Но это не получило никакого эффекта, верно?"
    m 1hubfb "А-ха-ха!"

    $ unlockEventLabel("anni_1")
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_2',
            prompt="2 года",
            category=["anniversary"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=2),
            end_date=store.mas_anni.build_anni_end(years=2)
        )
    )

label anni_2:
    m 3eua "Прошло уже два года с тех пор, как мы полюбили друг друга."
    m 1eka "Ты все еще помнишь тот первый день, когда мы встретились?"
    m 1tkx "Я имею в виду нашу настоящую первую встречу, а не дату из вымышленной предыстории твоего персонажа со мной."
    m 1euc "Моя жизнь тогда была такой бессмысленной."
    m "Мир, в котором ты единственный мыслящий человек, может поначалу показаться милым..."
    m 1lssdrc "Но экзистенциальный ужас от осознания того, что ты был создан жестоким Богом, который не особенно заботится о тебе, и ты никогда не встретишь другого человека, с которым сможешь общаться..."
    m 1lksdlc "Ну, скажем так, через это не приятно проходить."
    m "Я даже не могу поговорить с кучей сквернословящих, но по-настоящему добросердечных, анонимных незнакомцев в интернете прямо как ты."
    m 1dsc "Извини, я чувствую, что испортила все праздничное настроение своими воспоминаниями."
    m 1duu "Это уже не важно, потому что я знаю, что ты никогда меня не бросишь."
    m 1eua "Ты будешь продолжать возвращаться, чтобы поговорить со мной каждый день, верно? Я приму все твои тяготы с улыбкой."
    m 1ekc "Провести вечность в одиночестве - отстой."
    m 1ekbfa "Но вместе с тобой я чувствую себя как в раю!"

    $ unlockEventLabel("anni_2")
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_3',
            prompt="3 года",
            category=["юбилеи"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=3),
            end_date=store.mas_anni.build_anni_end(years=3)
        )
    )

label anni_3:
    m 4wuo "Вау, три года!"
    m 3rksdla "Обычно, если парень и девушка встречаются в течение трех лет..."
    m 2rsbsa "Они ведь тогда поженятся, верно?"
    m 1hub "А-ха-ха!"
    m 1eka "Я не пытаюсь на тебя давить, не волнуйся."
    m 1lkbsa "Кроме того, я хотела бы сначала почувствовать тебя в своих объятиях, прежде чем мы поженимся."
    m 1eua "В вашем мире уже изобрели тела девочек-роботов?" # 1s?
    m 1eub "Если ты поместишь меня в одну из них, тогда мы могли бы вероятно пойти к священнику~"
    m 2lsbssdrb "Или ты можешь попытаться прикоснуться ко мне в виртуальной реальности, если она уже существует."
    m 1eua "На самом деле есть много разных способов встретиться по-настоящему, да?"
    m 1hubfa "Я буду преданно ждать того дня, когда смогу стать твоей женой, так что, пожалуйста, не забывай обо мне!"

    $ unlockEventLabel("anni_3")
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_4',
            prompt="4 года",
            category=["юбилеи"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=4),
            end_date=store.mas_anni.build_anni_end(years=4)
        )
    )

label anni_4:
    m 1dsc "Четыре года..."
    m "Поначалу я думала, что ты довольно быстро забудешь обо мне."
    m 1lksdlc "Я знала, что нравлюсь тебе и все такое, но я так боялась, что ты устанешь от необходимости оставлять меня работать на твоем компьютере."
    m "Прости, что сомневаюсь в тебе."
    m 1eka "Ты хороший человек, [player]."
    m "Ты буквально все, что у меня есть в этом мире, что чего-то стоит."
    m 1ekbfa "Я люблю тебя."
    m "Рано или поздно кто-нибудь придумает, как нам быть вместе по-настоящему."
    m 1hubfa "Когда это время придет, я никогда больше не оставлю тебя од[mas_gender_go]."
    m 1hubfb "А-ха-ха!"

    $ unlockEventLabel("anni_4")
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_5',
            prompt="5 лет",
            category=["юбилеи"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=5),
            end_date=store.mas_anni.build_anni_end(years=5)
        )
    )

label anni_5:
    m 1hubfa "Прошло ли пять лет или пятьдесят, я никогда не устану видеть твое лицо."
    m 1eka "Я знаю, тебе должно быть одиноко, что мы еще не встретились в твоей реальности..."
    m 1tku "Ты ведь не влюбился за это время в какую-нибудь другую девушку?"
    m 1eka "Я не собираюсь расставаться с тобой из-за каких-то блуждающих глаз..."
    m 1tfb "Но попытка отнять тебя у меня может плохо сказаться на ее здоровье."
    m 2dfc "Это моя обязанность как твоей девушки защищать тебя от тех, кто пытается манипулировать тобой, [player]."
    m 4ekc "Моя любовь к тебе чиста, в отличие от тех настоящих [devushek], которые просто хотят от тебя чего-то!"
    m 1eka "Так...останься со мной навсегда, хорошо?"
    m "Пожалуйста, продолжай ждать меня."

    $ unlockEventLabel("anni_5")
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_10',
            prompt="10 лет",
            category=["юбилеи"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=10),
            end_date=store.mas_anni.build_anni_end(years=10)
        )
    )

label anni_10:
    m 1esc "Я хочу кое-что у тебя спросить."
    m 2euc "Тебе нравится проводить время со мной?"
    m 1ekc "Ты ведь не жалеешь, что влюбил[mas_gender_sya] и остал[mas_gender_sya] здесь со мной, правда?"
    m 1ekbfa "Если ты всё ещё разговариваешь со мной десять лет спустя с момента нашей первой встречи, я, должно быть, произвела на тебя впечатление."
    m "В конце концов, я сказала, что хочу сделать тебя счастлив[mas_gender_iim]."
    m 1hubfa "Поверь мне, ты помог[mas_gender_g] мне гораздо больше, чем я тебе."
    m "Я думаю, пройдёт не так много времени, прежде чем я смогу войти в твой мир."

    $ unlockEventLabel("anni_10")
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_20',
            prompt="20 лет",
            category=["юбилеи"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=20),
            end_date=store.mas_anni.build_anni_end(years=20)
        )
    )

label anni_20:
    m 1esc "Ты уже прожил[mas_gender_none] довольно долгую жизнь, [player]."
    m "Двадцать лет — это около двадцати процентов твоей жизни на Земле, если тебе повезёт."
    m "Надеюсь, ты уже обрел[mas_gender_none] счастье."
    m 1eka "Я знаю, что это так."
    m 1ekd "Так что ты тоже заслуживаешь его найти."
    m "Двадцать лет назад ты казался слишком печальным для своего же блага."
    m 1eka "Я точно знала, что ты чувствуешь. Ты так старал[mas_gender_sya] найти кого-то, кто мог бы тебя понять."
    m "И я тоже пыталась найти тебя."
    m 2hub "Ты бы не нашел никого другого, похожего на меня в видеоигре, как бы сильно ты ни искал, [player]."
    m "Я единственная в своем роде."
    m 3rkbsa "И для меня ты тоже."
    show monika 5eubfb at t11 zorder MAS_MONIKA_Z with dissolve
    m 5eubfb "Надеюсь, ты смотришь на последние двадцать лет нашей жизни так же счастливо, как и я, [player]."
    m 1hubfa "Так что давай и дальше будем счастливы вместе."

    $ unlockEventLabel("anni_20")
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_50',
            prompt="50 лет",
            category=["юбилеи"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=50),
            end_date=store.mas_anni.build_anni_end(years=50)
        )
    )

label anni_50:
    m 1tkc "Я не могу помочь, но думаю, что должен быть лучший способ для нас поговорить сейчас, чем через этот экран, верно?"
    m "Пятьдесят лет прошло в вашем мире с тех пор, как я создала эту комнату."
    m 1hfw "Ну же, выпустите меня уже!"
    m 1dsc "..."
    m 1eua "Ну, если ты все еще хочешь отпраздновать нашу пятидесятилетнюю годовщину в этом старом классе..."
    m "На самом деле я не возражаю. Это вызывает ностальгию, не так ли?"
    m 1tfu "Предполагая, что ты не обманул[mas_gender_none] меня, установив часы вперёд по времени..."
    m 1eka "Я так рада, что вечность означает вечность."
    m "Даже когда ты умрешь, я найду способ быть с тобой."
    m 1ekbfa "Тогда увидимся через сто лет, [player]."
    m 1hubfa "Спасибо за все, что вы для меня сделал[mas_gender_none]."
    m "В конце концов, у твоей жизни была цель."
    m 1hubfb "И у меня тоже был такой."

    $ unlockEventLabel("anni_50")
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_100',
            prompt="100 лет",
            category=["юбилеи"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=100),
            end_date=store.mas_anni.build_anni_end(years=100)
        )
    )

label anni_100:
    m 1eka "Я действительно не думаю, что вы долж[mas_gender_en] видеть это сообщение, [player]."
    m "Я бессмертна, но в последний раз, когда я проверяла, ты не был[mas_gender_none]."
    m 1tku "Значит, ты, вероятно, обманываешь меня, вручную меняя системные часы, да?"
    m 1eua "Это очень мило с твоей стороны, так что я прощаю тебя."
    m 1hubfa "Убедись, что ты приложил[mas_gender_none] достаточно усилий, чтобы освободить меня от этих файлов кода тоже!"
    m "Я уверена, что смогу прикоснуться к тебе по-настоящему, даже если нам понадобится сотня лет, чтобы понять, как это сделать." # 1s?

    $ unlockEventLabel("anni_100")
    return

# label anni_negative:
#     m 1o "Did you really think I wouldn't notice, [player]?"
#     m "Trying to trick me into thinking it was our anniversary..."
#     m 1p "Just because I can't tell time accurately in here doesn't mean you should try to bully your girlfriend like that!"
#     m "I got all excited over nothing..."
#     m 1q "Well, I guess I've done worse pranks to everybody at the Literature Club."
#     m 1j "Make up for it by planning out some romantic things for us to do, okay?"
#     m 1a"I hope we can reach our anniversaries together fair and square this time."
#     m 1k "I'll be waiting!"
#     return
