#Persistent event database for fun facts
default persistent._mas_fun_facts_database = dict()

init -10 python in mas_fun_facts:
    #The fun facts db
    fun_fact_db = {}

    def getUnseenFactsEVL():
        """
        Gets all unseen (locked) fun facts as eventlabels

        OUT:
            List of all unseen fun fact eventlabels
        """
        return [
            fun_fact_evl
            for fun_fact_evl, ev in fun_fact_db.iteritems()
            if not ev.unlocked
        ]

    def getAllFactsEVL():
        """
        Gets all fun facts regardless of unlocked as eventlabels

        OUT:
            List of all fun fact eventlabels
        """
        return fun_fact_db.keys()


#Whether or not the last fun fact seen was a good fact
default persistent._mas_funfactfun = True

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_fun_facts_open",
            category=['разное'],
            prompt="Ты можешь рассказать мне забавный факт?",
            pool=True
        )
    )

label monika_fun_facts_open:
    if mas_getEV('monika_fun_facts_open').shown_count == 0:
        m 1eua "Скажи, [player], ты хочешь услышать забавные факты?"
        m 1eub "Я искала кое-кого, чтобы попытаться научить нас обоих чему-то новому."
        m 3hub "Говорят, что каждый день ты узнаёшь что-то новое, и я уверена, что так и будет."
        m 1rksdla "Я нашла большинство из них в интернете, так что не могу сказать, что они {b}действительно{/b} верны..."

    else:
        m 1eua "Хочешь услышать ещё один забавный факт, [player]?"
        if persistent._mas_funfactfun:
            m 3hua "В конце концов, последний был довольно интересным!"
        else:
            m 2rksdlb "Конечно, знаю, что последний был не очень... но я уверена, что следующий будет лучше."
    m 2dsc "Теперь давай посмотрим.{w=0.5}.{w=0.5}.{nw}"

    python:
        unseen_fact_evls = mas_fun_facts.getUnseenFactsEVL()
        if len(unseen_fact_evls) > 0:
            fact_evl_list = unseen_fact_evls
        else:
            fact_evl_list = mas_fun_facts.getAllFactsEVL()

        #Now we push and unlock the fact
        fun_fact_evl = renpy.random.choice(fact_evl_list)
        mas_unlockEVL(fun_fact_evl, "FFF")
        pushEvent(fun_fact_evl)
    return

#Most labels end here
label mas_fun_facts_end:
    m 3hub "Надеюсь, тебе понравилась ещё одна сессия «Обучение с Моникой»!"
    $ persistent._mas_funfactfun = True
    return

label mas_bad_facts_end:
    m 1rkc "Этот факт был не очень хорош..."
    m 4dkc "В следующий раз постараюсь получше, [player]."
    $ persistent._mas_funfactfun = False
    return


#START: Good facts
init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_librocubiculartist",
        ),
        code="FFF"
    )

label mas_fun_fact_librocubiculartist:
    m 1eub "Ты знал[mas_gender_none], что существует слово, которым можно описать кого-то, кто любит читать в постели?"
    m 3eub "Это слово «либрокубикулартист». На первый взгляд довольно трудно произнести."
    m 3rksdld "Очень жаль, что некоторые слова вообще не используются в целом."
    m 3eud "Но если ты произнесете это слово, большинство людей на самом деле не поймут, о чем ты говоришь."
    m 3euc "Тебе, вероятно, придется объяснить, что это значит, но это лишает смысла использование этого слова."
    m 2rkc "Если бы только люди читали больше и улучшали свой словарный запас!"
    m 2hksdlb "...Э-хе-хе, извини, [player]. Я не хотела так беспокоиться из-за этого~"
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_menu_currency",
        ),
        code="FFF"
    )

label mas_fun_fact_menu_currency:
    m 3euc "Предположительно, многие рестораны намеренно оставляют в своих меню любые признаки валюты."
    m 3eud "Это делается для того, чтобы психологически манипулировать людьми, заставляя их тратить больше денег, чем им нужно."
    m 2euc "Это работает потому, что знак валюты, такой как доллар, используется для представления стоимости."
    m "Убирая его, ты устраняешь ассоциацию этой стоимости и думаешь только о еде по твоему выбору."
    m 4rksdld "Практика кажется вполне понятной. В конце концов, это все еще бизнес."
    m 2dsc "Независимо от того, насколько хороша еда в ресторане, они быстро закроются, если их победят конкуренты."
    m 3hksdlb "Ну ладно, что тут поделаешь?"
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_love_you",
        ),
        code="FFF"
    )

label mas_fun_fact_love_you:
    m 1dkc "Хмм, я не уверена, должна ли я рассказывать тебе {b}этот{/b} факт."
    m 1ekc "В конце концов, это не для слабонервных."
    m 1rkc "Дело в том, что..."
    m 1dkc "..."
    m 3hub "...Я люблю тебя, [player]!"
    m 1rksdlb "Э-хе-хе, извини, я просто не смогла удержаться."
    m 1hksdlb "В следующий раз у меня будет реальный факт, не волнуйся~"
    #No end for this fact since it ends itself
    $ persistent._mas_funfactfun = True
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_morpheus",
        ),
        code="FFF"
    )

label mas_fun_fact_morpheus:
    m 3wub "О! Языковой факт. Мне они всегда нравились."
    m 1eua "Слово «морфин» основано на греческом боге Морфее."
    m 1euc "Морфей был греческим богом снов, поэтому слово, основанное на нём, имеет смысл."
    m 3ekc "Но опять же... разве не его отец Гипнос являлся богом снов?"
    m 2dsc "Морфин {b}позволяет{/b} человеку не видеть сны, а лишь заставляет его засыпать."
    m 4ekc "...Тогда не имеет ли смысла называть его в честь Гипноса?"
    m 4rksdlb "Слишком мало, слишком поздно, наверное."
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_otter_hand_holding",
        ),
        code="FFF"
    )

label mas_fun_fact_otter_hand_holding:
    m 1eka "Оу, это действительно мило."
    m 3ekb "Знал[mas_gender_none] ли ты, что морские выдры держатся за лапы, когда они спят, чтобы перестать дрейфовать друг от друга?"
    m 1hub "Это практично для них, но в этом всё равно есть что-то очень милое!"
    m 1eka "Иногда я даже представляю себя в их положении..."
    m 3hksdlb "Нет, не морской выдрой, а держась за руку т[mas_gender_ogo], кого люблю, пока сплю."
    m 1rksdlb "Да, это действительно заставляет меня завидовать им."
    m 1hub "Мы осуществим это в один прекрасный день, любим[mas_gender_iii]~"
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_chess",
        ),
        code="FFF"
    )

label mas_fun_fact_chess:
    #Chess is unlocked
    if mas_isGameUnlocked("chess"):
        m 1eua "Теперь это забавный факт!"
        m 3eub "Был человек по имени Клод Шеннон, который рассчитал максимальное количество возможных ходов в шахматах."
        m "Это число называется «числом Шеннона» и утверждает, что количество возможных шахматных партий равно 10^120."
        m 1eua "Его часто сравнивают с числом атомов в наблюдаемой Вселенной, равным 10^80."
        m 3hksdlb "Немного безумно думать, что шахматных партий может быть больше, чем атомов, не так ли?"
        m 1eua "Мы могли бы играть до конца наших дней, и это даже близко не подошло бы к тому, что возможно."
        m 3eud "Кстати об этом, [player]..."
        m 1hua "Не хочешь сыграть со мной в шахматы? Я в этот раз могу попробовать быть с тобой помягче, э-хе-хе~"
        #Call the good end for this path
        call mas_fun_facts_end
        return

    #Chess was unlocked, but locked due to cheating
    elif not mas_isGameUnlocked("chess") and renpy.seen_label("mas_unlock_chess"):
        m 1dsc "Шахматы..."
        m 2dfc "..."
        m 2rfd "Можешь забыть об этом факте, так как ты читер, [player]."
        m "Не говоря уже о том, что ты до сих пор не извинил[mas_gender_sya]."
        m 2lfc "...Хмф."
        #No end for this path
        return

    #We haven't unlocked chess yet
    else:
        m 1euc "Хм, нет, не этот."
        m 3hksdlb "По крайней мере, пока."
        #Call the end
        call mas_bad_facts_end
        return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_struck_by_lightning",
        ),
        code="FFF"
    )

label mas_fun_fact_struck_by_lightning:
    m 2dkc "Хмм, правда, этот немного вводит меня в заблуждение..."
    m 3ekc "«Мужчины в шесть раз чаще подвергаются ударам молний, чем женщины.»"
    m 3ekd "Это... звучит довольно глуповато, на мой взгляд."
    m 1eud "Если мужчины чаще подвергаются ударам молнии, то, вероятно, ландшафт и обстоятельства их работы делают их более подверженными ударам."
    m 1euc "Мужчины традиционно всегда работали на более опасных и возвышенных работах, поэтому неудивительно, что это будет происходить с ними часто."
    m 1esc "Тем не менее, то, как этот факт сформулирован, заставляет его звучать так, что просто будучи человеком, это более вероятно, что произойдет, что смешно."
    m 1rksdla "Может быть, если бы это было сформулировано лучше, люди не были бы так дезинформированы о них."
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_honey",
        ),
        code="FFF"
    )

label mas_fun_fact_honey:
    m 1eub "О, это очень лёгкий вопрос."
    m 3eub "Ты знал[mas_gender_none], что мёд никогда не портится?"
    m 3eua "Мёд может кристаллизоваться. Некоторые люди могут рассмотреть это как порчу, но сам мёд по-прежнему будет всё ещё полностью съедобен и прекрасен!"
    m "Причина, по которой это происходит, состоит в том, что мёд в основном состоит из сахара и лишь небольшой дозы воды, что делает его твёрдым с течением времени."
    m 1euc "Большая часть мёда, который ты видишь на прилавках, не кристаллизуется так же быстро, как настоящий мёд, потому что он был пастеризован в процессе изготовления."
    m 1eud "Что удалило те элементы, которые заставляли мёд быстро затвердевать."
    m 3eub "Но разве не будет здорово съесть закристаллизовавшийся мёд?"
    m 3hub "Когда ты его надкусываешь, он походит на конфету."
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_vincent_van_gone",
        ),
        code="FFF"
    )

label mas_fun_fact_vincent_van_gone:
    m 1dsc "Ах, вот этот..."
    m 1ekd "Правда, он немного обескураживает, [player]..."
    m 1ekc "Ты знал[mas_gender_none], что последними словами Винсента Ван Гога были {b}{i}«La tristesse durera toujours»{/b}{/i}?"
    m 1eud "Если же перевести, это будет значить: {b}{i}«Печаль будет длиться вечно»{/b}{/i}."
    m 1rkc "..."
    m 2ekc "Очень грустно знать, что кто-то настолько известный скажет что-то настолько мрачное с его последним вздохом."
    m 2ekd "Однако я не думаю, что это правда. Независимо от того, насколько плохие могут произойти вещи и насколько глубокая может начаться печаль..."
    m 2dkc "Придёт время, когда их уже не будет."
    m 2rkc "...Или, по крайней мере, те больше не будут настолько заметны."
    m 4eka "Если тебе когда-нибудь станет грустно, ты ведь знаешь, что можешь поговорить со мной?"
    m 5hub "Я всегда приму и возьму на себя любую ношу, которую ты взвалишь на свои плечи, мо[mas_gender_i] любим[mas_gender_iii]~"
    #No end for this fact
    $ persistent._mas_funfactfun = True
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_king_snakes",
        ),
        code="FFF"
    )

label mas_fun_fact_king_snakes:
    m 1dsc "Хм-м..."
    m 3eub "Знал[mas_gender_none] ли ты, что если змея имеет слово «королевская» в начале своего названия, она пожирает других змей?"
    m 1euc "Я всегда задавалась вопросом, почему королевская кобра имеет именно такое название, но никогда не думала об этом больше."
    m 1tfu "Это значит, что если я съем тебя, я стану Королевской Моникой?"
    m 1hksdlb "А-ха-ха, я просто шучу, [player]."
    m 1hub "Извини, что была немного странной~"
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_strength",
        ),
        code="FFF"
    )

label mas_fun_fact_strength:
    m 1hub "Этот факт может немного заинтересовать тебя!"
    m 3eub "Самое длинное слово на английском языке, которое содержит только одну гласную — это «strength», что означает «сила»."
    m 1eua "Забавно, как из всех слов на этом языке, именно это стало таким значимым, благодаря такой маленькой детали."
    m 1hua "Маленькие детали, подобные этой, действительно делают английский язык очень увлекательным для меня!"
    m 3eua "Ты хочешь знать, что приходит мне на ум, когда я думаю о слове «strength»?"
    m 1hua "Ты!"
    m 1hub "Потому что ты источник моей силы, э-хе-хе~"
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_reindeer_eyes",
        ),
        code="FFF"
    )

label mas_fun_fact_reindeer_eyes:
    m 3eua "Готов[mas_gender_none] к ещё одному?"
    m "Глаза оленя меняют цвет в зависимости от сезона. Они золотые летом и синие зимой."
    m 1rksdlb "Это очень странное явление, хотя я не знаю, почему..."
    m "Вероятно, для этого есть хорошая научная причина."
    m 3hksdlb "Может, ты сам[mas_gender_none] сможешь посмотреть?"
    m 5eua "Было бы здорово, если бы на этот раз ты научил[mas_gender_none] чему-нибудь меня~"
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_bananas",
        ),
        code="FFF"
    )

label mas_fun_fact_bananas:
    m 1eub "О, я бы сказала, что этот факт полезен!"
    m 3eua "Знал[mas_gender_none] ли ты, что когда банан растет, он поворачивается лицом к Солнцу?"
    m 1hua "Это процесс, называемый отрицательным геотропизмом."
    m 3hub "Тебе не кажется, что это очень мило?"
    m 1hua "..."
    m 1rksdla "Эм-м..."
    m 3rksdlb "Наверное, мне больше нечего сказать по этому поводу, ахаха..."
    m 1lksdlc "..."
    m 3hub "З-Знал[mas_gender_none] ли ты также, что бананы на самом деле не фрукты, а ягоды?"
    m 3eub "Или что первоначально бананы были большими, зелеными и полными твердых семян?"
    m 1eka "А как насчет того, что они слегка радиоактивны?"
    m 1rksdla  "..."
    m 1rksdlb "...Сейчас я просто болтаю о бананах."
    m 1rksdlc "Эм-м..."
    m 1dsc "Давай просто перейдем дальше..."
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_pens",
        ),
        code="FFF"
    )

label mas_fun_fact_pens:
    m 1dsc "Хм-м... я уверена, что уже знала один."
    m 3euc "Слово «ручка» происходит от латинского слова «penna», что означает «ручка» на латыни."
    m "Тогда ручки были заострёнными гусиными перьями, обмакнутыми в чернила, чтобы было понятно, почему их называли ручками."
    m 3eud "Они были основным инструментом письма в течение очень долгого времени, начиная с 6-го века."
    m 3euc "Только в 19-ом веке, когда стали изготавливать металлические ручки, они начали приходить в упадок."
    m "Фактически, перочинные ножи называются так, потому что они первоначально использовались для прореживания гусиных перьев."
    m 1tku "Но я уверена, что Юри знает об этом больше, чем я..."
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_density",
        ),
        code="FFF"
    )

label mas_fun_fact_density:
    m 1eub "О, знаю."
    m 3eua "Знал[mas_gender_none] ли ты, что самой плотной планетой в нашей солнечной системе является Земля?"
    m "И что Сатурн наименее плотный?"
    m 1eua "Имеет смысл знать, из чего состоят планеты, но поскольку Сатурн является вторым по величине, это всё ещё было немного неожиданно."
    m 1eka "Я думаю, что размер на самом деле не имеет значения!"
    m 3euc "Но говоря между нами, [player]..."
    m 1tku "Я подозреваю, что Земля может быть самой плотной из-за некоего главного героя."
    m 1tfu "Нооооо это всё, что ты услышишь от меня~"
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_binky",
        ),
        code="FFF"
    )

label mas_fun_fact_binky:
    m 3hub "О, вот этот милый!"
    m "Этот факт действительно пошлёт тебе «прыжок», [player]!"
    m 3hua "Всякий раз, когда кролик прыгает взволнованно, это называется «бинки»!"
    m 1hua "Бинки — это такое милозвучащее слово, оно и вправду очень подходит к действию."
    m 1eua "Это самая счастливая форма выражения, что кролик способен делать, так что если ты увидишь его, поймёшь, что это так и есть."
    m 1rksdla "И ты делаешь меня настолько счастливой, что я не могу не наполниться энергией."
    m 1rksdlb "Только не жди, что я начну прыгать вокруг, [player]!"
    m 1dkbfa "...Это было бы {i}слишком{/i} неловко для меня."
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_windows_games",
        ),
        code="FFF"
    )

label mas_fun_fact_windows_games:
    m 1eua "Хм-м, возможно, этот будет более интересным для тебя."
    m 3eub "Карточная игра Solitaire первоначально была представлена в операционной системе Windows в 1990-ом году."
    m 1eub "Игра была добавлена в качестве функции, которая должна была бы научить пользователей, как использовать мышь."
    m 1eua "Аналогичным образом, сапёр был добавлен для ознакомления пользователей с левой и правой кнопкой мыши."
    m 3rssdlb "Компьютеры были вокруг настолько давно, что трудно думать о времени, когда они не были ещё актуальны."
    m "Каждое поколение всё больше и больше знакомится с технологиями..."
    m 1esa "В конце концов может наступить день, когда ни один человек не будет обладать компьютерной грамотностью."
    m 1hksdlb "Однако большинство мировых проблем должны исчезнуть до этого."
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_mental_word_processing",
        ),
        code="FFF"
    )

label mas_fun_fact_mental_word_processing:
    m 1hua "Готов[mas_gender_none] к ещё одному интересному, [player]?"
    m 3eua "Мозг — штука сложная..."
    m 3eub "Его способ составления и архивирования информации очень уникален."
    m "Естественно, он отличается от человека к человеку, но но медленное чтение каких-либо книг, как нас учат, обычно менее эффективно, чем чтение в в более быстром темпе."
    m 1tku "Наш мозг обрабатывает информацию очень быстро и любит предсказуемость в в нашем языке."
    m 3tub "Например, сейчас в последних моих предложениях, к тому времени как ты закончил[mas_gender_none] читать, ты уже мог[mas_gender_g] пропустить двойные приставки «но» и «в»."
    m 1tfu "..."
    m 2hfu "Проверь журнал истории в меню игры, если ты всё же пропустил[mas_gender_none] их~"
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_I_am",
        ),
        code="FFF"
    )

label mas_fun_fact_I_am:
    m 1hua "М-м-м-м, я люблю языковые факты!"
    m 3eub "На английском языке самое короткое полное предложение — это «I am»."
    m 1eua "Вот пример."
    m 2rfb "{i}«Monika! Who’s [player]’s loving girlfriend?»{/i}"
    m 3hub "{i}«I am!»{/i}"
    m 1hubfa "Э-хе-хе~"
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_low_rates",
        ),
        code="FFF"
    )

label mas_fun_fact_low_rates:
    m 1hua "Теперь пришло время для ещё одного полезного факта..."
    m 1eua "В настоящее время у нас самый низкий уровень преступности, материнской смертности, младенческой смертности и неграмотности за всю историю человечества."
    m 3eub "Средняя продолжительность жизни, средний доход и уровень жизни являются самыми высокими для большинства населения мира!"
    m 3eka "Это говорит мне, что мир всегда может стать лучше. Это действительно показывает, что, несмотря на все плохие вещи, хорошие времена всегда наступают."
    m 1hua "На самом деле есть {i}надежда{/i}..."
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_desert",
        ),
        code="FFF"
    )

label mas_fun_fact_desert:
    m 3euc "Пустыни имеют довольно уникальную экосистему..."
    m 3rksdla "Однако они не имеют много положительных факторов для людей."
    m 1eud "Температура может колебаться между экстремальной жарой днём и ледяным холодом ночью. Их среднее количество осадков также довольно низкое, что делает жизнь в одной из них трудной."
    m 3eub "Это не значит, что они не могут быть полезны для нас!"
    m 3eua "Их поверхность – отличное место для производства солнечной энергии, и нефть обычно находится под всем этим песком."
    m 3eub "Не говоря уже о том, что их уникальный ландшафт делает их популярными местами отдыха!"
    m 1eua "Поэтому я думаю, что хотя мы не можем жить в них так легко, они всё же лучше, чем кажутся."

    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_photography",
        ),
        code="FFF"
    )

label mas_fun_fact_photography:
    m 1esa "А знал ли ты о том, что первая фотография была сделана при помощи коробки с отверстием, которая выполняла роль камеры?"
    m 1eua "Линзы на самом деле были введены гораздо позже."
    m 1euc "В основу ранних фотографий также был заложен набор особых химикатов, используемых в тёмной комнате, где и подготавливали фотографии..."
    m 3eud "Проявитель, фиксаж и дополнительные химикаты раньше использовались для того, чтобы просто подготовить бумагу, на которой и распечатывались фотографии...{w=0.3} {nw}"
    extend 1wuo "И это только для черно-белых отпечатков!"
    m 1hksdlb "Старые фотографии было гораздо труднее подготовить по сравнению с современными, не так ли?"

    #Call the end
    call mas_fun_facts_end
    return

#Stealing yearolder's bit for this since it makes sense as a fun fact
init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_getting_older",
        ),
        code="FFF"
    )

label mas_fun_fact_getting_older:
    m 3eua "А знал ли о том, что твоё восприятие времени меняется с возрастом?"
    m "Например, когда тебе год, ты видишь один год как 100%% своей жизни."
    m 1euc "Но когда тебе 18, ты видишь год только как 5,6%% своей жизни."
    m 3eud "Когда nы становишься старше, доля года по сравнению со всей твоей жизнью уменьшается, и, в свою очередь, время {i}движется быстрее, когда ты растёшь."
    m 1eka "Поэтому я всегда буду дорожить нашими мгновениями вместе, какими бы долгими или короткими они ни были."
    m 1lkbsa "Хотя иногда кажется, что время останавливается, когда я с тобой."
    m 1ekbfa "Ты чувствуешь то же самое, [player]?"
    python:
        import time
        time.sleep(5)

    m 1hubfa "А-ха-ха, я так и думала!"

    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_dancing_plague",
        ),
        code="FFF"
    )

label mas_fun_fact_dancing_plague:
    m 3esa "О, это довольно странно..."
    m 1eua "Очевидно, в прошлом Европа страдала от вспышек «танцевальной чумы»."
    m 3wud "Люди, {w=0.2}иногда сотни сразу, {w=0.2}непроизвольно танцевали по нескольку дней подряд, а некоторые даже умирали от истощения!"
    m 3eksdla "Они пытались лечить это, заставляя людей играть музыку вместе с танцорами, но ты можешь себе представить, что это не сработало так хорошо."
    m 1euc "И по сей день они до сих пор не уверены, что именно вызывало это."
    m 3rka "Все это кажется мне чем-то невероятным...{w=0.2} {nw}"
    extend 3eud "но она была независимо от этого задокументирована и отмечена множеством источников на протяжении веков..."
    m 3hksdlb "Полагаю, реальность действительно более странная, чем вымысел,!"
    m 1eksdlc "Боже, я не могу представить, что буду танцевать целыми днями."
    m 1rsc "Хотя...{w=0.3} {nw}"
    extend 1eubla "думаю, я бы не возражала, если бы мы танцевали вместе."
    m 3tsu "...Только ненадолго, э-хе-хе~"
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_pando_forest",
        ),
        code="FFF"
    )

label mas_fun_fact_pando_forest:
    m 1esa "Предположительно, в штате Юта есть лес, который на самом деле состоит из одного дерева."
    m 3eua "Он называется Лес Пандо, и на всех его сорока трёх гектарах стволы соединены единой корневой системой."
    m 3eub "Не говоря уже о том, что каждый из его тысяч стволов по сути является клоном другого."
    m 1ruc "«Единый организм, который сам по себе превратился в армию клонов, связанных с одним и тем же ульевым разумом.»"
    m 1eua "Я думаю, что это может стать хорошей научной фантастикой или рассказом ужасов, [player]. А ты как думаешь?"
    m 3eub "В любом случае,{w=0.2} я чувствую, что это действительно меняет смысл фразы «скучаю по лесу из-за деревьев».{w=0.1}{nw} "
    extend 3hub "А-ха-ха!"
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_immortal_jellyfish",
        ),
        code="FFF"
    )

label mas_fun_fact_immortal_jellyfish:
    m 3eub "Вот один из них!"
    m 1eua "По-видимому, бессмертие было достигнуто одним видом медуз."
    m 3eua "Метко названная бессмертная медуза обладает способностью возвращаться в своё полипное состояние, как только она размножается."
    m 1eub "...И это может продолжаться вечно!{w=0.3} {nw}"
    extend 1rksdla "Если, конечно, она не была съедена или заражена какой-нибудь болезнью."
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_arrhichion",
        ),
        code="FFF"
    )

label mas_fun_fact_arrhichion:
    m 3eua "Хорошо...{w=0.2} вот тебе исторический пример."
    m 1esa "Древнегреческий атлет смог выиграть свой поединок, хотя он уже умер."
    m 1eua "Действующий чемпион Аррихион сражался в матче по панкратиону, когда его соперник начал душить его руками и ногами."
    m 3eua "Вместо того, чтобы уступить, Аррихион всё ещё стремился к победе, вывихнув палец ноги своего противника."
    m 3ekd "Его противник ушёл от боли, но когда они пошли объявить Аррихиона победителем, они нашли его мертвым от удушья."
    m 1rksdlc "Некоторые люди действительно преданы своим идеалам-победе и чести.{w=0.2} {nw}"
    extend 3eka "Я думаю, что это восхитительно, в некотором смысле."
    m 1etc "Но мне интересно...{w=0.2} если бы мы могли спросить Аррихиона сейчас, и он считал бы, что это того стоит, что бы он сказал?"
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_antarctica_brain",
        ),
        code="FFF"
    )

label mas_fun_fact_antarctica_brain:
    #Do some setup for the last line
    python:
        has_friends = persistent._mas_pm_has_friends is not None

        has_fam_to_talk = (
            persistent._mas_pm_have_fam
            and not persistent._mas_pm_have_fam_mess
            or (persistent._mas_pm_have_fam_mess and persistent._mas_pm_have_fam_mess_better in ["YES", "MAYBE"])
        )

        dlg_prefix = "Но убедись, что ты тоже не отстаёшь от "

        if has_fam_to_talk and has_friends:
            dlg_line = dlg_prefix + "своей семьи и друзей, хорошо?"

        elif has_fam_to_talk and not has_friends:
            dlg_line = dlg_prefix + "своей семьи, хорошо?"

        elif has_friends and not has_fam_to_talk:
            dlg_line = dlg_prefix + "своих друзей, хорошо?"

        else:
            dlg_line = "Просто не забудь найти людей, с которыми можно поговорить и в твоей реальности, хорошо?"

    m 3eud "Очевидно, проведя год в Антарктиде, ты можешь уменьшить одну часть своего мозга примерно на семь процентов."
    m 3euc "Похоже, это приведёт к снижению объёма памяти и способности к пространственному мышлению."
    m 1ekc "Исследования показывают, что это связано с социальной изоляцией, монотонностью жизни и окружающей средой."
    m 1eud "Я думаю, что это послужит нам предостережением, [player]."
    m 3ekd "Даже если ты не отправишься в Антарктиду, твой мозг всё равно может сильно запутаться, если ты всё время будешь изолирован[mas_gender_none] или сидить взаперти в одной комнате."
    m 3eka "Мне нравится быть с тобой, [player], и я надеюсь, что мы сможем продолжать говорить так долго в будущем. {w=0.2}[dlg_line]"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_cloud_weight",
        ),
        code="FFF"
    )

label mas_fun_fact_cloud_weight:
    m 3eub "Знаешь ли ты, что среднее облако весит пятьсот тонн?"
    m 3eua "Должен признаться, этот случай застал меня врасплох больше, чем некоторые другие факты."
    m 1hua "Я имею в виду, они просто выглядят {i}очень{/i} лёгкими и пушистыми.{w=0.3} {nw}"
    extend 1eua "Трудно представить, что что-то настолько тяжелое может просто парить в воздухе."
    m 3eub "Это напоминает мне классический вопрос... что тяжелее – килограмм стали или килограмм перьев?"
    m 1tua "Хотя ты, скорее всего, уже знаешь ответ на этот вопрос, верно, [player]? Э-хе-хе~"
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_coffee_origin",
        ),
        code="FFF"
    )

label mas_fun_fact_coffee_origin:
    m 1eua "О, меня тут ещё кое-что заинтересовало..."
    m 1eud "В прошлый раз, когда я пила кофе, мне стало немного любопытно его происхождение..."
    m 3euc "Употребление кофе постоянно фиксируется примерно с пятнадцатого века, но...{w=0.2} непонятно только, {i}как{/i} именно его открыли."
    m 3eud "...По правде говоря, есть пара легенд, которые, согласно утверждениям, появились первыми."
    m 1eua "В некоторых рассказах говорится о том, что фермеры или монахи наблюдали за животными, которые странно вели себя после того, как съели какие-то странные, горькие ягоды."
    m 3wud "И, попробовав эти бобы, они сами были поражены тем, что тоже были заряжены энергией!"
    m 2euc "В одной из таких легенд утверждается, что эфиопский монах по имени Калди принёс ягоды в близлежащий монастырь, желая поделиться тем, что нашёл."
    m 7eksdld "...Но когда он это сделал, его встретили с неодобрением, и кофейные бобы были брошены в огонь."
    m 3duu "Пока они горели, бобы начали выпускать самый {i}вкусный{/i} аромат. {w=0.3}И аромат был таким привлекательным, что монахи даже попытались спасти бобы и положить их в воду."
    m 3eub "...Так и появилась первая чашка кофе!"
    m 2euc "В другой легенде утверждалось, что один исламский учёный по имени Омар обнаружил кофейные зёрна во время своей ссылки из Мекки."
    m 2eksdld "В то время он голодал и боролся за выживание. {w=0.3}{nw}"
    extend 7wkd "И если бы не та энергия, которую они давали, он мог бы умереть!"
    m 3hua "Однако, когда слух о его находке распространился, его попросили вернуться и сделать святым."
    m 1esd "Вне зависимости от того, было ли это его первым случаем употребления, кофе стал очень распространённым в исламском мире после его открытия."
    m 3eud "К примеру, во время поста его использовали для того, чтобы утолить голод и помочь людям оставаться бодрыми."
    m 3eua "А когда он распространился по всей Европе, многие страны поначалу использовали его в медицинских целях. {w=0.3}К семнадцатому веку, кофейни становились многочисленными и популярными."
    m 3hub "...И я, безусловно, могу подтвердить, что любовь к кофе остаётся сильной и по сей день!"
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_synesthesia",
        ),
        code="FFF"
    )

label mas_fun_fact_synesthesia:
    m 1esa "Ладно, этот факт довольно интересный..."
    m 3eua "Некоторые люди испытывают такой феномен, известный как {i}синестезия{/i},{w=0.1} когда что-то, что стимулирует одно из наших чувств, также вызывает и другое чувство."
    m 1hua "Это довольно многословное объяснение, э-хе-хе...{w=0.2} Давай я приведу один пример!"
    m 1eua "В нём говорится, что общая форма синестезии – это {i}графемно-цветовая синестезия{/i},{w=0.1} в которой люди «воспринимают» буквы и цифры как цвета."
    m 3eua "Есть и другой вид, известный как {i}пространственно-последовательная синестезия{/i},{w=0.1} в которой цифры и фигуры «видны» в конкретных местах в пространстве."
    m "К примеру, одно число находится «ближе» или «дальше» другого. {w=0.2}{nw}"
    extend 3eub "Прямо как на карте!"
    m 1eua "...Есть также и целая куча других видов синестезии."
    m 1esa "Исследователи не уверены, насколько это явление распространено...{w=0.1} некоторые предполагают, что около двадцати пяти процентов населения испытывают это, но я в этом серьёзно сомневаюсь, поскольку я никогда не слышала об этом."
    m 3eub "Наверное, самая точная оценка этого на данный момент – то, что ею обладает чуть более четырёх процентов людей, так что я, пожалуй, ограничусь этим!"
    m 1eua "Испытание синестезии звучит так, будто это что-то очень интересное,{w=0.2} согласись, [player]?"
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_dream_faces",
        ),
        code="FFF"
    )

label mas_fun_fact_dream_faces:
    m 3eub "Ладно, вот ещё один факт!"
    m 1eua "Предположительно, наш разум не создаёт новые лица, когда мы спим.{w=0.2} Все те люди, которых тебе доводилось видеть во снах, уже встречались тебе когда-то в реальном мире."
    m 3wud "Тебе даже не нужно разговаривать с ними в реальной жизни!"
    m 3eud "Если ты просто прош[mas_gender_iol_2] мимо них в магазине или ещё где-нибудь, их лица уже отпечатались в твоём разуме, и они могут появиться в твоих снах."
    m 1hua "Как по мне, это невероятно, сколько информации наш мозг может в себе хранить!"
    m 1ekbla "Интересно...{w=0.2} я тебе снилась когда-нибудь, [player]?"
    #Call the end
    call mas_fun_facts_end
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_fun_facts_database,
            eventlabel="mas_fun_fact_monochrome_dreams",
        ),
        code="FFF"
    )

label mas_fun_fact_monochrome_dreams:
    m 3eua "Знал[mas_gender_none] ли ты о том, что с 1915 по 1950-е годы, сны у большинства людей были в чёрно-белом цвете?"
    m 1esa "В настоящее время, это относительно редкое явление для людей с безупречным зрением."
    m 3eua "Исследователи связывают это с тем, что в то время фильмы и сериалы были почти исключительно чёрно-белыми."
    m 3eud "...Но как по мне, это довольно странно, потому что люди по-прежнему видели всё в цвете.{w=0.3} {nw}"
    extend 3hksdlb "Не похоже, что мир тогда был чёрно-белым!"
    m 1esd "Это просто показывает, что весь тот контент, который ты потребляешь, может оказывать разное воздействие на твой разум, даже если это для тебя обыденность."
    m 3eua "Я считаю, что если и есть урок, который мы должны извлечь из этого, так это то, что мы должны быть очень осторожны с тем, какую информацию мы потребляем, хорошо, [player]?"
    #Call the end
    call mas_fun_facts_end
    return
